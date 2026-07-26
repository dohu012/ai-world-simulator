"""Deterministic construction of isolated agent Observations."""

from collections.abc import Mapping, Sequence

from app.domain.common import EntityReference
from app.domain.enums import FactVisibility, ObservationType
from app.domain.observation import (
    FeltChange,
    HeardStatement,
    ObservedEntity,
    ReceivedMessage,
)
from app.domain.schemas import (
    Character,
    Observation,
    OracleRequest,
    OracleResponse,
    WorldEvent,
)


class ObservationBuilder:
    """Apply explicit visibility/channel rules before agent input exists."""

    def build_for_events(
        self,
        events: Sequence[WorldEvent],
        characters: Sequence[Character],
        *,
        additional_recipients: Mapping[str, Sequence[str]] | None = None,
        observation_id_overrides: Mapping[tuple[str, str], str] | None = None,
    ) -> list[Observation]:
        character_ids = sorted(character.id for character in characters)
        known_ids = set(character_ids)
        additions = additional_recipients or {}
        overrides = observation_id_overrides or {}
        observations: list[Observation] = []

        for event in sorted(events, key=lambda item: (item.occurred_at, item.id)):
            recipients = self._event_recipients(event, character_ids, additions.get(event.id, ()))
            for agent_id in recipients:
                if agent_id not in known_ids:
                    continue
                is_indirect = agent_id not in event.participant_ids or (
                    event.event_type.value == "movement"
                    and agent_id != event.metadata.get("actor_id")
                )
                observation_type = (
                    ObservationType.AUDITORY if is_indirect else ObservationType.MIXED
                )
                visible_entities: list[ObservedEntity] = []
                heard_statements: list[HeardStatement] = []
                if is_indirect:
                    heard_statements = [HeardStatement(speaker_id=None, content=event.description)]
                elif event.location_id is not None:
                    visible_entities = [
                        ObservedEntity(
                            entity=EntityReference(
                                entity_type="location",
                                entity_id=event.location_id,
                            ),
                            name=event.location_id,
                            description=event.description,
                            attributes={"event_type": event.event_type.value},
                        )
                    ]
                observations.append(
                    Observation(
                        id=overrides.get(
                            (event.id, agent_id),
                            f"obs-{event.id.removeprefix('event-')}-{agent_id.removeprefix('char-')}",
                        ),
                        world_id=event.world_id,
                        agent_id=agent_id,
                        observed_at=event.occurred_at,
                        observation_type=observation_type,
                        source_event_id=event.id,
                        source_message_id=None,
                        visible_entities=visible_entities,
                        heard_statements=heard_statements,
                        received_messages=[],
                        felt_changes=[],
                        available_actions=[],
                        metadata={
                            "builder": "deterministic-v1",
                            "source_visibility": event.visibility.value,
                            "delivery": "indirect" if is_indirect else "participant",
                        },
                        schema_version=event.schema_version,
                    )
                )
        return observations

    def build_for_oracle(self, request: OracleRequest, response: OracleResponse) -> Observation:
        """Turn player advice into allowed local input, never a command."""
        if request.id != response.request_id or request.agent_id != response.agent_id:
            raise ValueError("Oracle response does not match its request")
        return Observation(
            id=f"obs-{response.id}",
            world_id=response.world_id,
            agent_id=response.agent_id,
            observed_at=response.responded_at,
            observation_type=ObservationType.ORACLE,
            source_event_id=None,
            source_message_id=response.id,
            visible_entities=[],
            heard_statements=[],
            received_messages=[
                ReceivedMessage(
                    message_id=response.id,
                    sender_id=None,
                    sent_at=response.responded_at,
                    content=response.content,
                )
            ],
            felt_changes=[
                FeltChange(
                    description="Player advice arrived as information, not a command.",
                    intensity=response.clarity,
                )
            ],
            available_actions=[],
            metadata={
                "builder": "deterministic-v1",
                "oracle_request_id": request.id,
                "oracle_response_id": response.id,
                "advice_only": True,
            },
            schema_version=response.schema_version,
        )

    @staticmethod
    def _event_recipients(
        event: WorldEvent,
        all_character_ids: Sequence[str],
        additional_recipients: Sequence[str],
    ) -> list[str]:
        if event.visibility == FactVisibility.PUBLIC:
            return list(all_character_ids)
        recipients = set(event.participant_ids)
        if event.visibility == FactVisibility.RESTRICTED:
            recipients.update(additional_recipients)
        return sorted(recipients)
