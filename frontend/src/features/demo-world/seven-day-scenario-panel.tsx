"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiGet, apiPost } from "@/lib/api-client";
import type { RuntimeResponse, SevenDayScenarioResponse } from "@/types/api";

export function SevenDayScenarioPanel() {
  const client = useQueryClient();
  const scenario = useQuery({
    queryKey: ["seven-day-scenario"],
    queryFn: () =>
      apiGet<SevenDayScenarioResponse>("/demo/worlds/gray-harbor/scenario"),
  });
  const runtime = useQuery({
    queryKey: ["world-runtime"],
    queryFn: () => apiGet<RuntimeResponse>("/demo/worlds/gray-harbor/runtime"),
    retry: false,
  });
  const refresh = () =>
    Promise.all([
      client.invalidateQueries({ queryKey: ["seven-day-scenario"] }),
      client.invalidateQueries({ queryKey: ["world-runtime"] }),
    ]);
  const reset = useMutation({
    mutationFn: () =>
      apiPost<SevenDayScenarioResponse>(
        "/demo/worlds/gray-harbor/scenario/reset",
        {},
      ),
    onSuccess: refresh,
  });
  const start = useMutation({
    mutationFn: () =>
      apiPost<RuntimeResponse>("/demo/worlds/gray-harbor/runtime/start", {}),
    onSuccess: refresh,
  });
  const advance = useMutation({
    mutationFn: () =>
      apiPost<RuntimeResponse>("/demo/worlds/gray-harbor/runtime/advance", {
        minutes: 1440,
        expected_generation: runtime.data?.generation ?? 0,
      }),
    onSuccess: refresh,
  });
  const candidate = scenario.data;
  const data =
    candidate &&
    candidate.resources &&
    Array.isArray(candidate.residents) &&
    Array.isArray(candidate.plans) &&
    Array.isArray(candidate.actions)
      ? candidate
      : undefined;
  return (
    <section
      aria-label="Seven Day Gray Harbor"
      className="border-y border-slate-700 bg-slate-950 py-5"
    >
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase text-amber-300">
            Gray Harbor / Day {data?.current_day ?? 0} of 7
          </p>
          <h2 className="mt-1 text-xl font-semibold text-white">
            Resources, plans and consequences
          </h2>
        </div>
        <div className="flex gap-2">
          <button
            className="border border-slate-500 px-3 py-2 text-sm text-slate-100"
            onClick={() => reset.mutate()}
            type="button"
          >
            Reset
          </button>
          <button
            className="border border-emerald-500 px-3 py-2 text-sm text-emerald-100 disabled:opacity-40"
            disabled={runtime.data?.status === "running" || start.isPending}
            onClick={() => start.mutate()}
            type="button"
          >
            Start
          </button>
          <button
            className="border border-amber-500 px-3 py-2 text-sm text-amber-100 disabled:opacity-40"
            disabled={
              !data ||
              data.current_day >= 7 ||
              runtime.data?.status !== "running" ||
              advance.isPending
            }
            onClick={() => advance.mutate()}
            type="button"
          >
            Advance day
          </button>
        </div>
      </div>
      {scenario.isLoading ? (
        <p className="mt-4 text-sm text-slate-400">Loading scenario state...</p>
      ) : null}
      {scenario.isError ? (
        <p className="mt-4 text-sm text-red-300" role="alert">
          Scenario state is unavailable.
        </p>
      ) : null}
      {data ? (
        <>
          <dl className="mt-5 grid grid-cols-2 gap-4 sm:grid-cols-4">
            {Object.entries(data.resources).map(([name, amount]) => (
              <div className="border-l-2 border-emerald-500 pl-3" key={name}>
                <dt className="text-xs uppercase text-slate-400">{name}</dt>
                <dd className="text-xl font-semibold text-white">{amount}</dd>
              </div>
            ))}
            <div className="border-l-2 border-sky-500 pl-3">
              <dt className="text-xs uppercase text-slate-400">Residents</dt>
              <dd className="text-xl font-semibold text-white">
                {data.residents.length}
              </dd>
            </div>
          </dl>
          <div className="mt-6 grid gap-6 lg:grid-cols-2">
            <div>
              <h3 className="font-semibold text-white">Active plans</h3>
              <div className="mt-3 divide-y divide-slate-700 border-y border-slate-700">
                {data.plans.map((plan) => (
                  <div className="py-3" key={plan.owner_id}>
                    <div className="flex justify-between gap-3 text-sm">
                      <span className="text-slate-100">{plan.objective}</span>
                      <span className="text-amber-200">{plan.status}</span>
                    </div>
                    {plan.blockage_code ? (
                      <p className="mt-1 text-xs text-red-300">
                        {plan.blockage_code}
                      </p>
                    ) : null}
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h3 className="font-semibold text-white">Latest consequences</h3>
              <ol className="mt-3 space-y-3">
                {data.actions.slice(-4).map((action) => (
                  <li
                    className="text-sm text-slate-300"
                    key={`${action.day}-${action.action_type}`}
                  >
                    Day {action.day}: {action.consequence}
                    {action.failure_code ? (
                      <span className="ml-2 text-red-300">
                        {action.failure_code}
                      </span>
                    ) : null}
                  </li>
                ))}
              </ol>
            </div>
          </div>
          {data.outcomes.length ? (
            <div className="mt-6 border-l-2 border-red-500 pl-4">
              <h3 className="font-semibold text-white">Irreversible outcome</h3>
              {data.outcomes.map((outcome) => (
                <p className="mt-1 text-sm text-slate-300" key={outcome}>
                  {outcome}
                </p>
              ))}
            </div>
          ) : null}
        </>
      ) : null}
    </section>
  );
}
