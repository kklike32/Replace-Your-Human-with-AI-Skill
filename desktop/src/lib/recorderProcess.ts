import { invoke } from "@tauri-apps/api/core";
import { listen, type UnlistenFn } from "@tauri-apps/api/event";
import type { RecorderEvent } from "../types";
import { parseRecorderEvent } from "./jsonlParser";

export async function startRecorder(): Promise<void> {
  await invoke("start_recorder");
}

export async function stopRecorder(): Promise<void> {
  await invoke("stop_recorder");
}

export async function pauseRecorder(): Promise<void> {
  await invoke("pause_recorder");
}

export async function resumeRecorder(): Promise<void> {
  await invoke("resume_recorder");
}

export async function showDashboard(): Promise<void> {
  await invoke("show_dashboard");
}

export async function listenToRecorderEvents(
  handler: (event: RecorderEvent) => void,
): Promise<UnlistenFn> {
  return listen("recorder-event", (event) => {
    const parsed = parseRecorderEvent(event.payload);
    if (parsed) {
      handler(parsed);
    }
  });
}
