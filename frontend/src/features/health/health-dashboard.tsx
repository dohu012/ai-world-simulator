"use client";

import { useQuery } from "@tanstack/react-query";

import { apiGet } from "@/lib/api-client";
import type { HealthResponse, ReadinessResponse } from "@/types/api";

function StatusCard({
  label,
  loading,
  error,
  success,
}: Readonly<{
  label: string;
  loading: boolean;
  error: boolean;
  success: boolean;
}>) {
  const state = loading ? "加载中" : error ? "失败" : success ? "正常" : "未知";
  return (
    <section className="rounded-lg border border-slate-700 bg-slate-900 p-5">
      <h2 className="text-sm text-slate-400">{label}</h2>
      <p className="mt-2 text-xl">{state}</p>
    </section>
  );
}

export function HealthDashboard() {
  const health = useQuery({
    queryKey: ["health"],
    queryFn: () => apiGet<HealthResponse>("/health"),
  });
  const readiness = useQuery({
    queryKey: ["readiness"],
    queryFn: () => apiGet<ReadinessResponse>("/health/ready"),
  });

  return (
    <div className="mt-10 grid gap-4 sm:grid-cols-3">
      <StatusCard label="前端运行状态" loading={false} error={false} success />
      <StatusCard
        label="后端健康状态"
        loading={health.isPending}
        error={health.isError}
        success={health.data?.status === "ok"}
      />
      <StatusCard
        label="后端依赖就绪状态"
        loading={readiness.isPending}
        error={readiness.isError}
        success={readiness.data?.status === "ready"}
      />
    </div>
  );
}
