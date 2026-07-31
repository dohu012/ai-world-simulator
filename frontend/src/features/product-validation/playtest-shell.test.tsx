import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { PlaytestShell } from "./playtest-shell";

describe("PlaytestShell", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/presentation")) {
          return new Response(
            JSON.stringify({
              condition: "causal",
              claims: [
                {
                  id: "claim-1",
                  source_id: "source-1",
                  epistemic_class: "observed",
                  text: "Chen observed the flooded road.",
                },
              ],
            }),
            { status: 200, headers: { "Content-Type": "application/json" } },
          );
        }
        return new Response(
          JSON.stringify({
            participant_id: "study-test",
            sequence: "AB",
            next_period: 1,
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        );
      }),
    );
  });

  it("separates participant pressure from fictional intensity", async () => {
    render(<PlaytestShell />);
    fireEvent.change(
      screen.getByLabelText(/facilitator-provided study access code/i),
      { target: { value: "abcdefghijklmnop" } },
    );
    fireEvent.click(screen.getByRole("checkbox"));
    fireEvent.click(screen.getByRole("button", { name: "Continue" }));
    await waitFor(() =>
      expect(
        screen.getByRole("button", { name: "Answer bounded questions" }),
      ).toBeInTheDocument(),
    );
    fireEvent.click(
      screen.getByRole("button", { name: "Answer bounded questions" }),
    );
    expect(
      screen.getByLabelText(/pressure was caused to you/i),
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/fictional situation/i)).toBeInTheDocument();
  });

  it("offers withdrawal and no notification prompt", () => {
    render(<PlaytestShell />);
    expect(
      screen.queryByText(/enable push|missed you|need you/i),
    ).not.toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Withdraw and delete" }),
    ).toBeInTheDocument();
  });
});
