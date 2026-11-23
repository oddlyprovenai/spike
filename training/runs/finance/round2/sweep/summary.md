# Checkpoint sweep: finance

Recipe `training/configs/finance.yaml`, trained at commit `fc6273925567d01838c74db258db679eb0a2dcb0` for 20063 iterations. Chosen on `finance-select, general-select` (the recipe's rule with the suites renamed), measured against the base model in one run (`training/runs/finance/sweep/select`).

| candidate | asked | iteration | scale | finance-select Δ pts (p) | general-select Δ pts | passes |
|---|---|---|---|---|---|---|
| spike-finance-it20063-s0.25 | 1@0.25 | 20063 | 0.25 | +3.67 (0.01685) | -3.75 | no |
| spike-finance-it20063-s0.35 | 1@0.35 | 20063 | 0.35 | +5.50 (0.000378) | -5.00 | no |
| spike-finance-it10000-s0.5 | 0.5@0.5 | 10000 | 0.5 | +6.17 (0.00057) | -5.25 | no |

Chosen: none, no candidate passed.
- spike-finance-it20063-s0.25: finance-select: +3.67 pts (need ≥ 3.0), p = 0.01685 (need ≤ 0.05); general-select: -3.75 pts (max drop 1.5)
- spike-finance-it20063-s0.35: finance-select: +5.50 pts (need ≥ 3.0), p = 0.000378 (need ≤ 0.05); general-select: -5.00 pts (max drop 1.5)
- spike-finance-it10000-s0.5: finance-select: +6.17 pts (need ≥ 3.0), p = 0.00057 (need ≤ 0.05); general-select: -5.25 pts (max drop 1.5)
