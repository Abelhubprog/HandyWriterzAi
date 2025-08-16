SYSTEM
Implement budgets and provider backoff without overhauling existing services.

USER
Objective:
- runtime/budgets.py should track tokens/time/$ per run and expose “allow/deny” at node boundaries.
- tools/rate_limit.py should provide exponential backoff + jitter and a simple provider portfolio (switch to next provider on repeated 429/5xx).

Constraints:
- Read price_table.json and existing services/model_selector.py if available.
- Add notes to state when budget gates or provider switches occur.

TODOs:
1) Implement budgets with simple counters and kill switch.
2) Extend core/llm.py to use rate_limit + provider fallback.

Acceptance:
- Diffs for budgets + llm + notes logging.
- Unit test showing a simulated 429 recovery and provider switch.
