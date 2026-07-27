"use client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { apiGet, apiPost, ApiClientError } from "@/lib/api-client";
import type { OracleWindowResponse, RuntimeResponse } from "@/types/api";

export function WorldRuntimePanel() {
  const queryClient = useQueryClient();
  const [reply, setReply] = useState("");
  const runtime = useQuery({
    queryKey: ["world-runtime"],
    queryFn: () => apiGet<RuntimeResponse>("/demo/worlds/gray-harbor/runtime"),
    retry: false,
  });
  const oracle = useQuery({
    queryKey: ["oracle-inbox"],
    queryFn: () =>
      apiGet<OracleWindowResponse[]>(
        "/demo/worlds/gray-harbor/oracle-requests",
      ),
  });
  const refresh = () => {
    void queryClient.invalidateQueries({ queryKey: ["world-runtime"] });
    void queryClient.invalidateQueries({ queryKey: ["oracle-inbox"] });
  };
  const command = useMutation({
    mutationFn: (path: string) => apiPost<RuntimeResponse>(path, {}),
    onSuccess: refresh,
  });
  const advance = useMutation({
    mutationFn: () =>
      apiPost<RuntimeResponse>("/demo/worlds/gray-harbor/runtime/advance", {
        minutes: 10,
        expected_generation: runtime.data?.generation ?? 0,
      }),
    onSuccess: refresh,
  });
  const windows = Array.isArray(oracle.data) ? oracle.data : [];
  const waiting = windows.find((item) => item.status === "waiting");
  const respond = useMutation({
    mutationFn: () =>
      apiPost<OracleWindowResponse>(
        `/demo/worlds/gray-harbor/oracle-requests/${waiting?.request_id}/responses`,
        { content: reply },
      ),
    onSuccess: () => {
      setReply("");
      refresh();
    },
  });
  const error = command.error ?? advance.error ?? respond.error;
  return (
    <section
      aria-label="World Runtime Control"
      className="rounded-lg border border-violet-800 bg-slate-900/80 p-5"
    >
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-violet-300">
        Durable World Runtime
      </p>
      <h2 className="mt-1 text-lg font-semibold text-white">
        World clock and Oracle inbox
      </h2>
      <p className="mt-2 text-sm text-slate-300">
        {runtime.data
          ? `${runtime.data.status} ? ${runtime.data.world_time} ? generation ${runtime.data.generation}`
          : "Runtime is disabled or not started."}
      </p>
      <div className="mt-3 flex flex-wrap gap-2">
        {["start", "pause", "resume"].map((name) => (
          <button
            key={name}
            onClick={() =>
              command.mutate(`/demo/worlds/gray-harbor/runtime/${name}`)
            }
            className="rounded border border-violet-500 px-3 py-1 text-sm text-violet-100"
          >
            {name}
          </button>
        ))}
        <button
          onClick={() => advance.mutate()}
          disabled={!runtime.data || advance.isPending}
          className="rounded border border-amber-500 px-3 py-1 text-sm text-amber-100 disabled:opacity-50"
        >
          advance 10m
        </button>
      </div>
      {error ? (
        <p role="alert" className="mt-3 text-sm text-red-300">
          {error instanceof ApiClientError ? error.code : "COMMAND_FAILED"}
        </p>
      ) : null}
      <div className="mt-5 border-t border-slate-700 pt-4">
        <h3 className="font-semibold text-white">Oracle Inbox</h3>
        {waiting ? (
          <>
            <p className="mt-2 text-sm text-slate-300">{waiting.question}</p>
            <p className="mt-1 text-xs text-slate-400">
              Advice is information, not a command. Deadline:{" "}
              {waiting.world_deadline}
            </p>
            <textarea
              aria-label="Oracle advice"
              value={reply}
              onChange={(event) => setReply(event.target.value)}
              className="mt-3 w-full rounded border border-slate-600 bg-slate-950 p-2 text-sm"
            />
            <button
              onClick={() => respond.mutate()}
              disabled={!reply.trim()}
              className="mt-2 rounded border border-emerald-500 px-3 py-1 text-sm text-emerald-100 disabled:opacity-50"
            >
              Send advice
            </button>
          </>
        ) : (
          <p className="mt-2 text-sm text-slate-400">No waiting request.</p>
        )}
        {windows.map((item) => (
          <p key={item.request_id} className="mt-2 text-xs text-slate-400">
            {item.request_id} ? {item.status} ? {item.outcome ?? "pending"}
          </p>
        ))}
      </div>
    </section>
  );
}
