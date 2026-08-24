# Coherent

**Coherent** is a spec-driven governance and orchestration layer on top of AI coding agents. It enforces architectural rigor, keeps living documentation synchronized with code changes, and provisions minimal, precision-sliced context to downstream execution agents.

## Quickstart

```bash
# 1. Install dependencies
pip install -e .

# 2. Start a governed session
coherent start "Add Stripe webhook idempotency using Redis" --files docs/rfc-01.md

# 3. Resume an existing session
coherent resume <session_id>



coherent start "calculate tax for given revenue. If revenue more than threshold tax is revenue/30 else revenue/20" --files docs/rfc-01.md
coherent resume calculate-tax-for-given--436365