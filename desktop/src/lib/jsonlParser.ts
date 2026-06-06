import type { RecorderEvent } from "../types";

export function parseRecorderEvent(payload: unknown): RecorderEvent | null {
  if (typeof payload === "string") {
    try {
      return parseRecorderEvent(JSON.parse(payload));
    } catch {
      return null;
    }
  }

  if (!payload || typeof payload !== "object" || !("type" in payload)) {
    return null;
  }

  return payload as RecorderEvent;
}
