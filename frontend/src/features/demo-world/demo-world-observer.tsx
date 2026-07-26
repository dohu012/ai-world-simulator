"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import {
  confidencePercent,
  formatWorldTime,
  visibilityLabel,
} from "@/features/demo-world/demo-world-types";
import { apiGet } from "@/lib/api-client";
import type {
  DemoAgentPerspectiveResponse,
  DemoWorldResponse,
} from "@/types/api";

function SectionTitle({
  eyebrow,
  title,
}: Readonly<{ eyebrow: string; title: string }>) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-sky-300">
        {eyebrow}
      </p>
      <h2 className="mt-1 text-lg font-semibold text-slate-50">{title}</h2>
    </div>
  );
}

export function DemoWorldObserver() {
  const [selectedAgentId, setSelectedAgentId] = useState("char-chen-mo");
  const { data, error, isError, isLoading } = useQuery({
    queryKey: ["demo-world", "gray-harbor"],
    queryFn: () => apiGet<DemoWorldResponse>("/demo/worlds/gray-harbor"),
  });
  const selectedAgent = data?.characters.find(
    (character) => character.id === selectedAgentId,
  );
  const {
    data: perspective,
    error: perspectiveError,
    isError: isPerspectiveError,
    isLoading: isPerspectiveLoading,
  } = useQuery({
    queryKey: [
      "demo-world",
      "gray-harbor",
      "agent-perspective",
      selectedAgentId,
    ],
    queryFn: () =>
      apiGet<DemoAgentPerspectiveResponse>(
        `/demo/worlds/gray-harbor/agents/${selectedAgentId}/perspective`,
      ),
    enabled: Boolean(selectedAgentId),
  });

  if (isLoading) {
    return (
      <section
        className="rounded-lg border border-slate-700 bg-slate-900/80 p-5 text-sm text-slate-300"
        aria-label="固定世界观察台加载中"
      >
        正在加载灰港封锁区观察台...
      </section>
    );
  }

  if (isError || !data) {
    return (
      <section
        className="rounded-lg border border-red-800 bg-red-950/30 p-5 text-sm text-red-100"
        aria-label="固定世界观察台错误"
      >
        灰港封锁区观察台加载失败：
        {error instanceof Error ? error.message : "未知错误"}
      </section>
    );
  }

  const selectedObservations = perspective?.observations ?? [];
  const selectedBeliefs = perspective?.beliefs ?? [];
  const oracleRequest = perspective?.oracleRequests?.[0];
  const oracleResponse = perspective?.oracleResponses?.[0];
  const actionIntent = perspective?.actionIntents?.[0];
  const actionResult = perspective?.actionResults?.[0];

  return (
    <section className="space-y-6" aria-label="固定世界观察台">
      <div className="border-b border-slate-700 pb-5">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-amber-300">
          静态开发切片
        </p>
        <div className="mt-3 flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h1 className="text-3xl font-semibold text-white">
              {data.world.name}
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
              {data.world.description}
            </p>
          </div>
          <dl className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-3">
            <div className="border-l-2 border-sky-400 pl-3">
              <dt className="text-slate-400">世界时间</dt>
              <dd className="font-medium text-slate-100">
                {formatWorldTime(data.world.current_time)}
              </dd>
            </div>
            <div className="border-l-2 border-emerald-400 pl-3">
              <dt className="text-slate-400">特殊角色</dt>
              <dd className="font-medium text-slate-100">
                {data.characters.length} 人
              </dd>
            </div>
            <div className="border-l-2 border-amber-400 pl-3">
              <dt className="text-slate-400">前端职责</dt>
              <dd className="font-medium text-slate-100">只读展示</dd>
            </div>
          </dl>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.08fr_0.92fr]">
        <section className="rounded-lg border border-slate-700 bg-slate-900/80 p-5">
          <SectionTitle eyebrow="Objective World" title="客观世界事件时间线" />
          <ol className="mt-5 space-y-4">
            {data.events.map((event) => (
              <li
                key={event.id}
                className="grid gap-3 border-l-2 border-slate-600 pl-4 sm:grid-cols-[110px_1fr]"
              >
                <time className="text-sm font-medium text-slate-300">
                  {formatWorldTime(event.occurred_at)}
                </time>
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="font-semibold text-slate-50">
                      {event.title}
                    </h3>
                    <span className="rounded border border-slate-600 px-2 py-0.5 text-xs text-slate-300">
                      {visibilityLabel(event)}
                    </span>
                  </div>
                  <p className="mt-1 text-sm leading-6 text-slate-300">
                    {event.description}
                  </p>
                </div>
              </li>
            ))}
          </ol>
        </section>

        <section className="rounded-lg border border-slate-700 bg-slate-900/80 p-5">
          <SectionTitle eyebrow="Special Agents" title="角色主观入口" />
          <div className="mt-4 grid gap-3">
            {data.characters.map((character) => {
              const active = character.id === selectedAgentId;
              return (
                <button
                  className={`rounded-md border p-4 text-left transition ${
                    active
                      ? "border-sky-400 bg-sky-950/60"
                      : "border-slate-700 bg-slate-950/50 hover:border-slate-500"
                  }`}
                  key={character.id}
                  type="button"
                  onClick={() => setSelectedAgentId(character.id)}
                  aria-pressed={active}
                >
                  <div className="flex items-center justify-between gap-3">
                    <span className="font-semibold text-slate-50">
                      {character.name}
                    </span>
                    <span className="text-xs text-slate-400">
                      {character.occupation}
                    </span>
                  </div>
                  <p className="mt-2 text-sm leading-6 text-slate-300">
                    {character.description}
                  </p>
                </button>
              );
            })}
          </div>
        </section>
      </div>

      <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <section className="rounded-lg border border-slate-700 bg-slate-900/80 p-5">
          <SectionTitle
            eyebrow="First Person View"
            title={`${selectedAgent?.name ?? "角色"}的第一视角`}
          />
          {isPerspectiveLoading ? (
            <p
              className="mt-4 text-sm text-slate-300"
              aria-label="角色第一视角加载中"
            >
              正在加载角色第一视角...
            </p>
          ) : null}
          {isPerspectiveError ? (
            <p
              className="mt-4 rounded-md border border-red-800 bg-red-950/30 p-3 text-sm text-red-100"
              aria-label="角色第一视角错误"
            >
              角色第一视角加载失败：
              {perspectiveError instanceof Error
                ? perspectiveError.message
                : "未知错误"}
            </p>
          ) : null}
          <div className="mt-4 space-y-4">
            {!isPerspectiveLoading && !isPerspectiveError
              ? selectedObservations.map((observation) => (
                  <article
                    key={observation.id}
                    className="rounded-md border border-slate-700 bg-slate-950/60 p-4"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <h3 className="font-semibold text-slate-50">
                        Observation
                      </h3>
                      <time className="text-sm text-slate-400">
                        {formatWorldTime(observation.observed_at)}
                      </time>
                    </div>
                    <p className="mt-2 text-sm text-slate-300">
                      {String(observation.metadata.perspective_note)}
                    </p>
                    <div className="mt-3 space-y-2 text-sm leading-6 text-slate-200">
                      {observation.visible_entities.map((entity) => (
                        <p key={entity.entity.entity_id}>
                          看到：{entity.description}
                        </p>
                      ))}
                      {observation.heard_statements.map((statement) => (
                        <p key={statement.content}>听到：{statement.content}</p>
                      ))}
                      {observation.felt_changes.map((change) => (
                        <p key={change.description}>
                          感到：{change.description}
                        </p>
                      ))}
                    </div>
                  </article>
                ))
              : null}
            {!isPerspectiveLoading &&
            !isPerspectiveError &&
            selectedObservations.length === 0 ? (
              <p className="text-sm text-slate-400">该角色暂无观察记录。</p>
            ) : null}
          </div>
        </section>

        <section className="rounded-lg border border-slate-700 bg-slate-900/80 p-5">
          <SectionTitle eyebrow="Subjective Beliefs" title="主观 Belief" />
          <div className="mt-4 space-y-3">
            {!isPerspectiveLoading && !isPerspectiveError
              ? selectedBeliefs.map((belief) => (
                  <article
                    key={belief.id}
                    className="rounded-md border border-slate-700 bg-slate-950/60 p-4"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <h3 className="font-semibold text-slate-50">
                        {belief.subject} {belief.predicate}
                      </h3>
                      <span className="text-sm text-amber-200">
                        置信度 {confidencePercent(belief)}
                      </span>
                    </div>
                    <p className="mt-2 text-sm leading-6 text-slate-300">
                      {String(belief.object)}
                    </p>
                    <p className="mt-2 text-xs text-slate-500">
                      来源：{belief.source_type}，不自动等同于客观事实
                    </p>
                  </article>
                ))
              : null}
            {!isPerspectiveLoading &&
            !isPerspectiveError &&
            selectedBeliefs.length === 0 ? (
              <p className="text-sm text-slate-400">该角色暂无信念记录。</p>
            ) : null}
          </div>
        </section>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <section className="rounded-lg border border-amber-700/70 bg-amber-950/30 p-5">
          <SectionTitle eyebrow="Player Revelation" title="玩家启示请求" />
          <div className="mt-4 space-y-3 text-sm leading-6 text-amber-50">
            {oracleRequest && oracleResponse ? (
              <>
                <p>
                  <span className="font-semibold">请求者：</span>
                  {perspective?.character.name ?? oracleRequest.agent_id}
                </p>
                <p>
                  <span className="font-semibold">问题：</span>
                  {oracleRequest.question}
                </p>
                <p>
                  <span className="font-semibold">玩家建议：</span>
                  {oracleResponse.content}
                </p>
              </>
            ) : (
              <p>当前角色暂无玩家启示请求。</p>
            )}
            <p className="rounded-md border border-amber-700/70 bg-slate-950/50 p-3 text-amber-100">
              建议是信息，不是命令。角色可能接受、误解或拒绝；世界结果仍由裁定层决定。
            </p>
            <button
              className="rounded-md border border-amber-500 px-4 py-2 text-sm font-medium text-amber-100 opacity-70"
              type="button"
              disabled
            >
              发送建议（静态演示不可提交）
            </button>
          </div>
        </section>

        <section className="rounded-lg border border-slate-700 bg-slate-900/80 p-5">
          <SectionTitle eyebrow="Action Lifecycle" title="行动意图与裁定结果" />
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <article className="rounded-md border border-sky-800 bg-sky-950/40 p-4">
              <h3 className="font-semibold text-slate-50">ActionIntent</h3>
              <p className="mt-2 text-sm leading-6 text-slate-300">
                {actionIntent?.reason_summary ?? "当前角色暂无行动意图记录。"}
              </p>
              <p className="mt-2 text-xs text-slate-400">
                只表示角色想尝试，不声明成功。
              </p>
            </article>
            <article className="rounded-md border border-emerald-800 bg-emerald-950/30 p-4">
              <h3 className="font-semibold text-slate-50">ActionResult</h3>
              <p className="mt-2 text-sm leading-6 text-slate-300">
                {actionResult
                  ? "配送员没有接电话，但陈沫发现库存还剩两箱饮用水；她暂时推迟前往北门。"
                  : "当前角色暂无裁定结果记录。"}
              </p>
              {actionResult ? (
                <p className="mt-2 text-xs text-slate-400">
                  状态：{actionResult.status}，由世界裁定产生。
                </p>
              ) : null}
            </article>
          </div>
        </section>
      </div>
    </section>
  );
}
