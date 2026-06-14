import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NextIntlClientProvider } from "next-intl";
import { StepRenderer } from "./StepRenderer";

// Mock VoiceRecorder — it touches navigator.mediaDevices which jsdom doesn't
// provide. We're testing StepRenderer's keyboard/text path here.
vi.mock("./VoiceRecorder", () => ({
  VoiceRecorder: () => <div data-testid="voice-recorder-stub" />,
}));

const messages = {
  lesson: {
    continue: "Continue",
    correct: "Good work",
    tryAgain: "Try again",
    whatIsInSpanish: "What is in Spanish",
    sayThis: "Say or type this in English",
    check: "Check",
    typeAnswer: "Type your answer...",
  },
};

function renderStep(step: unknown, onComplete = vi.fn()) {
  render(
    <NextIntlClientProvider locale="en" messages={messages}>
      <StepRenderer step={step} onComplete={onComplete} />
    </NextIntlClientProvider>,
  );
  return onComplete;
}

describe("StepRenderer", () => {
  describe("intro step", () => {
    it("renders bilingual prompt and emits score 1.0 on continue", async () => {
      const user = userEvent.setup();
      const onComplete = renderStep({
        step_type: "intro",
        prompt: { en: "Welcome!", es: "¡Bienvenido!" },
      });
      expect(screen.getByText("Welcome!")).toBeInTheDocument();
      expect(screen.getByText("¡Bienvenido!")).toBeInTheDocument();
      await user.click(screen.getByRole("button", { name: "Continue" }));
      expect(onComplete).toHaveBeenCalledWith(1.0);
    });
  });

  describe("vocab_intro step", () => {
    it("lists every word in both languages", () => {
      renderStep({
        step_type: "vocab_intro",
        prompt: { en: "Learn these", es: "Aprende esto" },
        config: { words: [{ en: "water", es: "agua" }, { en: "thank you", es: "gracias" }] },
      });
      expect(screen.getByText("water")).toBeInTheDocument();
      expect(screen.getByText("agua")).toBeInTheDocument();
      expect(screen.getByText("thank you")).toBeInTheDocument();
      expect(screen.getByText("gracias")).toBeInTheDocument();
    });
  });

  describe("vocab_drill step", () => {
    const items = [
      { prompt: "agua", answer: "water" },
      { prompt: "gracias", answer: "thank you" },
    ];

    it("scores 1.0 when every answer matches (case-insensitive)", async () => {
      const user = userEvent.setup();
      const onComplete = renderStep({ step_type: "vocab_drill", config: { items } });

      await user.type(screen.getByPlaceholderText("Type your answer..."), "Water");
      await user.click(screen.getByRole("button", { name: "Continue" }));
      // Now on item 2
      await user.type(screen.getByPlaceholderText("Type your answer..."), "thank you");
      await user.click(screen.getByRole("button", { name: "Continue" }));

      expect(onComplete).toHaveBeenCalledOnce();
      expect(onComplete).toHaveBeenCalledWith(1.0);
    });

    it("scores 0.5 when one of two answers is wrong", async () => {
      const user = userEvent.setup();
      const onComplete = renderStep({ step_type: "vocab_drill", config: { items } });

      await user.type(screen.getByPlaceholderText("Type your answer..."), "wrong");
      await user.click(screen.getByRole("button", { name: "Continue" }));
      await user.type(screen.getByPlaceholderText("Type your answer..."), "thank you");
      await user.click(screen.getByRole("button", { name: "Continue" }));

      expect(onComplete).toHaveBeenCalledOnce();
      expect(onComplete).toHaveBeenCalledWith(0.5);
    });

    it("submits on Enter key", async () => {
      const user = userEvent.setup();
      const onComplete = renderStep({
        step_type: "vocab_drill",
        config: { items: [{ prompt: "agua", answer: "water" }] },
      });
      const input = screen.getByPlaceholderText("Type your answer...");
      await user.type(input, "water{Enter}");
      expect(onComplete).toHaveBeenCalledWith(1.0);
    });
  });

  describe("production_speaking step", () => {
    it("accepts an exact-match typed answer", async () => {
      const user = userEvent.setup();
      const onComplete = renderStep({
        step_type: "production_speaking",
        config: { target: "I would like water, please.", acceptable_variants: [] },
      });
      await user.type(
        screen.getByPlaceholderText("Type your answer..."),
        "I would like water, please.",
      );
      await user.click(screen.getByRole("button", { name: "Check" }));
      // Now in "checked" state — should show success and a Continue button
      expect(screen.getByText("Good work")).toBeInTheDocument();
      await user.click(screen.getByRole("button", { name: "Continue" }));
      expect(onComplete).toHaveBeenCalledWith(1.0);
    });

    it("accepts a listed variant as a full match", async () => {
      const user = userEvent.setup();
      const onComplete = renderStep({
        step_type: "production_speaking",
        config: { target: "Hello", acceptable_variants: ["Hi there"] },
      });
      await user.type(screen.getByPlaceholderText("Type your answer..."), "hi there");
      await user.click(screen.getByRole("button", { name: "Check" }));
      await user.click(screen.getByRole("button", { name: "Continue" }));
      expect(onComplete).toHaveBeenCalledWith(1.0);
    });

    it("partial overlap yields fractional score and shows Try again", async () => {
      const user = userEvent.setup();
      const onComplete = renderStep({
        step_type: "production_speaking",
        config: { target: "I would like water please", acceptable_variants: [] },
      });
      await user.type(screen.getByPlaceholderText("Type your answer..."), "water please");
      await user.click(screen.getByRole("button", { name: "Check" }));
      expect(screen.getAllByText("Try again").length).toBeGreaterThan(0);
      await user.click(screen.getByRole("button", { name: "Continue" }));
      // 2 of 5 words = 0.4
      expect(onComplete).toHaveBeenCalledWith(0.4);
    });
  });
});
