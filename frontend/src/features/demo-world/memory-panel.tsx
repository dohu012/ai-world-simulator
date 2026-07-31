"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { demoCurrentAgentId } from "@/features/demo-world/demo-agent-api";
import { apiGet, apiPost } from "@/lib/api-client";
import type {
  MemoryEvaluationResponse,
  MemoryResponse,
  MemoryRetrievalResponse,
  MemorySyncResponse,
} from "@/types/api";

const headers = { "X-Demo-Agent-Id": demoCurrentAgentId };

export function MemoryPanel() {
  const client = useQueryClient();
  const memories = useQuery({
    queryKey: ["agent-memories", demoCurrentAgentId],
    queryFn: () =>
      apiGet<MemoryResponse[]>("/demo/worlds/gray-harbor/me/memories", {
        headers,
      }),
  });
  const sync = useMutation({
    mutationFn: () =>
      apiPost<MemorySyncResponse>("/demo/worlds/gray-harbor/memory/sync", {}),
    onSuccess: () =>
      client.invalidateQueries({
        queryKey: ["agent-memories", demoCurrentAgentId],
      }),
  });
  const evaluation = useQuery({
    queryKey: ["memory-evaluation"],
    queryFn: () =>
      apiGet<MemoryEvaluationResponse>(
        "/demo/worlds/gray-harbor/memory/evaluation",
      ),
  });
  const retrieval = useQuery({
    queryKey: ["latest-memory-retrieval", demoCurrentAgentId],
    queryFn: () =>
      apiGet<MemoryRetrievalResponse | null>(
        "/demo/worlds/gray-harbor/me/memory-retrieval/latest",
        { headers },
      ),
  });
  const items = Array.isArray(memories.data) ? memories.data : [];
  const evaluationData =
    evaluation.data?.hybrid?.metrics &&
    typeof evaluation.data.hybrid.metrics.hard_gates_passed === "boolean"
      ? evaluation.data
      : undefined;

  return (
    <section
      aria-label="Long-term memory"
      className="rounded-lg border border-violet-700/70 bg-slate-950 p-5"
    >
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-violet-300">
            Auditable memory / Chen Mo
          </p>
          <h2 className="mt-1 text-xl font-semibold text-white">
            Subjective long-term context
          </h2>
          <p className="mt-1 text-sm text-slate-400">
            Memories are evidence, not objective world facts.
          </p>
        </div>
        <button
          className="border border-violet-500 px-3 py-2 text-sm text-violet-100 disabled:opacity-40"
          disabled={sync.isPending}
          onClick={() => sync.mutate()}
          type="button"
        >
          {sync.isPending ? "Projecting..." : "Project important experiences"}
        </button>
      </div>
      {memories.isLoading ? (
        <p className="mt-4 text-sm text-slate-400">Loading owner memory...</p>
      ) : null}
      {memories.isError ? (
        <p className="mt-4 text-sm text-red-300" role="alert">
          Owner memory is unavailable.
        </p>
      ) : null}
      {!memories.isLoading && !memories.isError && items.length === 0 ? (
        <p className="mt-4 text-sm text-slate-400">
          No important experience has been admitted yet.
        </p>
      ) : null}
      <ol className="mt-4 grid gap-3 lg:grid-cols-2">
        {items.map((memory) => (
          <li className="border-l-2 border-violet-500 pl-3" key={memory.id}>
            <div className="flex flex-wrap gap-2 text-xs uppercase text-slate-400">
              <span>{memory.memory_type.replace("_", " ")}</span>
              <span>importance {memory.importance.toFixed(2)}</span>
              <span>confidence {memory.confidence.toFixed(2)}</span>
              <span>{memory.embedding_status}</span>
            </div>
            <p className="mt-1 text-sm text-slate-200">{memory.summary}</p>
            <p className="mt-1 text-xs text-slate-500">
              {new Date(memory.occurred_at).toLocaleString()} /{" "}
              {memory.source_count} immutable source
              {memory.source_count === 1 ? "" : "s"}
            </p>
          </li>
        ))}
      </ol>
      {evaluationData ? (
        <div className="mt-5 border-t border-slate-700 pt-4">
          <div className="flex flex-wrap gap-x-5 gap-y-1 text-sm">
            <strong
              className={
                evaluationData.hybrid.metrics.hard_gates_passed
                  ? "text-emerald-300"
                  : "text-red-300"
              }
            >
              Hard gates{" "}
              {evaluationData.hybrid.metrics.hard_gates_passed
                ? "pass"
                : "fail"}
            </strong>
            <span className="text-slate-400">
              hybrid recall@k{" "}
              {evaluationData.hybrid.metrics.required_recall_at_k.toFixed(2)}
            </span>
            <span className="text-slate-400">
              forbidden exposure{" "}
              {evaluationData.hybrid.metrics.forbidden_exposure_count}
            </span>
            <span className="text-slate-400">
              fallback recall@k{" "}
              {evaluationData.fallback.metrics.required_recall_at_k.toFixed(2)}
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500">
            {evaluationData.corpus_version} / deterministic offline fixture
          </p>
        </div>
      ) : null}
      {retrieval.data?.candidates ? (
        <div className="mt-5 border-t border-slate-700 pt-4">
          <div className="flex flex-wrap justify-between gap-2">
            <h3 className="text-sm font-semibold text-slate-100">
              Latest decision context
            </h3>
            <p className="text-xs text-slate-500">
              {retrieval.data.mode} / {retrieval.data.characters_used} of{" "}
              {retrieval.data.character_budget} characters
            </p>
          </div>
          <ol className="mt-3 space-y-2">
            {retrieval.data.candidates.map((candidate) => (
              <li
                className="grid gap-2 border-l-2 border-slate-700 pl-3 text-xs md:grid-cols-[3rem_1fr_auto]"
                key={candidate.memory.id}
              >
                <span className="font-mono text-slate-500">
                  #{candidate.rank}
                </span>
                <span className="text-slate-300">
                  {candidate.memory.summary}
                </span>
                <span
                  className={
                    candidate.selected ? "text-emerald-300" : "text-amber-300"
                  }
                >
                  {candidate.selected
                    ? "selected"
                    : candidate.exclusion_reason.toLowerCase()}{" "}
                  / total {candidate.scores.total.toFixed(3)} / lexical{" "}
                  {candidate.scores.lexical.toFixed(2)} / semantic{" "}
                  {candidate.scores.semantic.toFixed(2)}
                </span>
              </li>
            ))}
          </ol>
        </div>
      ) : null}
    </section>
  );
}
