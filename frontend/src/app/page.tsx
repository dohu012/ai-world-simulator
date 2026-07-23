import { HealthDashboard } from "@/features/health/health-dashboard";

export default function Home() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-16">
      <p className="text-sm uppercase tracking-[0.25em] text-cyan-300">
        Development Environment
      </p>
      <h1 className="mt-3 text-4xl font-semibold">AI 世界观察与干预模拟器</h1>
      <HealthDashboard />
    </main>
  );
}
