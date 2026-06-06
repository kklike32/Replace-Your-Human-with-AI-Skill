import type { ChunkSummary } from "../types";

type Props = {
  chunks: ChunkSummary[];
};

export function ChunkSummaryList({ chunks }: Props) {
  return (
    <section className="rounded-[28px] border border-white/70 bg-white/80 p-6 shadow-panel backdrop-blur">
      <div className="mb-6 flex items-end justify-between gap-4">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-slate-500">
            Chunk Summaries
          </p>
          <h2 className="mt-2 text-[24px] font-semibold tracking-[-0.03em] text-slate-950">
            6-second workflow slices
          </h2>
        </div>
        <div className="rounded-full border border-slate-200 bg-white/80 px-3 py-1 text-xs font-medium text-slate-500">
          {chunks.length} chunks
        </div>
      </div>
      <div className="space-y-4">
        {chunks.length === 0 ? (
          <div className="rounded-[24px] border border-dashed border-slate-200 bg-slate-50 p-6 text-sm text-slate-500">
            Recording will stream privacy-safe chunk summaries here as Gemini finishes each 6-second slice.
          </div>
        ) : (
          chunks.map((chunk) => (
            <article
              key={chunk.chunkIndex}
              className="rounded-[24px] border border-slate-100 bg-slate-50/65 px-5 py-5"
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <div className="text-[11px] uppercase tracking-[0.26em] text-slate-400">
                    Chunk {chunk.chunkIndex + 1}
                  </div>
                  <div className="mt-2 text-sm font-medium text-slate-700">
                    {new Date(chunk.startedAt).toLocaleTimeString()} to{" "}
                    {new Date(chunk.endedAt).toLocaleTimeString()}
                  </div>
                </div>
                <div className="flex flex-wrap gap-2">
                  <span className="rounded-full border border-slate-200 bg-white px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-600">
                    {chunk.confidence}
                  </span>
                  <span className="rounded-full border border-slate-200 bg-white px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-600">
                    {chunk.syncStatus}
                  </span>
                </div>
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                {chunk.observedApps.map((app) => (
                  <span
                    key={`${chunk.chunkIndex}-${app}`}
                    className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-600"
                  >
                    {app}
                  </span>
                ))}
              </div>
              <p className="mt-4 text-sm leading-7 text-slate-700">{chunk.summary}</p>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
