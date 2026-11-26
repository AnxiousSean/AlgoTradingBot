# AlgoTradingBot

TradeLocker Studio bot for a Goat Funded Trader 2-Step ($5,000) evaluation.

| Stage | Status | Files |
|---|---|---|
| 0. Studio capability probe | ready to paste into Studio | `probe_strategy.py` |
| 1. PropRiskGuard + tests | done (38 tests pass) | `tl_prop_bot.py`, `research/tests/` |
| 2. Strategies (RSI2, ORB) | waiting for probe results | |
| 3. Local research harness | not started | `research/` |
| 4. Studio testing guide + launch checklist | not started | |

Run the guard tests:

```bash
cd research && pip install -r requirements.txt && python -m pytest -q
```
