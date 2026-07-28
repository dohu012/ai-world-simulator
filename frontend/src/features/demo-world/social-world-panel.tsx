"use client";

import { useQuery } from "@tanstack/react-query";

import { apiGet } from "@/lib/api-client";

interface PropagationItem {
  transmission_id: string;
  recipient_id: string;
  channel_kind: string;
  arrival_world_time: string;
  status: string;
  reliability: number;
  distortion_policy_id: string;
  claim_value: string;
}

interface BeliefRevision {
  id: string;
  agent_id: string;
  revision: number;
  value: string;
  confidence: number;
  status: string;
  reason_code: string;
}

interface Conversation {
  id: string;
  participant_ids: string[];
  state: string;
  turn_count: number;
  max_turns: number;
  used_tokens: number;
  max_tokens: number;
  terminal_reason: string | null;
}

export function SocialWorldPanel() {
  const propagation = useQuery({
    queryKey: ["gray-harbor", "propagation"],
    queryFn: () =>
      apiGet<PropagationItem[]>("/demo/worlds/gray-harbor/propagation"),
    refetchOnMount: "always",
  });
  const beliefs = useQuery({
    queryKey: ["gray-harbor", "belief-history"],
    queryFn: () =>
      apiGet<BeliefRevision[]>("/demo/worlds/gray-harbor/beliefs/history"),
    refetchOnMount: "always",
  });
  const conversations = useQuery({
    queryKey: ["gray-harbor", "conversations"],
    queryFn: () =>
      apiGet<Conversation[]>("/demo/worlds/gray-harbor/conversations"),
    refetchOnMount: "always",
  });

  if (propagation.isLoading || beliefs.isLoading || conversations.isLoading) {
    return (
      <section className="rounded-lg border border-slate-700 bg-slate-900/80 p-5 text-slate-300">
        正在加载因果传播链…
      </section>
    );
  }
  if (propagation.isError || beliefs.isError || conversations.isError) {
    return (
      <section className="rounded-lg border border-red-800 bg-red-950/30 p-5 text-red-100">
        因果传播数据加载失败。
      </section>
    );
  }

  return (
    <section
      className="space-y-5 rounded-lg border border-slate-700 bg-slate-900/80 p-5"
      aria-label="因果信息传播与对话"
    >
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-sky-300">
          Causal Social World
        </p>
        <h2 className="mt-1 text-lg font-semibold text-slate-50">
          传播、信念演化与有界对话
        </h2>
        <p className="mt-2 text-sm text-slate-400">
          “已发送”“已送达”“被相信”和“客观真实”是不同状态。
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        {propagation.data?.map((item) => (
          <article
            key={item.transmission_id}
            className="rounded-md border border-slate-700 bg-slate-950/60 p-4"
          >
            <p className="text-xs text-sky-300">{item.channel_kind}</p>
            <h3 className="mt-1 font-semibold text-slate-50">
              {item.recipient_id}
            </h3>
            <p className="mt-2 text-sm text-slate-300">{item.claim_value}</p>
            <dl className="mt-3 space-y-1 text-xs text-slate-400">
              <div>状态：{item.status}</div>
              <div>可靠度：{Math.round(item.reliability * 100)}%</div>
              <div>失真策略：{item.distortion_policy_id}</div>
              <div>
                到达：{new Date(item.arrival_world_time).toLocaleString()}
              </div>
            </dl>
          </article>
        ))}
      </div>

      <div>
        <h3 className="font-semibold text-slate-50">Belief Evolution</h3>
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          {beliefs.data?.map((belief) => (
            <article
              key={belief.id}
              className="rounded-md border border-amber-900/70 bg-amber-950/20 p-3"
            >
              <p className="text-sm font-medium text-amber-100">
                {belief.agent_id} · 修订 {belief.revision}
              </p>
              <p className="mt-1 text-sm text-slate-300">{belief.value}</p>
              <p className="mt-2 text-xs text-slate-400">
                {belief.status} · {belief.reason_code} ·{" "}
                {Math.round(belief.confidence * 100)}%
              </p>
            </article>
          ))}
        </div>
      </div>

      <div>
        <h3 className="font-semibold text-slate-50">Bounded Conversation</h3>
        {conversations.data?.length ? (
          conversations.data.map((conversation) => (
            <article
              key={conversation.id}
              className="mt-3 rounded-md border border-emerald-900/70 bg-emerald-950/20 p-3 text-sm text-slate-300"
            >
              <p>{conversation.participant_ids.join(" ↔ ")}</p>
              <p className="mt-1">
                {conversation.state} · 回合 {conversation.turn_count}/
                {conversation.max_turns} · Token {conversation.used_tokens}/
                {conversation.max_tokens}
              </p>
              <p className="mt-1 text-xs text-slate-400">
                终止原因：{conversation.terminal_reason ?? "尚未终止"}
              </p>
            </article>
          ))
        ) : (
          <p className="mt-2 text-sm text-slate-400">修正对话尚未开启。</p>
        )}
      </div>
    </section>
  );
}
