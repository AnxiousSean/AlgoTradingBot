# AlgoTradingBot

TradeLocker Studio bot for a Goat Funded Trader 2-Step ($5,000) evaluation.

| Stage | Status | Files |
|---|---|---|
| 0. Studio capability probe | done | `probe_strategy.py`, `STUDIO_PROBE_RESULTS.md` |
| 1. PropRiskGuard + tests | done | `tl_prop_bot.py`, `research/tests/test_prop_risk_guard.py` |
| 2. Strategies (RSI2, ORB) in the bot | done, mechanical checks pass; first Studio run pending | `tl_prop_bot.py`, `research/tests/test_strategy_smoke.py` |
| 3. Local research harness | not started | `research/` |
| 4. Studio testing guide + launch checklist | not started | |

Run the guard tests:

```bash
cd research && pip install -r requirements.txt && python -m pytest -q
```
