"use client";

import { useQuery } from "@tanstack/react-query";

import {
  demoCurrentAgentId,
  getGrayHarborCurrentAgentPerspective,
} from "@/features/demo-world/demo-agent-api";
import { confidencePercent, formatWorldTime } from "./demo-world-types";

export function DemoAgentPreview() {
  const { data, error, isError, isPending } = useQuery({
    queryKey: ["demo-world", "gray-harbor", "current-agent-perspective"],
    queryFn: getGrayHarborCurrentAgentPerspective,
  });

  if (isPending) {
    return (
      <section
        className="rounded-lg border border-slate-700 bg-slate-900/80 p-5 text-sm text-slate-300"
        aria-label="Agent Preview loading"
      >
        Loading current-agent perspective...
      </section>
    );
  }

  if (isError || !data) {
    return (
      <section
        className="rounded-lg border border-red-800 bg-red-950/30 p-5 text-sm text-red-100"
        aria-label="Agent Preview error"
      >
        Current-agent perspective failed:{" "}
        {error instanceof Error ? error.message : "Unknown error"}
      </section>
    );
  }

  const observation = data.observations[0];
  const belief = data.beliefs[0];
  const oracleRequest = data.oracleRequests[0];
  const oracleResponse = data.oracleResponses[0];
  const actionIntent = data.actionIntents[0];
  const actionResult = data.actionResults[0];

  return (
    <section
      className="rounded-lg border border-emerald-800/80 bg-slate-900/80 p-5"
      aria-label="Agent Preview"
    >
      <div className="flex flex-col gap-3 border-b border-slate-700 pb-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-emerald-300">
            Agent Preview
          </p>
          <h2 className="mt-1 text-lg font-semibold text-slate-50">
            {data.character.name}
          </h2>
        </div>
        <dl className="grid gap-3 text-sm sm:grid-cols-2">
          <div className="border-l-2 border-emerald-400 pl-3">
            <dt className="text-slate-400">Caller</dt>
            <dd className="font-medium text-slate-100">{demoCurrentAgentId}</dd>
          </div>
          <div className="border-l-2 border-sky-400 pl-3">
            <dt className="text-slate-400">World Time</dt>
            <dd className="font-medium text-slate-100">
              {formatWorldTime(data.world.current_time)}
            </dd>
          </div>
        </dl>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <article className="rounded-md border border-slate-700 bg-slate-950/60 p-4">
          <h3 className="font-semibold text-slate-50">Observation</h3>
          <p className="mt-2 text-sm leading-6 text-slate-300">
            {observation
              ? String(observation.metadata.perspective_note)
              : "No current observation."}
          </p>
        </article>

        <article className="rounded-md border border-slate-700 bg-slate-950/60 p-4">
          <h3 className="font-semibold text-slate-50">Belief</h3>
          {belief ? (
            <>
              <p className="mt-2 text-sm leading-6 text-slate-300">
                {belief.subject} {belief.predicate}
              </p>
              <p className="mt-2 text-xs text-amber-200">
                Confidence {confidencePercent(belief)}
              </p>
            </>
          ) : (
            <p className="mt-2 text-sm text-slate-300">No current belief.</p>
          )}
        </article>

        <article className="rounded-md border border-amber-800 bg-amber-950/30 p-4">
          <h3 className="font-semibold text-amber-50">Oracle</h3>
          {oracleRequest && oracleResponse ? (
            <>
              <p className="mt-2 text-sm leading-6 text-amber-50">
                {oracleRequest.question}
              </p>
              <p className="mt-2 text-sm leading-6 text-amber-100">
                {oracleResponse.content}
              </p>
            </>
          ) : (
            <p className="mt-2 text-sm text-amber-100">No Oracle request.</p>
          )}
        </article>

        <article className="rounded-md border border-sky-800 bg-sky-950/40 p-4">
          <h3 className="font-semibold text-slate-50">Action</h3>
          <p className="mt-2 text-sm leading-6 text-slate-300">
            {actionIntent?.reason_summary ?? "No action intent."}
          </p>
          <p className="mt-2 text-xs text-slate-400">
            Result {actionResult?.status ?? "none"}
          </p>
        </article>
      </div>
    </section>
  );
}
