import type {
  AgentBelief,
  Character,
  Observation,
  WorldEvent,
} from "@/types/domain";

export function getCharacterById(characters: Character[], id: string) {
  return characters.find((character) => character.id === id);
}

export function getObservationsForAgent(
  observations: Observation[],
  agentId: string,
) {
  return observations.filter((observation) => observation.agent_id === agentId);
}

export function getBeliefsForAgent(beliefs: AgentBelief[], agentId: string) {
  return beliefs.filter((belief) => belief.agent_id === agentId);
}

export function formatWorldTime(value: string) {
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(new Date(value));
}

export function visibilityLabel(event: WorldEvent) {
  const labels: Record<WorldEvent["visibility"], string> = {
    public: "公开",
    restricted: "受限",
    secret: "秘密",
    private: "私人",
  };
  return labels[event.visibility];
}

export function confidencePercent(belief: AgentBelief) {
  return `${Math.round(belief.confidence * 100)}%`;
}
