import type { RecorderStatus } from "../types";

type Props = {
  status: RecorderStatus;
  isBusy: boolean;
  onStart: () => void;
  onStop: () => void;
  onPauseResume: () => void;
};

export function RecordingControls({ status, isBusy, onStart, onStop, onPauseResume }: Props) {
  const canStart = status === "idle" || status === "complete" || status === "error";
  const isPaused = status === "paused";
  const canPause = status === "recording" || status === "summarizing" || status === "syncing" || isPaused;

  return (
    <div className="flex flex-wrap gap-3">
      <button
        className="rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:bg-slate-300"
        disabled={!canStart || isBusy}
        onClick={onStart}
      >
        Start recording
      </button>
      <button
        className="rounded-full border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-900 disabled:opacity-50"
        disabled={canStart || isBusy}
        onClick={onStop}
      >
        Stop
      </button>
      <button
        className="rounded-full border border-slate-200 bg-slate-50 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-100 disabled:opacity-50"
        disabled={!canPause || isBusy}
        onClick={onPauseResume}
      >
        {isPaused ? "Resume" : "Pause"}
      </button>
    </div>
  );
}
