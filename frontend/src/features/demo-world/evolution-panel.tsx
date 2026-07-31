"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { demoCurrentAgentId } from "@/features/demo-world/demo-agent-api";
import { apiGet, apiPost } from "@/lib/api-client";
import type { EvolutionStateResponse, ReflectionResponse } from "@/types/api";

const headers = { "X-Demo-Agent-Id": demoCurrentAgentId };

export function EvolutionPanel() {
  const queryClient = useQueryClient();
  const state = useQuery({
    queryKey: ["agent-evolution", demoCurrentAgentId],
    queryFn: () =>
      apiGet<EvolutionStateResponse>("/demo/worlds/gray-harbor/me/evolution", {
        headers,
      }),
  });
  const reflection = useMutation({
    mutationFn: () =>
      apiPost<ReflectionResponse>(
        "/demo/worlds/gray-harbor/me/reflections",
        {},
        { headers },
      ),
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: ["agent-evolution", demoCurrentAgentId],
      }),
  });
  const data =
    state.data?.baseline &&
    state.data.identity &&
    Array.isArray(state.data.relationships) &&
    Array.isArray(state.data.changes)
      ? state.data
      : undefined;

  return (
    <section
      aria-label="Identity and relationships"
      className="rounded-lg border border-cyan-800 bg-slate-950 p-5"
      data-testid="evolution-panel"
    >
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-cyan-300">
            Auditable evolution / Chen Mo
          </p>
          <h2 className="mt-1 text-xl font-semibold text-white">
            Baseline, learned stance, and directional relationships
          </h2>
          <p className="mt-1 text-sm text-slate-400">
            Structured fictional state is bounded evidence interpretation—not a
            diagnosis or objective truth.
          </p>
        </div>
        <button
          className="border border-cyan-500 px-3 py-2 text-sm text-cyan-100 disabled:opacity-40"
          disabled={reflection.isPending}
          onClick={() => reflection.mutate()}
          type="button"
        >
          {reflection.isPending ? "Reflecting..." : "Run bounded reflection"}
        </button>
      </div>

      {state.isLoading ? (
        <p className="mt-4 text-sm text-slate-400">
          Loading identity history...
        </p>
      ) : null}
      {state.isError ? (
        <p className="mt-4 text-sm text-red-300" role="alert">
          Identity and relationship history is unavailable.
        </p>
      ) : null}
      {data ? (
        <>
          <div className="mt-5 grid gap-4 lg:grid-cols-2">
            <article className="border border-slate-800 p-4">
              <h3 className="text-sm font-semibold text-slate-100">
                Immutable baseline · generation {data.baseline.generation}
              </h3>
              <p className="mt-2 text-sm text-slate-300">
                {data.baseline.persona_summary}
              </p>
            </article>
            <article className="border border-slate-800 p-4">
              <h3 className="text-sm font-semibold text-slate-100">
                Current derived identity · version {data.identity.version}
              </h3>
              <p className="mt-2 text-sm text-slate-300">
                {data.identity.persona_summary}
              </p>
              <dl className="mt-3 flex flex-wrap gap-3 text-xs">
                {Object.entries(data.identity.offsets).map(
                  ([dimension, value]) => (
                    <div key={dimension}>
                      <dt className="text-slate-500">{dimension}</dt>
                      <dd className="font-mono text-cyan-200">
                        {value > 0 ? "+" : ""}
                        {value.toFixed(2)}
                      </dd>
                    </div>
                  ),
                )}
              </dl>
            </article>
          </div>
          <h3 className="mt-5 text-sm font-semibold text-slate-100">
            Directional relationships (Chen → target)
          </h3>
          <ul className="mt-2 grid gap-3 lg:grid-cols-2">
            {data.relationships.map((relationship) => (
              <li
                className="border-l-2 border-cyan-600 pl-3"
                key={relationship.id}
              >
                <p className="text-sm text-slate-200">
                  {relationship.target_type} · {relationship.target_id} ·
                  version {relationship.version}
                </p>
                <p className="mt-1 text-xs text-slate-400">
                  {relationship.interpretation}
                </p>
                <p className="mt-1 font-mono text-xs text-cyan-200">
                  {Object.entries(relationship.dimensions)
                    .map(([key, value]) => `${key} ${value.toFixed(2)}`)
                    .join(" · ") || "unknown / no durable conclusion"}
                </p>
              </li>
            ))}
          </ul>
          <h3 className="mt-5 text-sm font-semibold text-slate-100">
            Why this changed
          </h3>
          {data.changes.length === 0 ? (
            <p className="mt-2 text-sm text-slate-400">
              No supported durable change has been committed.
            </p>
          ) : (
            <ol className="mt-2 space-y-3">
              {data.changes.map((change) => (
                <li
                  className="border-l-2 border-slate-700 pl-3"
                  key={change.id}
                >
                  <p className="text-sm text-slate-200">
                    {change.dimension} ·{" "}
                    <span
                      className={
                        change.accepted ? "text-emerald-300" : "text-amber-300"
                      }
                    >
                      {change.accepted
                        ? "accepted"
                        : change.reason.toLowerCase()}
                    </span>
                  </p>
                  <p className="text-xs text-slate-400">{change.rationale}</p>
                  <p className="mt-1 text-xs text-slate-500">
                    Evidence: {change.evidence_memory_ids.join(", ")}
                  </p>
                </li>
              ))}
            </ol>
          )}
        </>
      ) : null}
    </section>
  );
}
