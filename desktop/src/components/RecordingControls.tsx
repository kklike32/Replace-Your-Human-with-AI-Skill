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
        className="btn-organic-primary px-6 text-sm"
        disabled={!canStart || isBusy}
        onClick={onStart}
      >
        Start recording
      </button>
      <button
        className="btn-organic-outline px-6 text-sm"
        disabled={canStart || isBusy}
        onClick={onStop}
      >
        Stop
      </button>
      <button
        className="btn-organic-ghost border border-border bg-white/40 px-6 text-sm"
        disabled={!canPause || isBusy}
        onClick={onPauseResume}
      >
        {isPaused ? "Resume" : "Pause"}
      </button>
    </div>
  );
}
