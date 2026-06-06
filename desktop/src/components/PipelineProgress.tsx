import type { PipelineStep } from "../types";

type Props = {
  steps: PipelineStep[];
  metrics: {
    screenshots: number;
    events: number;
    syncLabel: string;
  };
};

export function PipelineProgress({ steps, metrics }: Props) {
  return (
    <section className="rounded-[28px] border border-white/70 bg-white/80 p-6 shadow-panel backdrop-blur">
      <div className="mb-6 flex items-start justify-between gap-4">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-slate-500">
            Live Pipeline
          </p>
          <h2 className="mt-2 text-[24px] font-semibold tracking-[-0.03em] text-slate-950">
            Capture to workflow intelligence
          </h2>
        </div>
        <div className="rounded-[20px] border border-slate-200 bg-slate-50 px-4 py-3 text-right text-xs text-slate-600">
          <div>{metrics.screenshots} screenshots</div>
          <div>{metrics.events} local events</div>
          <div className="max-w-[12rem] text-slate-500">{metrics.syncLabel}</div>
        </div>
      </div>
      <div className="space-y-3">
        {steps.map((step, index) => (
          <div key={step.id} className="flex gap-4 rounded-[22px] border border-slate-100 bg-slate-50/55 px-4 py-4">
            <div className="flex flex-col items-center">
              <div
                className={`mt-1 flex h-10 w-10 items-center justify-center rounded-full text-sm font-semibold ${
                  step.state === "complete"
                    ? "bg-slate-900 text-white"
                    : step.state === "active"
                      ? "bg-slate-700 text-white"
                      : step.state === "error"
                        ? "bg-rose-500 text-white"
                        : "bg-slate-200 text-slate-600"
                }`}
              >
                {index + 1}
              </div>
              {index < steps.length - 1 ? <div className="mt-2 h-full w-px bg-slate-200/80" /> : null}
            </div>
            <div className="min-w-0 pb-1">
              <div className="flex flex-wrap items-center gap-2">
                <p className="text-sm font-semibold text-slate-900">{step.label}</p>
                <span className="rounded-full bg-slate-100 px-2 py-1 text-[10px] uppercase tracking-[0.22em] text-slate-500">
                  {step.state}
                </span>
              </div>
              <p className="mt-1 text-sm leading-6 text-slate-600">{step.description}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
