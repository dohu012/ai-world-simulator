"use client";

import { useQuery } from "@tanstack/react-query";

import { getGrayHarborCurrentAgentInput } from "@/features/demo-world/demo-agent-api";
import { formatWorldTime } from "./demo-world-types";

function observationSummary(observation: {
  metadata: Record<string, unknown>;
  received_messages: Array<{ content: string }>;
}) {
  if (typeof observation.metadata.perspective_note === "string") {
    return observation.metadata.perspective_note;
  }
  const message = observation.received_messages[0];
  if (message) {
    return message.content;
  }
  return "No summary available.";
}

export function DemoAgentInputFeed() {
  const { data, error, isError, isPending } = useQuery({
    queryKey: ["demo-world", "gray-harbor", "current-agent-input"],
    queryFn: getGrayHarborCurrentAgentInput,
  });

  if (isPending) {
    return (
      <section
        className="rounded-lg border border-slate-700 bg-slate-900/80 p-5 text-sm text-slate-300"
        aria-label="Agent Input Feed loading"
      >
        Loading agent input feed...
      </section>
    );
  }

  if (isError || !data) {
    return (
      <section
        className="rounded-lg border border-red-800 bg-red-950/30 p-5 text-sm text-red-100"
        aria-label="Agent Input Feed error"
      >
        Agent input feed failed:{" "}
        {error instanceof Error ? error.message : "Unknown error"}
      </section>
    );
  }

  return (
    <section
      className="rounded-lg border border-sky-800/80 bg-slate-900/80 p-5"
      aria-label="Agent Input Feed"
    >
      <div className="flex flex-col gap-3 border-b border-slate-700 pb-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-sky-300">
            Agent Input Feed
          </p>
          <h2 className="mt-1 text-lg font-semibold text-slate-50">
            {data.character.name}
          </h2>
        </div>
        <p className="text-sm text-slate-300">
          {formatWorldTime(data.world.current_time)} - Observation-only
        </p>
      </div>

      <ol className="mt-5 space-y-3">
        {data.observations.map((observation) => (
          <li
            key={observation.id}
            className="rounded-md border border-slate-700 bg-slate-950/60 p-4"
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="font-semibold text-slate-50">{observation.id}</h3>
              <span className="rounded border border-slate-600 px-2 py-0.5 text-xs text-slate-300">
                {observation.observation_type}
              </span>
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-300">
              {observationSummary(observation)}
            </p>
          </li>
        ))}
      </ol>
    </section>
  );
}
