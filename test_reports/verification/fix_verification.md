# Post-test fixes — 2026-11-07

- Zero balances: replaced falsy fallback with nullish fallback. Browser assertions pass for home and simulator $0.000 after withdrawal.
- Bonus display: API exposes `credited_mills`; UI counter/toast use exact credit. Two boosted charges yield +$0.023 and vault$0.023. Browser assertions pass; second toast correctly+$0.012.
- Chart initial dimensions set; radar now includes discovered topic union and a fixed0–100 domain.
- Reset tested separately: own sandbox HTTP200, discovered `{}`, browser shows “A fresh start.” Earlier600ms immediate assertion failed due response timing; response-aware wait passed.
- Insight read increment atomic predicate added. Existing concurrent12-read test passed again.
- Whitespace validation and backend topic whitelist added.
- Insight mini card radius reduced to8px; ring utility shadow collision removed.
- Amber budget-exhausted cells added to advertiser temporal grid.
- Backend regression rerun:15 passed. Optimized frontend build passed.
- Testing agent did not change app sources; only tests/reports and exact sandbox cleanup utility were added.
- The deliberate simulation boundaries remain unchanged.