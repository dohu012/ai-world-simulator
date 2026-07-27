"use client";
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { decideGrayHarborOnce } from "./demo-agent-api";
import { ApiClientError } from "@/lib/api-client";

export function AgentDecisionPanel() {
  const [key, setKey] = useState(() => `manual-${Date.now()}`);
  const decision = useMutation({ mutationFn: () => decideGrayHarborOnce(key) });
  const data = decision.data;
  const failure =
    decision.error instanceof ApiClientError
      ? decision.error.code
      : decision.error instanceof Error
        ? decision.error.message
        : null;
  return (
    <section
      aria-label="Agent Decision"
      className="rounded-lg border border-cyan-800 bg-slate-900/80 p-5"
    >
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-cyan-300">
        Agent Decision · Chen only
      </p>
      <h2 className="mt-1 text-lg font-semibold text-white">
        Observation-only decide once
      </h2>
      <p className="mt-2 text-sm text-slate-400">
        The model may propose one offered wait/move. The World Engine alone
        decides the outcome.
      </p>
      <button
        className="mt-4 rounded border border-cyan-500 px-4 py-2 text-sm text-cyan-100 disabled:opacity-50"
        disabled={decision.isPending}
        onClick={() => decision.mutate()}
      >
        {decision.isPending ? "Deciding…" : "Decide once"}
      </button>
      {failure ? (
        <p role="alert" className="mt-3 text-sm text-red-300">
          {failure}
        </p>
      ) : null}
      {data ? (
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          <article className="rounded border border-sky-800 bg-sky-950/30 p-4">
            <h3 className="font-semibold text-sky-100">Model proposal</h3>
            <p className="mt-2 text-sm text-slate-300">
              {data.proposal
                ? `${data.proposal.action} · ${data.proposal.rationale_summary}`
                : data.failure_code}
            </p>
            <p className="mt-2 text-xs text-slate-400">
              {data.prompt_version} · {data.attempts.length} attempt(s)
              {data.idempotent_replay ? " · replay" : ""}
            </p>
            {data.attempts.map((attempt) => (
              <p
                key={attempt.attempt_number}
                className="mt-1 text-xs text-slate-400"
              >
                {attempt.provider}/{attempt.model} · {attempt.latency_ms}ms ·
                tokens {attempt.input_tokens ?? "?"}/
                {attempt.output_tokens ?? "?"} · cost{" "}
                {attempt.cost_usd ?? "not calculated"}
              </p>
            ))}
          </article>
          <article className="rounded border border-emerald-800 bg-emerald-950/30 p-4">
            <h3 className="font-semibold text-emerald-100">
              Authoritative engine outcome
            </h3>
            <p className="mt-2 text-sm text-slate-300">
              {data.action
                ? `${data.action.result.status}${data.action.result.failure_code ? ` · ${data.action.result.failure_code}` : ""}`
                : "No action or world mutation."}
            </p>
            <p className="mt-2 text-xs text-slate-400">
              Watermark {data.observation_watermark.slice(0, 12)}… ·{" "}
              {data.observation_ids.length} observations
            </p>
          </article>
        </div>
      ) : null}
      <button
        className="mt-3 text-xs text-slate-500"
        onClick={() => setKey(`manual-${Date.now()}`)}
      >
        Use a new idempotency key
      </button>
    </section>
  );
}
