import type { ChunkSummary } from "../types";
import { CardSurface } from "./ui/CardSurface";
import { Pill } from "./ui/Pill";
import { SectionEyebrow, SectionTitle } from "./ui/Typography";

type Props = {
  chunks: ChunkSummary[];
};

export function ChunkSummaryList({ chunks }: Props) {
  return (
    <section className="organic-surface rounded-[2rem] rounded-bl-[3.25rem] p-6">
      <div className="mb-6 flex items-end justify-between gap-4">
        <div>
          <SectionEyebrow>Chunk Summaries</SectionEyebrow>
          <SectionTitle>6-second workflow slices</SectionTitle>
        </div>
        <Pill tone="outline" uppercase={false} className="text-xs">{chunks.length} chunks</Pill>
      </div>
      <div className="space-y-4">
        {chunks.length === 0 ? (
          <CardSurface className="rounded-[1.7rem] border-dashed p-6 text-sm text-muted-foreground" tone="muted">
            Recording will stream privacy-safe chunk summaries here as Gemini finishes each 6-second slice.
          </CardSurface>
        ) : (
          chunks.map((chunk) => (
            <CardSurface
              key={chunk.chunkIndex}
              className="rounded-[1.7rem] px-5 py-5"
              interactive
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <div className="text-[11px] uppercase tracking-[0.26em] text-muted-foreground">
                    Chunk {chunk.chunkIndex + 1}
                  </div>
                  <div className="mt-2 text-sm font-medium text-foreground">
                    {new Date(chunk.startedAt).toLocaleTimeString()} to{" "}
                    {new Date(chunk.endedAt).toLocaleTimeString()}
                  </div>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Pill tone="muted" size="xs">{chunk.confidence}</Pill>
                  <Pill tone="muted" size="xs">{chunk.syncStatus}</Pill>
                </div>
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                {chunk.observedApps.map((app) => (
                  <span
                    key={`${chunk.chunkIndex}-${app}`}
                    className="rounded-full border border-border/70 bg-accent/35 px-3 py-1 text-xs font-semibold text-accent-foreground"
                  >
                    {app}
                  </span>
                ))}
              </div>
              <p className="mt-4 text-sm leading-7 text-accent-foreground">{chunk.summary}</p>
            </CardSurface>
          ))
        )}
      </div>
    </section>
  );
}
