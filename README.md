# 5centSUB

5centSUB aims to produce Korean subtitle files from authorized Japanese-language
video while keeping the cloud-service cost for a four-hour input at or below
US$0.05.

The current offline proof uses deterministic mock providers. It validates the
cost guard, pipeline stages, and SRT output without credentials or HTTP calls.

```powershell
python -m pytest
python -m fivecentsub demo
```

The first cloud-backed deliverable will be a small, repeatable end-to-end proof
that:

1. accepts a short authorized media sample,
2. creates a Japanese transcript,
3. translates it to Korean,
4. writes a valid SRT file, and
5. records actual cloud usage and cost.

See [the project foundation plan](docs/PROJECT_FOUNDATION.ko.md) for the
delivery order, reuse policy, and open decisions.
