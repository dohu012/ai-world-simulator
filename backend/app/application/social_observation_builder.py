"""Task 18 extension of the unique Observation Builder boundary."""

from datetime import datetime

from app.application.observation_builder import ObservationBuilder
from app.domain.enums import ObservationType
from app.domain.observation import ReceivedMessage
from app.domain.schemas import Observation


class SocialObservationBuilder(ObservationBuilder):
    def build_for_message(
        self,
        *,
        observation_id: str,
        world_id: str,
        recipient_id: str,
        message_id: str,
        sender_id: str | None,
        body: str,
        sent_at: datetime,
        delivered_at: datetime,
        channel_kind: str,
    ) -> Observation:
        """Create recipient-only input without hidden fact or route identifiers."""
        return Observation(
            id=observation_id,
            world_id=world_id,
            agent_id=recipient_id,
            observed_at=delivered_at,
            observation_type=ObservationType.MESSAGE,
            source_event_id=None,
            source_message_id=message_id,
            visible_entities=[],
            heard_statements=[],
            received_messages=[
                ReceivedMessage(
                    message_id=message_id,
                    sender_id=sender_id,
                    sent_at=sent_at,
                    content=body,
                )
            ],
            felt_changes=[],
            available_actions=[],
            # A recipient can tell an official bulletin from a courier's word, so
            # `channel_kind` is perceivable. The channel's numeric reliability is the
            # world's own truth about how trustworthy that route is; the agent must
            # infer trust from content and history instead of reading it off input.
            metadata={
                "builder": "deterministic-v2",
                "delivery": "message",
                "channel_kind": channel_kind,
            },
            schema_version="1.0",
        )
