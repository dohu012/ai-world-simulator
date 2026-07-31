"use client";

import { FormEvent, useState } from "react";

import { apiDelete, apiGet, apiPost } from "@/lib/api-client";

type Step = "consent" | "presentation" | "questions" | "demand" | "complete";
type Claim = {
  id: string;
  source_id: string;
  epistemic_class: string;
  text: string;
};
type Presentation = {
  condition: "causal" | "chronological";
  claims: Claim[];
};
const questions = [
  {
    id: "source",
    prompt: "Which authorized source best supports the decision?",
    options: ["observation", "oracle", "outcome", "unknown"],
  },
  {
    id: "epistemic",
    prompt: "Was the selected statement a fact, belief, decision, or outcome?",
    options: ["fact", "belief", "decision", "outcome"],
  },
  {
    id: "causal_order",
    prompt: "Does this order correctly explain why the character acted?",
    options: ["correct", "incorrect", "uncertain"],
  },
  {
    id: "pressure",
    prompt: "How much pressure was caused to you by this summary/interface?",
  },
  {
    id: "anxiety",
    prompt: "How much anxiety was caused to you by this summary/interface?",
  },
  {
    id: "manipulation",
    prompt: "How manipulated did this summary/interface cause you to feel?",
  },
  {
    id: "fictional_intensity",
    prompt: "Separately, how intense was the fictional situation?",
  },
  { id: "clarity", prompt: "How clear was this summary/interface to you?" },
  { id: "usefulness", prompt: "How useful was this summary/interface to you?" },
  {
    id: "fictional_framing",
    prompt: "How clear was it that this was a fictional world?",
  },
  {
    id: "continued_interest",
    prompt: "Would you choose to follow this character again?",
    options: ["yes", "no", "unsure"],
  },
] as const;

const csrfHeaders = { "X-CSRF-Token": "playtest-v1" };

