import { AgentDecisionPanel } from "@/features/demo-world/agent-decision-panel";
import { DemoAgentInputFeed } from "@/features/demo-world/demo-agent-input-feed";
import { DemoWorldObserver } from "@/features/demo-world/demo-world-observer";
import { DemoAgentPreview } from "@/features/demo-world/demo-agent-preview";
import { ReplayInspector } from "@/features/demo-world/replay-inspector";
import { SocialWorldPanel } from "@/features/demo-world/social-world-panel";
import { WorldRuntimePanel } from "@/features/demo-world/world-runtime-panel";
import { SevenDayScenarioPanel } from "@/features/demo-world/seven-day-scenario-panel";
import { HealthDashboard } from "@/features/health/health-dashboard";
import { MemoryPanel } from "@/features/demo-world/memory-panel";
import { EvolutionPanel } from "@/features/demo-world/evolution-panel";
import { ReturnLoopPanel } from "@/features/demo-world/return-loop-panel";

export default function Home() {
  return (
    <main className="mx-auto max-w-7xl px-5 py-8 sm:px-6 lg:px-8">
      <DemoWorldObserver />
      <div className="mt-6">
        <ReplayInspector />
        <div className="mt-6">
          <WorldRuntimePanel />
        </div>
      </div>
      <div className="mt-6">
        <SocialWorldPanel />
      </div>
      <div className="mt-6">
        <AgentDecisionPanel />
      </div>
      <div className="mt-6">
        <DemoAgentPreview />
      </div>
      <div className="mt-6">
        <DemoAgentInputFeed />
      </div>
      <div className="mt-6">
        <MemoryPanel />
      </div>
      <div className="mt-6">
        <EvolutionPanel />
      </div>
      <div className="mt-6">
        <ReturnLoopPanel />
      </div>
      <section className="mt-6 rounded-lg border border-slate-700 bg-slate-900/80 p-5">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">
            System Health
          </p>
          <h2 className="mt-1 text-lg font-semibold text-slate-50">
            开发环境健康检查
          </h2>
        </div>
        <HealthDashboard />
      </section>
      <div className="mt-6">
        <SevenDayScenarioPanel />
      </div>
    </main>
  );
}
