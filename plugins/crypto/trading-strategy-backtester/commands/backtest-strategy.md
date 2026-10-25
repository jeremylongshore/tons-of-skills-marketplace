---
name: backtest-strategy
description: Run a historical trading simulation and report its data and metric limits.
allowed-tools: Read, Bash(python:*)
shortcut: bs
---

# Backtest Trading Strategy

Requested inputs: $ARGUMENTS

Run the shipped Python backtester. Read
`${CLAUDE_PLUGIN_ROOT}/skills/backtesting-trading-strategies/SKILL.md` for the
supported strategies, parameters, data loading and result files.

1. Parse the requested strategy, symbol, historical date range and cost
   assumptions. Ask for missing required values and check the strategy against
   the supported list. Pass validated values as quoted literal arguments; never
   interpolate raw argument text into shell code. Do not infer a future return
   target from the request.
2. Run the existing CLI with those inputs. For example, substitute the user's
   symbol and strategy in this invocation:

   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/skills/backtesting-trading-strategies/scripts/backtest.py" \
     --strategy sma_crossover --symbol BTC-USD --period 1y
   ```

   Prepare the environment described in the skill's Prerequisites section. Use `--help` for
   the supported flags; parameter optimization is a separate operation to run
   only when requested.

3. Present measured output as a historical simulation of the supplied series
   and assumptions. Include the period and number of completed trades. `N/A`
   denotes an unavailable metric, including profit factor with no observed
   losses; zero/one-trade samples do not establish strategy performance.
4. Explain that in-sample optimization and historical returns do not establish
   expected future performance. Do not substitute example figures for actual
   results or describe this simulation as a validated trading recommendation.
