"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { apiGet, apiPost } from "@/lib/api-client";
import { demoCurrentAgentId } from "@/features/demo-world/demo-agent-api";
import type { ReturnLoopResponse } from "@/types/api";

export function ReturnLoopPanel() {
  const queryClient = useQueryClient();
  const [permission, setPermission] = useState<
    "unsupported" | NotificationPermission
  >("unsupported");
  const { data, isLoading, isError } = useQuery({
    queryKey: ["return-loop"],
    queryFn: () =>
      apiGet<ReturnLoopResponse>("/demo/worlds/gray-harbor/me/return-loop", {
        headers: { "X-Demo-Agent-Id": demoCurrentAgentId },
      }),
  });
  const updateItem = useMutation({
    mutationFn: ({ id, action }: { id: string; action: "read" | "dismiss" }) =>
      apiPost<void>(
        `/demo/worlds/gray-harbor/me/return-loop/inbox/${id}/${action}`,
        {},
        {
          headers: {
            "X-CSRF-Token": "demo-return-loop",
            "X-Demo-Agent-Id": demoCurrentAgentId,
          },
        },
      ),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["return-loop"] }),
  });

  useEffect(() => {
    if ("Notification" in window) setPermission(Notification.permission);
    if ("serviceWorker" in navigator) {
      void navigator.serviceWorker.register("/sw.js", { scope: "/" });
    }
  }, []);

  async function askPermission() {
    if ("Notification" in window) {
      setPermission(await Notification.requestPermission());
    }
  }

  return (
    <section
      className="rounded-lg border border-sky-800 bg-slate-900/80 p-5"
      aria-labelledby="return-loop-title"
    >
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-sky-300">
        Offline Return
      </p>
      <h2
        id="return-loop-title"
        className="mt-1 text-lg font-semibold text-white"
      >
        离线期间发生了什么
      </h2>
      <p className="mt-2 text-sm text-slate-300">
        所有内容均为虚构世界更新。站内体验完整可用；浏览器推送默认关闭。
      </p>
      {isLoading ? <p className="mt-4 text-sm">正在编译因果摘要…</p> : null}
      {isError ? (
        <p className="mt-4 text-sm text-red-300">
          摘要暂不可用，可查看时间线。
        </p>
      ) : null}
      {data?.summary?.claims && data.inbox && data.debug ? (
        <div className="mt-5 grid gap-5 lg:grid-cols-[1.4fr_0.6fr]">
          <ol className="space-y-3">
            {data.summary.claims.map((claim) => (
              <li
                key={claim.id}
                className="rounded border border-slate-700 p-3"
              >
                <div className="flex flex-wrap gap-2">
                  <span className="rounded bg-sky-950 px-2 py-0.5 text-xs text-sky-200">
                    {claim.epistemic_class}
                  </span>
                  <span className="text-xs text-slate-500">虚构内容</span>
                </div>
                <p className="mt-2 text-sm text-slate-200">{claim.text}</p>
                <p className="mt-2 text-xs text-slate-400">
                  纳入原因：重要且在离线区间内可见 · 来源 {claim.source_id}
                </p>
              </li>
            ))}
          </ol>
          <aside className="rounded border border-slate-700 p-4">
            <h3 className="font-semibold text-white">通知、权限与成本</h3>
            <dl className="mt-3 space-y-2 text-sm">
              <div>
                <dt className="text-slate-400">站内项目</dt>
                <dd>{data.inbox.length}</dd>
              </div>
              <div>
                <dt className="text-slate-400">推送</dt>
                <dd>关闭（需主动启用）</dd>
              </div>
              <div>
                <dt className="text-slate-400">摘要模式</dt>
                <dd>{String(data.debug.summary_mode)}</dd>
              </div>
              <div>
                <dt className="text-slate-400">模型/提供商调用</dt>
                <dd>{String(data.debug.provider_calls)}</dd>
              </div>
            </dl>
            <div className="mt-4 border-t border-slate-700 pt-4">
              <p className="text-sm text-slate-300">
                浏览器权限：{permission}。权限不等于订阅，拒绝后不会再次催促。
              </p>
              {permission === "default" ? (
                <button
                  className="mt-3 rounded border border-slate-500 px-3 py-2 text-sm"
                  type="button"
                  onClick={() => void askPermission()}
                >
                  主动检查浏览器通知权限
                </button>
              ) : null}
            </div>
            {data.inbox.map((item) => (
              <div className="mt-4 flex gap-2" key={item.id}>
                <button
                  className="rounded border border-sky-600 px-3 py-2 text-sm"
                  disabled={item.read || updateItem.isPending}
                  type="button"
                  onClick={() =>
                    updateItem.mutate({ id: item.id, action: "read" })
                  }
                >
                  {item.read ? "已读" : "标为已读"}
                </button>
                <button
                  className="rounded border border-slate-600 px-3 py-2 text-sm"
                  disabled={updateItem.isPending}
                  type="button"
                  onClick={() =>
                    updateItem.mutate({ id: item.id, action: "dismiss" })
                  }
                >
                  忽略
                </button>
              </div>
            ))}
          </aside>
        </div>
      ) : null}
    </section>
  );
}