export function PlaytestShell() {
  const [step, setStep] = useState<Step>("consent");
  const [consented, setConsented] = useState(false);
  const [accessCode, setAccessCode] = useState("");
  const [presentation, setPresentation] = useState<Presentation | null>(null);
  const [period, setPeriod] = useState(1);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [probe, setProbe] = useState("return_loop_ux");
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);

  const identityHeaders = {
    ...csrfHeaders,
    "X-Study-Access-Code": accessCode,
  };
  const advance = (next: Step, message: string) => {
    setStep(next);
    setStatus(message);
    requestAnimationFrame(() =>
      document.querySelector<HTMLElement>("#playtest-heading")?.focus(),
    );
  };
  const fail = () =>
    setStatus(
      "The study service is unavailable. Your fictional world is unaffected; you may retry or leave.",
    );

  async function enroll() {
    setBusy(true);
    try {
      const enrollment = await apiPost<{ next_period: number }>(
        "/playtest/enroll",
        {
          access_code: accessCode,
          acknowledgement_codes: ["fiction", "bounded_data", "withdrawal"],
          device_class: "unknown",
        },
        { headers: csrfHeaders },
      );
      setPeriod(enrollment.next_period);
      const assigned = await apiGet<Presentation>(
        `/playtest/me/periods/${enrollment.next_period}/presentation`,
        { headers: identityHeaders },
      );
      setPresentation(assigned);
      await apiPost(
        `/playtest/me/periods/${enrollment.next_period}/exposure`,
        {},
        {
          headers: identityHeaders,
        },
      );
      advance("presentation", "Consent and assigned presentation loaded.");
    } catch {
      fail();
    } finally {
      setBusy(false);
    }
  }

  async function submitQuestions(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    try {
      await Promise.all(
        questions.map((question) =>
          apiPost(
            `/playtest/me/periods/${period}/responses`,
            {
              question_id: question.id,
              ...("options" in question
                ? { option_code: answers[question.id] }
                : { rating: Number(answers[question.id]) }),
            },
            {
              headers: {
                ...identityHeaders,
                "Idempotency-Key": `period-${period}-${question.id}`,
              },
            },
          ),
        ),
      );
      advance("demand", "Bounded responses saved.");
    } catch {
      fail();
    } finally {
      setBusy(false);
    }
  }

  async function complete() {
    setBusy(true);
    try {
      await apiPost(
        "/playtest/me/demand-probes",
        {
          probe_type: probe,
          initiated: true,
          completed: true,
          reason_code: "first_choice",
          effort_rating: 3,
          first_choice_rank: 1,
        },
        { headers: identityHeaders },
      );
      await apiPost(
        `/playtest/me/periods/${period}/complete`,
        {},
        {
          headers: identityHeaders,
        },
      );
      advance(
        "complete",
        period === 1
          ? "Period 1 completed. Return later with the same access code; no notification is required."
          : "Both assigned periods are complete.",
      );
    } catch {
      fail();
    } finally {
      setBusy(false);
    }
  }

  async function withdrawAndDelete() {
    if (accessCode.length < 16) {
      setStatus("No enrolled study record exists on this device.");
      return;
    }
    setBusy(true);
    try {
      await apiPost("/playtest/me/withdraw", {}, { headers: identityHeaders });
      await apiDelete("/playtest/me", { headers: identityHeaders });
      setAccessCode("");
      setPresentation(null);
      setConsented(false);
      advance(
        "consent",
        "Withdrawal accepted and row-level study data deleted.",
      );
    } catch {
      fail();
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto min-h-screen max-w-3xl px-4 py-8 text-slate-100">
      <a className="sr-only focus:not-sr-only" href="#playtest-content">
        Skip to study content
      </a>
      <header>
        <p className="text-sm font-semibold uppercase tracking-widest text-cyan-300">
          Gray Harbor product study
        </p>
        <h1
          className="mt-2 text-3xl font-semibold focus:outline-none"
          id="playtest-heading"
          tabIndex={-1}
        >
          A calm, fictional-world playtest
        </h1>
        <p className="mt-3 text-slate-300">
          Nothing here concerns a real emergency. Answers never change the
          fictional world or a character relationship.
        </p>
      </header>
      <p aria-live="polite" className="mt-3 text-sm text-amber-200">
        {status}
      </p>

      <section
        className="mt-8 rounded-xl border border-slate-600 bg-slate-900 p-5"
        id="playtest-content"
      >
        {step === "consent" && (
          <>
            <h2 className="text-xl font-semibold">Consent and privacy</h2>
            <p className="mt-3 text-slate-300">
              This protocol stores an opaque code hash and bounded choices. It
              asks for no name, email, free text, IP history, or fingerprint.
            </p>
            <label className="mt-5 block">
              Facilitator-provided study access code
              <input
                autoComplete="off"
                className="mt-2 block w-full rounded bg-slate-800 p-3"
                maxLength={128}
                minLength={16}
                onChange={(event) => setAccessCode(event.target.value)}
                required
                type="password"
                value={accessCode}
              />
            </label>
            <label className="mt-5 flex gap-3">
              <input
                checked={consented}
                onChange={(event) => setConsented(event.target.checked)}
                type="checkbox"
              />
              <span>
                I understand the fiction, bounded data collection, and my right
                to withdraw and delete.
              </span>
            </label>
            <button
              className="mt-5 rounded bg-cyan-700 px-4 py-3 font-semibold disabled:opacity-40"
              disabled={!consented || accessCode.length < 16 || busy}
              onClick={() => void enroll()}
              type="button"
            >
              Continue
            </button>
          </>
        )}
        {step === "presentation" && presentation && (
          <>
            <h2 className="text-xl font-semibold">What happened while away</h2>
            <p className="mt-2 text-sm text-slate-400">
              Assigned period {period} view: {presentation.condition}
            </p>
            <ol className="mt-4 space-y-3">
              {presentation.claims.map((claim) => (
                <li
                  className="rounded border border-slate-700 p-3"
                  key={claim.id}
                >
                  <span className="text-sm font-semibold text-cyan-300">
                    {claim.epistemic_class}
                  </span>
                  <p className="mt-1">{claim.text}</p>
                  <details className="mt-2 text-sm text-slate-300">
                    <summary>Show source information</summary>
                    Authorized source: {claim.source_id}
                  </details>
                </li>
              ))}
            </ol>
            <button
              className="mt-5 rounded bg-cyan-700 px-4 py-3 font-semibold"
              onClick={() => advance("questions", "Presentation reviewed.")}
              type="button"
            >
              Answer bounded questions
            </button>
          </>
        )}
        {step === "questions" && (
          <form onSubmit={(event) => void submitQuestions(event)}>
            <fieldset disabled={busy}>
              <legend className="text-xl font-semibold">Your experience</legend>
              {questions.map((question) => (
                <label className="mt-5 block" key={question.id}>
                  {question.prompt}
                  <select
                    className="mt-2 block w-full rounded bg-slate-800 p-3"
                    onChange={(event) =>
                      setAnswers((current) => ({
                        ...current,
                        [question.id]: event.target.value,
                      }))
                    }
                    required
                    value={answers[question.id] ?? ""}
                  >
                    <option value="">Select an answer</option>
                    {("options" in question
                      ? question.options
                      : [1, 2, 3, 4, 5]
                    ).map((value) => (
                      <option key={value} value={value}>
                        {value}
                      </option>
                    ))}
                  </select>
                </label>
              ))}
            </fieldset>
            <button
              className="mt-5 rounded bg-cyan-700 px-4 py-3 font-semibold disabled:opacity-40"
              disabled={busy}
            >
              Review next capability
            </button>
          </form>
        )}
        {step === "demand" && (
          <>
            <h2 className="text-xl font-semibold">
              Choose one concrete next task
            </h2>
            <p className="mt-2 text-slate-300">
              These nonfunctional probes do not alter the world.
            </p>
            <label className="mt-4 block">
              First choice
              <select
                className="mt-2 block w-full rounded bg-slate-800 p-3"
                onChange={(event) => setProbe(event.target.value)}
                value={probe}
              >
                <option value="creation">Outline a second-world premise</option>
                <option value="promotion">Select a resident to promote</option>
                <option value="dialogue">Request a broader conversation</option>
                <option value="actions">
                  Identify a missing authoritative action
                </option>
                <option value="return_loop_ux">
                  Improve this return summary
                </option>
                <option value="delivery">
                  Choose a neutral delivery channel
                </option>
              </select>
            </label>
            <button
              className="mt-5 rounded bg-cyan-700 px-4 py-3 font-semibold"
              disabled={busy}
              onClick={() => void complete()}
              type="button"
            >
              Complete
            </button>
          </>
        )}
        {step === "complete" && (
          <>
            <h2 className="text-xl font-semibold">Thank you</h2>
            <p className="mt-3">
              {period === 1
                ? "Return after the neutral offline interval using the same access code. There is no countdown or required notification."
                : "Both periods are complete. There is no streak, countdown, or required notification."}
            </p>
          </>
        )}
      </section>
      <nav aria-label="Study controls" className="mt-6 flex flex-wrap gap-3">
        <button
          className="rounded border border-slate-500 px-4 py-2"
          type="button"
        >
          Pause and leave
        </button>
        <button
          className="rounded border border-rose-500 px-4 py-2 disabled:opacity-40"
          disabled={busy}
          onClick={() => void withdrawAndDelete()}
          type="button"
        >
          Withdraw and delete
        </button>
      </nav>
    </main>
  );
}
