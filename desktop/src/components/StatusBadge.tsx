import type { RecorderStatus } from "../types";

const statusStyles: Record<RecorderStatus, string> = {
  idle: "bg-white text-slate-700 ring-1 ring-slate-200",
  recording: "bg-slate-900 text-white ring-1 ring-slate-900",
  paused: "bg-slate-100 text-slate-800 ring-1 ring-slate-200",
  summarizing: "bg-slate-100 text-slate-800 ring-1 ring-slate-200",
  syncing: "bg-slate-100 text-slate-800 ring-1 ring-slate-200",
  complete: "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-100",
  error: "bg-rose-50 text-rose-700 ring-1 ring-rose-100",
};

type Props = {
  status: RecorderStatus;
};

export function StatusBadge({ status }: Props) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.22em] ${statusStyles[status]}`}
    >
      {status}
    </span>
  );
}
