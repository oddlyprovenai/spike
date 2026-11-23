# Checkpoint sweep: finance

Recipe `training/configs/finance.yaml`, trained at commit `58eb44913e2e5759d2907098c647b011d3837735` for 8825 iterations. Chosen on `finance-select, general-select` (the recipe's rule with the suites renamed), measured against the base model in one run (`training/runs/finance/sweep/select`).

| candidate | asked | iteration | scale | finance-select Δ pts (p) | general-select Δ pts | passes |
|---|---|---|---|---|---|---|
| spike-finance-it1200-s1 | 0.125 | 1200 | 1 | +1.50 (0.488) | -10.00 | no |
| spike-finance-it2200-s1 | 0.25 | 2200 | 1 | +4.17 (0.0287) | -6.75 | no |
| spike-finance-it4400-s1 | 0.5 | 4400 | 1 | +6.33 (0.000534) | -6.75 | no |
| spike-finance-it8825-s0.5 | 1@0.5 | 8825 | 0.5 | +5.17 (0.003854) | -3.00 | no |

Chosen: none, no candidate passed.
- spike-finance-it1200-s1: finance-select: +1.50 pts (need ≥ 3.0), p = 0.488 (need ≤ 0.05); general-select: -10.00 pts (max drop 1.5)
- spike-finance-it2200-s1: finance-select: +4.17 pts (need ≥ 3.0), p = 0.0287 (need ≤ 0.05); general-select: -6.75 pts (max drop 1.5)
- spike-finance-it4400-s1: finance-select: +6.33 pts (need ≥ 3.0), p = 0.000534 (need ≤ 0.05); general-select: -6.75 pts (max drop 1.5)
- spike-finance-it8825-s0.5: finance-select: +5.17 pts (need ≥ 3.0), p = 0.003854 (need ≤ 0.05); general-select: -3.00 pts (max drop 1.5)
