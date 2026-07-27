"use client";

import { useQuery } from "@tanstack/react-query";

import { formatWorldTime, visibilityLabel } from "./demo-world-types";
import { apiGet } from "@/lib/api-client";
import type { ReplayChain, WorldReplayResponse } from "@/types/api";

function compactId(value: string | null) {
  if (!value) return "none";
  return value.length > 28
    ? `${value.slice(0, 14)}鈥?{value.slice(-10)}`
    : value;
}

function chainLabel(chain: ReplayChain) {
  return [
    `${chain.decision_ids?.length ?? 0} decision`,
    `${chain.oracle_request_ids.length} request`,
    `${chain.oracle_response_ids.length} response`,
    `${chain.action_intent_ids.length} intent`,
    `${chain.action_result_ids.length} result`,
    `${chain.event_ids.length} event`,
  ].join(" · ");
}

export function ReplayInspector() {
  const { data, error, isError, isPending } = useQuery({
    queryKey: ["demo-world", "gray-harbor", "replay"],
    queryFn: () =>
      apiGet<WorldReplayResponse>("/demo/worlds/gray-harbor/replay"),
  });

  if (isPending) {
    return (
      <section
        aria-label="Replay Inspector loading"
        className="rounded-lg border border-violet-800/80 bg-slate-900/80 p-5 text-sm text-slate-300"
      >
        Loading replay inspector...
      </section>
    );
  }

  if (isError || !data) {
    return (
      <section
        aria-label="Replay Inspector error"
        className="rounded-lg border border-red-800 bg-red-950/30 p-5 text-sm text-red-100"
      >
        Replay inspector failed:{" "}
        {error instanceof Error ? error.message : "Unknown error"}
      </section>
    );
  }

  const events = [...data.events].sort(
    (left, right) =>
      left.occurred_at.localeCompare(right.occurred_at) ||
      left.id.localeCompare(right.id),
  );

  return (
    <section
      aria-label="Replay Inspector"
      className="rounded-lg border border-violet-800/80 bg-slate-900/80 p-5"
    >
      <div className="border-b border-slate-700 pb-4">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-violet-300">
          Replay Inspector 路 Observer/debug only
        </p>
        <h2 className="mt-1 text-lg font-semibold text-slate-50">
          Objective order and causal links
        </h2>
        <p className="mt-2 text-sm text-slate-400">
          Read-only audit projection; this does not rebuild or play the world.
        </p>
      </div>

      {events.length === 0 ? (
        <p className="mt-4 text-sm text-slate-400">No replay events.</p>
      ) : (
        <ol className="mt-5 space-y-3">
          {events.map((event, index) => {
            const observations = data.observations.filter(
              (observation) => observation.source_event_id === event.id,
            );
            const chain = data.chains.find((candidate) =>
              candidate.event_ids.includes(event.id),
            );
            const result = data.action_results.find((candidate) =>
              candidate.generated_event_ids.includes(event.id),
            );
            return (
              <li
                key={event.id}
                className="rounded-md border border-slate-700 bg-slate-950/60 p-4"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-xs text-violet-300">
                    #{String(index + 1).padStart(2, "0")}
                  </span>
                  <time className="text-xs text-slate-400">
                    {formatWorldTime(event.occurred_at)}
                  </time>
                  <span className="rounded border border-slate-600 px-2 py-0.5 text-xs text-slate-300">
                    {visibilityLabel(event)}
                  </span>
                  <strong className="text-sm text-slate-50">
                    {event.title}
                  </strong>
                </div>
                <dl className="mt-3 grid gap-2 text-xs text-slate-300 md:grid-cols-3">
                  <div>
                    <dt className="text-slate-500">source_action_id</dt>
                    <dd
                      className="font-mono"
                      title={event.source_action_id ?? "none"}
                    >
                      {compactId(event.source_action_id)}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-slate-500">correlation_id</dt>
                    <dd className="font-mono" title={event.correlation_id}>
                      {compactId(event.correlation_id)}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-slate-500">observations</dt>
                    <dd>{observations.length} linked</dd>
                  </div>
                </dl>
                <p className="mt-3 text-xs text-slate-400">
                  {chain ? `Chain: ${chainLabel(chain)}` : "No causal chain"}
                </p>{" "}
                {result ? (
                  <div className="mt-3 text-xs text-slate-300">
                    <p>
                      Result: {result.status}
                      {result.failure_code ? ` · ${result.failure_code}` : ""}
                      {` · ${result.witness_character_ids.length} recipient(s)`}
                    </p>
                    {result.state_changes.map((change) => (
                      <p
                        key={`${change.entity_type}-${change.entity_id}-${change.field}`}
                      >
                        {change.entity_type}.{change.field}:{" "}
                        {String(change.old_value)} → {String(change.new_value)}
                      </p>
                    ))}
                  </div>
                ) : null}
              </li>
            );
          })}
        </ol>
      )}

      {data.chains.length > 0 ? (
        <div className="mt-5 border-t border-slate-700 pt-4">
          <h3 className="text-sm font-semibold text-slate-100">
            Oracle 鈫?response 鈫?intent 鈫?result 鈫?event
          </h3>
          <ul className="mt-3 space-y-2">
            {data.chains.map((chain) => (
              <li
                key={chain.correlation_id}
                className="font-mono text-xs text-slate-300"
              >
                <span title={chain.correlation_id}>
                  {compactId(chain.correlation_id)}
                </span>
                {" · "}
                {chainLabel(chain)}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </section>
  );
}
