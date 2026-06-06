import { invoke } from "@tauri-apps/api/core";
import type { AppSettings } from "../types";

export async function loadSettings(): Promise<AppSettings> {
  return invoke<AppSettings>("load_settings");
}

export async function saveSettings(settings: AppSettings): Promise<AppSettings> {
  return invoke<AppSettings>("save_settings", { settings });
}
