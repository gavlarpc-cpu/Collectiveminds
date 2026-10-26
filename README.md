# Collective Mind — 10-mind starter

This is **real model-backed reasoning orchestration**, not the previous random-discovery toy. It uses ten independent API calls to an LLM, a single shared append-only SQLite event log, and records failures as well as successes. It does **not** yet implement 16 million persistent autonomous minds, continuous exploration, a mobile UI, or genuinely instantaneous in-flight sharing. Every mind sees the same complete event history **at the start of each round**, and new results become durable immediately; other in-flight calls cannot see new results until the next round. Distinct calls have equal resources and capabilities, but independent prompts/sampling do not guarantee genuinely different ideas.

## Run (on a computer or hosted Python server)

Requires Python 3.10+, an OpenAI-compatible chat-completions API and a valid key. No extra Python packages required.

```bash
export OPENAI_API_KEY='YOUR_KEY'
python collective.py 'How could we experimentally test a new water filter design?' --rounds 2
```

Optional environment variables: `COLLECTIVE_MODEL`, `COLLECTIVE_API_URL`, `COLLECTIVE_DB`.

**Cost:** Ten model requests per round, plus their growing shared history. Check model pricing. Never commit your API key to GitHub. No automatic tool use or external experiments are implemented. Responses are hypotheses, not verified discoveries.

## Next engineering milestones

1. Add distinct persistent per-mind state and independent self-selected goals.
2. Use an event-driven shared context with real-time updates and interruption/refresh, rather than round snapshots.
3. Add bounded, sandboxed research and experiment tools with provenance and verification.
4. Expose a secured server API for the existing Android client.
5. Benchmark against independent and hybrid controls under equal compute budgets.
