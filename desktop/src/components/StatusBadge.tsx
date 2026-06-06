import type { RecorderStatus } from "../types";
import { Pill } from "./ui/Pill";

const statusStyles: Record<RecorderStatus, string> = {
  idle: "bg-white/90 text-muted-foreground ring-1 ring-border",
  recording: "bg-primary text-primary-foreground ring-1 ring-primary/70",
  paused: "bg-muted text-foreground ring-1 ring-border",
  summarizing: "bg-muted text-foreground ring-1 ring-border",
  syncing: "bg-accent text-accent-foreground ring-1 ring-border",
  complete: "bg-[#E8F0E5] text-[#2D4A2C] ring-1 ring-[#AEC4A3]",
  error: "bg-[#FFF0ED] text-[#7D3A33] ring-1 ring-[#E0B3AB]",
};

type Props = {
  status: RecorderStatus;
};

export function StatusBadge({ status }: Props) {
  return (
    <Pill className={statusStyles[status]}>
      {status}
    </Pill>
  );
}
