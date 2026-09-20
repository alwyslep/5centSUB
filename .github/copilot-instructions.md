# Copilot Instructions

## Commands

```powershell
python -m pytest
python -m pytest tests/test_pipeline.py::test_mock_pipeline_produces_valid_korean_srt
python -m fivecentsub demo
python -m fivecentsub validate-srt path\to\subtitle.srt
python -m fivecentsub estimate --source-seconds 14400 --speech-seconds 7200 --audio-tokens-per-second 25 --asr-input-usd-per-million 0.15 --asr-output-tokens 42000 --asr-output-usd-per-million 1.25 --translation-input-tokens 42000 --translation-input-usd-per-million 0.15 --translation-output-tokens 42000 --translation-output-usd-per-million 1.25
python -m fivecentsub prepare-audio input.mp4 output.flac --dry-run
```

`demo` is intentionally offline: it uses deterministic mock providers and must
not require credentials or make HTTP requests.

## Architecture and conventions

- `fivecentsub.pipeline` owns stage transitions and coordinates transcript and translation providers.
- Providers implement small protocol interfaces. Concrete cloud clients will be added behind those interfaces; tests use `MockTranscriptProvider` and `MockTranslationProvider`.
- All provider estimates must be authorized by `BudgetLedger` before a request begins. Actual charges are recorded separately; a charge over the budget changes the job to `FAILED`.
- `fivecentsub.srt` is the single strict SRT parser. It rejects malformed timestamps, empty cue text, non-sequential cue numbers, non-positive durations, and overlaps.
- `fivecentsub.estimation` accepts measured durations, tokens, and current provider rates; it must not embed time-sensitive provider pricing.
- `fivecentsub.media` builds the one canonical FFmpeg command for local non-ML audio preparation. `prepare-audio --dry-run` never invokes FFmpeg.
- Keep the implementation cloud-only with no local ML or GPU inference. Local non-ML media preparation, such as FFmpeg audio extraction, is permitted before cloud requests.

## Reuse and publishing boundary

- Use the existing WhisperJAV-Cloud, javstt-cloud, and javtrans projects as behavioral references and sources of independently verified requirements; do not copy their code into this public repository until its authorship, license, and required notices are documented.
- Do not import code or derived assets from pyvideotrans: its bundled license is GPLv3, which is incompatible with treating this repository as independently licensed without satisfying GPL obligations.
- Never commit API keys, credentials, source media, extracted audio, generated subtitles, cloud request/response logs, or usage records. Keep fixtures synthetic or explicitly redistributable.
- Preserve the `master` branch as a runnable, reviewed baseline. Use task branches and pull requests for changes after this documentation foundation.

## Project documents

- `README.md` defines the externally visible purpose and present scope.
- `docs/PROJECT_FOUNDATION.ko.md` is the decision log and phased delivery plan. Update it when a provider, cost formula, or processing boundary is selected.
- `docs/PROVIDER_RESEARCH.ko.md` records time-sensitive provider pricing and policy evidence. Reconfirm every cited rate and policy before implementing a concrete provider.


<!-- graft:start -->
## Graft — repo context graph

This repo is indexed in `graft/`: small linked markdown nodes that explain each
system and carry exact file:line spans, kept in sync with the code through git.

For ANY task here — understanding how something works, finding where code lives,
or scoping a change — get context from the graph before grepping or opening
source files. Re-ask freely (it's cheap) and reuse literal identifiers you
already have (symbol, error string, file name) as the query. New to this repo?
Run `graft map` first — a token-budgeted orientation (dir clusters, hubs,
hotspots), no LLM, no key.

- Run `graft ask "<your question>" --source` → ranked nodes with the relevant
  code spans inlined (each hit's ≤8-line crux by default; `--full` for whole
  definitions when the crux isn't enough). Match the tool to the task shape:
  for understanding or editing, the top node IS the answer — cite its
  `covers:` file:line spans and edit straight from `--source`. For
  exhaustive tasks ("every occurrence / every caller of this pattern"), ranked
  results are top-N, not complete — run `graft grep "<literal>"` instead
  (exhaustive over indexed files, grouped by enclosing symbol), falling back
  to raw `grep -rn` only for unindexed files.
- `graft skeleton <file>` → every definition's signature + span, ~10× cheaper
  than reading the file; use it to skim an API surface.
- `graft callers <symbol>` gives precomputed, exact edges — who calls this.
  Add `--direction out` for what it calls, or `--depth N` to walk
  transitively for the full blast radius. For structural questions, skip
  ranking and use this directly.
- Or browse: `graft/INDEX.md` lists every node; follow the links.
- Monorepos and folders of multiple repos rank fairly across sub-projects —
  hits carry `[scope/]` labels naming which one they're from. Narrow with
  `graft ask "<task>" --in <scope>/` once you know where you're working.

If a returned span is truncated ("+N more lines"), open the file at that exact
range before finalizing. Only open source files when a node genuinely lacks a
needed detail, and then at the exact file:line the node points to — never
re-read whole files.

After big code changes, refresh the graph with `graft build` (deterministic,
no API key, $0).
<!-- graft:end -->
