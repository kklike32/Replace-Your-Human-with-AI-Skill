export function PrivacyPanel() {
  return (
    <section className="rounded-[28px] border border-white/70 bg-white/82 p-6 shadow-panel backdrop-blur">
      <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-slate-500">Privacy first</p>
      <p className="mt-3 text-sm leading-7 text-slate-900">
        Raw screenshots, keystrokes, mouse events, and OCR text stay local. InsForge only receives
        summaries, pseudocode, workflow insights, templates, and agent handoff drafts.
      </p>
      <div className="mt-5 grid gap-2 text-sm text-slate-700">
        <div className="rounded-2xl border border-slate-100 bg-slate-50/70 px-4 py-3">Upload raw screenshots: disabled by design</div>
        <div className="rounded-2xl border border-slate-100 bg-slate-50/70 px-4 py-3">Upload raw keyboard events: disabled by design</div>
        <div className="rounded-2xl border border-slate-100 bg-slate-50/70 px-4 py-3">Upload raw mouse events: disabled by design</div>
        <div className="rounded-2xl border border-slate-100 bg-slate-50/70 px-4 py-3">Upload OCR text: disabled by design</div>
        <div className="rounded-2xl border border-slate-100 bg-slate-50/70 px-4 py-3">Upload summaries only: enabled</div>
      </div>
    </section>
  );
}
