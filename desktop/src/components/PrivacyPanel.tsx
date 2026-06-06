import { CardSurface } from "./ui/CardSurface";
import { SectionEyebrow } from "./ui/Typography";

export function PrivacyPanel() {
  return (
    <section className="organic-surface rounded-[2rem] p-6">
      <SectionEyebrow>Privacy first</SectionEyebrow>
      <p className="mt-3 text-sm leading-7 text-foreground">
        Raw screenshots, keystrokes, mouse events, and OCR text stay local. InsForge only receives
        summaries, pseudocode, workflow insights, templates, and agent handoff drafts.
      </p>
      <div className="mt-5 grid gap-2 text-sm text-accent-foreground">
        <CardSurface className="rounded-[1.2rem] px-4 py-3" tone="muted">Upload raw screenshots: disabled by design</CardSurface>
        <CardSurface className="rounded-[1.2rem] px-4 py-3" tone="muted">Upload raw keyboard events: disabled by design</CardSurface>
        <CardSurface className="rounded-[1.2rem] px-4 py-3" tone="muted">Upload raw mouse events: disabled by design</CardSurface>
        <CardSurface className="rounded-[1.2rem] px-4 py-3" tone="muted">Upload OCR text: disabled by design</CardSurface>
        <CardSurface className="rounded-[1.2rem] px-4 py-3" tone="muted">Upload summaries only: enabled</CardSurface>
      </div>
    </section>
  );
}
