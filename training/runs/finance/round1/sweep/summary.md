# Checkpoint sweep: finance

Recipe `training/configs/finance.yaml`, trained at commit `58eb44913e2e5759d2907098c647b011d3837735` for 8825 iterations. Chosen on `finance-select, general-select` (the recipe's rule with the suites renamed), measured against the base model in one run (`training/runs/finance/sweep/select`).

| candidate | asked | iteration | scale | finance-select Δ pts (p) | general-select Δ pts | passes |
|---|---|---|---|---|---|---|
| spike-finance-it8825-s0.25 | 1@0.25 | 8825 | 0.25 | +1.67 (0.2954) | -5.50 | no |
| spike-finance-it8825-s0.35 | 1@0.35 | 8825 | 0.35 | +4.00 (0.01163) | -4.50 | no |
| spike-finance-it4400-s0.5 | 0.5@0.5 | 4400 | 0.5 | +3.67 (0.05682) | -5.50 | no |

Chosen: none, no candidate passed.
- spike-finance-it8825-s0.25: finance-select: +1.67 pts (need ≥ 3.0), p = 0.2954 (need ≤ 0.05); general-select: -5.50 pts (max drop 1.5)
- spike-finance-it8825-s0.35: finance-select: +4.00 pts (need ≥ 3.0), p = 0.01163 (need ≤ 0.05); general-select: -4.50 pts (max drop 1.5)
- spike-finance-it4400-s0.5: finance-select: +3.67 pts (need ≥ 3.0), p = 0.05682 (need ≤ 0.05); general-select: -5.50 pts (max drop 1.5)
