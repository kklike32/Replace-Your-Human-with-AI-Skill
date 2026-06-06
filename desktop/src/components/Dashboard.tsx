import type { RecorderStatus } from "../types";
import { RecordingControls } from "./RecordingControls";
import { StatusBadge } from "./StatusBadge";

type Props = {
  status: RecorderStatus;
  sessionTimer: string;
  isBusy: boolean;
  sessionId: string | null;
  syncLabel: string;
  metrics: {
    screenshots: number;
    events: number;
  };
  errorMessage: string | null;
  onStart: () => void;
  onStop: () => void;
  onPauseResume: () => void;
  onOpenSettings: () => void;
};

export function Dashboard({
  status,
  sessionTimer,
  isBusy,
  sessionId,
  syncLabel,
  metrics,
  errorMessage,
  onStart,
  onStop,
  onPauseResume,
  onOpenSettings,
}: Props) {
  return (
    <div className="space-y-6">
      <section className="rounded-[32px] border border-white/70 bg-[rgba(255,255,255,0.8)] p-6 shadow-panel backdrop-blur">
        <div className="flex flex-col gap-6">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
            <div className="max-w-3xl">
              <div className="flex flex-wrap items-center gap-3">
                <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-slate-500">
                  Workflow Tracker
                </p>
                <StatusBadge status={status} />
                <span className="rounded-full border border-slate-200 bg-white px-3 py-1 text-[11px] font-medium text-slate-500">
                  Cmd+Shift+R toggle
                </span>
              </div>
              <h1 className="mt-4 max-w-2xl text-[38px] font-semibold tracking-[-0.05em] text-slate-950">
                Record desktop workflows with a simple local-first control panel.
              </h1>
              <p className="mt-3 max-w-2xl text-[15px] leading-7 text-slate-600">
                Start and stop the Python recorder, pause when needed, and keep raw screenshots and
                input data on-device.
              </p>
            </div>

            <button
              className="rounded-full border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-900"
              onClick={onOpenSettings}
            >
              Settings
            </button>
          </div>

          <div className="grid gap-4 xl:grid-cols-[1.15fr_0.85fr]">
            <div className="rounded-[28px] border border-slate-200 bg-slate-950 px-6 py-5 text-white">
              <div className="grid gap-4 md:grid-cols-3">
                <div>
                  <div className="text-[11px] uppercase tracking-[0.26em] text-slate-400">Session timer</div>
                  <div className="mt-2 text-3xl font-semibold tracking-[-0.04em]">{sessionTimer}</div>
                </div>
                <div>
                  <div className="text-[11px] uppercase tracking-[0.26em] text-slate-400">Session ID</div>
                  <div className="mt-2 break-all text-sm leading-6 text-slate-100">{sessionId ?? "Not started"}</div>
                </div>
                <div>
                  <div className="text-[11px] uppercase tracking-[0.26em] text-slate-400">Sync status</div>
                  <div className="mt-2 text-sm leading-6 text-slate-100">{syncLabel}</div>
                </div>
              </div>
            </div>

            <div className="rounded-[28px] border border-slate-200 bg-white p-5">
              <div className="text-[11px] font-semibold uppercase tracking-[0.26em] text-slate-500">
                Session controls
              </div>
              <div className="mt-4 space-y-4">
                <RecordingControls
                  status={status}
                  isBusy={isBusy}
                  onStart={onStart}
                  onStop={onStop}
                  onPauseResume={onPauseResume}
                />
                <div className="text-xs leading-6 text-slate-500">
                  <div>{metrics.screenshots} screenshots captured</div>
                  <div>{metrics.events} local events recorded</div>
                  <div>Shortcut: Cmd+Shift+R</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {status === "idle" ? (
          <div className="mt-6 rounded-[28px] border border-slate-200 bg-slate-50/80 p-5">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <div className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-400">
                  Before you start
                </div>
                <div className="mt-2 text-lg font-semibold text-slate-900">
                  Save config, grant macOS permissions, then start a session.
                </div>
              </div>
              <div className="grid gap-2 text-sm text-slate-600">
                <div>1. Save capture and sync settings.</div>
                <div>2. Allow screen recording and accessibility access.</div>
                <div>3. Start from the button or the global shortcut.</div>
              </div>
            </div>
          </div>
        ) : null}

        <div className="mt-6 rounded-[24px] border border-slate-200 bg-slate-50/75 px-5 py-4 text-sm leading-7 text-slate-600">
          Raw screenshots, keystrokes, mouse events, and OCR text stay local. InsForge only receives
          summaries, pseudocode, workflow insights, templates, and agent handoff drafts.
        </div>

        {errorMessage ? (
          <div className="mt-6 rounded-[28px] border border-rose-200 bg-rose-50/88 p-5 text-sm text-rose-800">
            <div className="font-semibold">Recorder error</div>
            <div className="mt-2">{errorMessage}</div>
            <div className="mt-2 text-rose-700">
              Recovery suggestion: stop the session, verify `.env` values, and retry.
            </div>
          </div>
        ) : null}
      </section>
    </div>
  );
}
