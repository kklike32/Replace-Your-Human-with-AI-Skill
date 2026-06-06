import type { AppSettings } from "../types";

type Props = {
  settings: AppSettings;
  isSaving: boolean;
  onChange: (next: AppSettings) => void;
  onSave: () => void;
  onClose: () => void;
};

function update<K extends keyof AppSettings>(
  settings: AppSettings,
  key: K,
  value: AppSettings[K],
): AppSettings {
  return { ...settings, [key]: value };
}

export function SettingsPanel({ settings, isSaving, onChange, onSave, onClose }: Props) {
  return (
    <section className="rounded-[32px] border border-white/70 bg-white/82 p-6 shadow-panel backdrop-blur">
      <div className="mb-8 flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-slate-500">Settings</p>
          <h2 className="mt-2 text-[30px] font-semibold tracking-[-0.04em] text-slate-950">
            Recorder and sync configuration
          </h2>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-600">
            Save demo-safe capture settings locally, then write the approved values back to `.env`
            only when you commit to them.
          </p>
        </div>
        <div className="flex gap-3">
          <button
            className="rounded-full border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-900"
            onClick={onClose}
          >
            Back
          </button>
          <button
            className="rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:bg-slate-300"
            disabled={isSaving}
            onClick={onSave}
          >
            {isSaving ? "Saving..." : "Save settings"}
          </button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-[24px] border border-slate-100 bg-slate-50/75 p-5">
          <h3 className="text-lg font-semibold text-slate-900">Capture</h3>
          <div className="mt-4 grid gap-4">
            <label className="text-sm text-slate-700">
              <span className="mb-1 block font-medium">Screenshot interval seconds</span>
              <input
                className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-slate-300 focus:ring-4 focus:ring-slate-100"
                type="number"
                min={1}
                value={settings.screenshotIntervalSeconds}
                onChange={(event) =>
                  onChange(update(settings, "screenshotIntervalSeconds", Number(event.target.value)))
                }
              />
            </label>
            <label className="text-sm text-slate-700">
              <span className="mb-1 block font-medium">Chunk interval seconds</span>
              <input
                className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-slate-300 focus:ring-4 focus:ring-slate-100"
                type="number"
                min={1}
                value={settings.chunkIntervalSeconds}
                onChange={(event) =>
                  onChange(update(settings, "chunkIntervalSeconds", Number(event.target.value)))
                }
              />
            </label>
            <label className="text-sm text-slate-700">
              <span className="mb-1 block font-medium">Raw data TTL seconds</span>
              <input
                className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-slate-300 focus:ring-4 focus:ring-slate-100"
                type="number"
                min={60}
                value={settings.rawDataTtlSeconds}
                onChange={(event) =>
                  onChange(update(settings, "rawDataTtlSeconds", Number(event.target.value)))
                }
              />
            </label>
          </div>
        </div>

        <div className="rounded-[24px] border border-slate-100 bg-slate-50/75 p-5">
          <h3 className="text-lg font-semibold text-slate-900">LLM</h3>
          <div className="mt-4 grid gap-4">
            <label className="text-sm text-slate-700">
              <span className="mb-1 block font-medium">Provider</span>
              <input
                className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-slate-300 focus:ring-4 focus:ring-slate-100"
                value={settings.llmProvider}
                onChange={(event) => onChange(update(settings, "llmProvider", event.target.value))}
              />
            </label>
            <label className="text-sm text-slate-700">
              <span className="mb-1 block font-medium">Model</span>
              <input
                className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-slate-300 focus:ring-4 focus:ring-slate-100"
                value={settings.llmModel}
                onChange={(event) => onChange(update(settings, "llmModel", event.target.value))}
              />
            </label>
            <label className="text-sm text-slate-700">
              <span className="mb-1 block font-medium">Google Cloud project</span>
              <input
                className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-slate-300 focus:ring-4 focus:ring-slate-100"
                value={settings.googleCloudProject}
                onChange={(event) =>
                  onChange(update(settings, "googleCloudProject", event.target.value))
                }
              />
            </label>
            <label className="text-sm text-slate-700">
              <span className="mb-1 block font-medium">Google Cloud location</span>
              <input
                className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-slate-300 focus:ring-4 focus:ring-slate-100"
                value={settings.googleCloudLocation}
                onChange={(event) =>
                  onChange(update(settings, "googleCloudLocation", event.target.value))
                }
              />
            </label>
          </div>
        </div>

        <div className="rounded-[24px] border border-slate-100 bg-slate-50/75 p-5">
          <h3 className="text-lg font-semibold text-slate-900">InsForge</h3>
          <div className="mt-4 grid gap-4">
            <label className="text-sm text-slate-700">
              <span className="mb-1 block font-medium">Base URL</span>
              <input
                className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-slate-300 focus:ring-4 focus:ring-slate-100"
                value={settings.insforgeBaseUrl}
                onChange={(event) => onChange(update(settings, "insforgeBaseUrl", event.target.value))}
              />
            </label>
            <label className="text-sm text-slate-700">
              <span className="mb-1 block font-medium">Project ID</span>
              <input
                className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-slate-300 focus:ring-4 focus:ring-slate-100"
                value={settings.insforgeProjectId}
                onChange={(event) =>
                  onChange(update(settings, "insforgeProjectId", event.target.value))
                }
              />
            </label>
            <label className="text-sm text-slate-700">
              <span className="mb-1 block font-medium">API key</span>
              <input
                className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-slate-300 focus:ring-4 focus:ring-slate-100"
                type="password"
                placeholder={
                  settings.hasInsforgeApiKey ? "Saved key is masked. Enter a new key to replace it." : ""
                }
                value={settings.insforgeApiKey}
                onChange={(event) => onChange(update(settings, "insforgeApiKey", event.target.value))}
              />
            </label>
            <label className="flex items-center gap-3 rounded-2xl border border-slate-100 bg-white px-4 py-3 text-sm font-medium text-slate-700">
              <input
                className="h-4 w-4 rounded border-slate-300"
                type="checkbox"
                checked={settings.cloudSyncEnabled}
                onChange={(event) =>
                  onChange(update(settings, "cloudSyncEnabled", event.target.checked))
                }
              />
              Cloud sync enabled
            </label>
          </div>
        </div>

        <div className="rounded-[24px] border border-slate-100 bg-slate-50/75 p-5">
          <h3 className="text-lg font-semibold text-slate-900">Privacy</h3>
          <div className="mt-4 grid gap-3 text-sm text-slate-700">
            <div className="rounded-2xl border border-slate-100 bg-white px-4 py-3">Upload raw screenshots: disabled by design</div>
            <div className="rounded-2xl border border-slate-100 bg-white px-4 py-3">Upload raw keyboard events: disabled by design</div>
            <div className="rounded-2xl border border-slate-100 bg-white px-4 py-3">Upload raw mouse events: disabled by design</div>
            <div className="rounded-2xl border border-slate-100 bg-white px-4 py-3">Upload OCR text: disabled by design</div>
            <div className="rounded-2xl border border-slate-100 bg-white px-4 py-3">Upload summaries only: enabled</div>
          </div>
        </div>
      </div>
    </section>
  );
}
