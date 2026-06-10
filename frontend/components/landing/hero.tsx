import { ConceptGraph } from "./concept_graph";

export function Hero() {
  return (
    <section className="p-8 pl-15">
      <div className="mb-8 flex justify-end">
        <button className="flex items-center gap-2 rounded-xl border border-white/10 bg-[#0f1320] px-4 py-2 text-sm">
          <span className="text-green-500 leading-none">●</span>
          <span>Gemini</span>
        </button>
      </div>

      <div className="grid gap-8 xl:grid-cols-[1fr_700px]">
        <div>
          <div className="mb-6 inline-flex rounded-full border border-violet-500/20 bg-violet-500/5 px-4 py-2 text-xs font-medium tracking-wider text-violet-300">
            LOCAL AI • MEMORY-DRIVEN • PRIVATE
          </div>

          <h1 className="max-w-3xl text-7xl font-black leading-[0.95] tracking-tight">
            Your AI tutor that
            <br />

            <span className="bg-gradient-to-r from-violet-400 via-fuchsia-400 to-violet-500 bg-clip-text text-transparent">
              remembers
            </span>
            <span className="bg-gradient-to-r from-violet-400 via-fuchsia-400 to-violet-500 bg-clip-text text-transparent italic px-2">
              how
            </span>

            <br />
            you think
          </h1>

          <p className="mt-8 max-w-xl text-xl text-zinc-400">
            Recursive is a local AI study
            copilot for CS and STEM learners.
            It tracks your concepts, learns
            your patterns, and builds a
            personal knowledge graph.
          </p>

          <div className="mt-10 flex gap-4">
            <button className="rounded-xl bg-violet-600 px-8 py-4 font-medium shadow-xl shadow-violet-900/40">
              Start Learning →
            </button>

            <button className="rounded-xl border border-white/10 bg-[#101522] px-8 py-4 font-medium">
              See it in action →
            </button>
          </div>

          <div className="mt-14 grid max-w-xl grid-cols-3 gap-6">
            <div>
              <div className="text-3xl font-bold text-violet-400">
                100%
              </div>

              <div className="mt-1 text-sm text-zinc-500">
                Local & private
              </div>
            </div>

            <div>
              <div className="text-3xl font-bold text-violet-400">
                ∞
              </div>

              <div className="mt-1 text-sm text-zinc-500">
                Memory
                persistence
              </div>
            </div>

            <div>
              <div className="text-3xl font-bold text-violet-400">
                3+
              </div>

              <div className="mt-1 text-sm text-zinc-500">
                STEM
                disciplines
              </div>
            </div>
          </div>
        </div>

        <ConceptGraph />
      </div>
    </section>
  );
}