import type { FinalWorkflow } from "../types";

type Props = {
  workflow: FinalWorkflow;
};

export function FinalWorkflowPanel({ workflow }: Props) {
  return (
    <section className="rounded-[28px] border border-white/70 bg-white/82 p-6 shadow-panel backdrop-blur">
      <div className="mb-6">
        <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-slate-500">
          Final Workflow
        </p>
        <h2 className="mt-2 text-[24px] font-semibold tracking-[-0.03em] text-slate-950">
          Pseudocode and next action
        </h2>
      </div>

      {workflow.pseudocode.length === 0 ? (
        <div className="rounded-[24px] border border-dashed border-slate-200 bg-slate-50 p-6 text-sm text-slate-500">
          Final pseudocode will appear after the recorder stops, chunk summaries finish, and workflow insights are generated.
        </div>
      ) : (
        <>
          <ol className="space-y-3 text-sm leading-6 text-slate-700">
            {workflow.pseudocode.map((step, index) => (
              <li
                key={`${index}-${step}`}
                className="flex gap-3 rounded-[20px] border border-slate-100 bg-slate-50/55 px-4 py-4"
              >
                <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-slate-950 text-xs font-semibold text-white">
                  {index + 1}
                </span>
                <span>{step.replace(/^Step \d+\.\s*/, "")}</span>
              </li>
            ))}
          </ol>

          <div className="mt-5 grid gap-3">
            <div className="rounded-[20px] bg-slate-950 px-4 py-4 text-white">
              <div className="text-[11px] uppercase tracking-[0.24em] text-slate-300">Automation score</div>
              <div className="mt-2 text-3xl font-semibold">{workflow.automationScore ?? "--"}</div>
            </div>
            <div className="rounded-[20px] border border-slate-100 bg-slate-50/55 px-4 py-4 text-sm text-slate-700">
              <div className="text-[11px] uppercase tracking-[0.24em] text-slate-400">Recommended next action</div>
              <div className="mt-2 font-medium text-slate-900">
                {workflow.recommendedNextAction ?? "Pending workflow insight generation."}
              </div>
            </div>
            <div className="rounded-[20px] border border-slate-100 bg-slate-50/55 px-4 py-4 text-sm text-slate-700">
              <div className="text-[11px] uppercase tracking-[0.24em] text-slate-400">Workflow template</div>
              <div className="mt-2 font-medium text-slate-900">
                {workflow.templateTitle ?? "Not created yet"}
              </div>
            </div>
            <div className="rounded-[20px] border border-slate-100 bg-slate-50/55 px-4 py-4 text-sm text-slate-700">
              <div className="text-[11px] uppercase tracking-[0.24em] text-slate-400">Agent handoff</div>
              <div className="mt-2 font-medium text-slate-900">
                {workflow.agentHandoffStatus ?? "No draft available yet"}
              </div>
            </div>
          </div>
        </>
      )}
    </section>
  );
}
