# Checkpoint sweep: finance

Recipe `training/configs/finance.yaml`, trained at commit `fc6273925567d01838c74db258db679eb0a2dcb0` for 20063 iterations. Chosen on `finance-select, general-select` (the recipe's rule with the suites renamed), measured against the base model in one run (`training/runs/finance/sweep/select`).

| candidate | asked | iteration | scale | finance-select Δ pts (p) | general-select Δ pts | passes |
|---|---|---|---|---|---|---|
| spike-finance-it2600-s1 | 0.125 | 2600 | 1 | +4.67 (0.01582) | -12.50 | no |
| spike-finance-it5000-s1 | 0.25 | 5000 | 1 | +6.00 (0.002194) | -7.75 | no |
| spike-finance-it10000-s1 | 0.5 | 10000 | 1 | +4.00 (0.05321) | -10.25 | no |
| spike-finance-it20063-s0.5 | 1@0.5 | 20063 | 0.5 | +7.00 (3.9e-05) | -2.75 | no |

Chosen: none, no candidate passed.
- spike-finance-it2600-s1: finance-select: +4.67 pts (need ≥ 3.0), p = 0.01582 (need ≤ 0.05); general-select: -12.50 pts (max drop 1.5)
- spike-finance-it5000-s1: finance-select: +6.00 pts (need ≥ 3.0), p = 0.002194 (need ≤ 0.05); general-select: -7.75 pts (max drop 1.5)
- spike-finance-it10000-s1: finance-select: +4.00 pts (need ≥ 3.0), p = 0.05321 (need ≤ 0.05); general-select: -10.25 pts (max drop 1.5)
- spike-finance-it20063-s0.5: finance-select: +7.00 pts (need ≥ 3.0), p = 3.9e-05 (need ≤ 0.05); general-select: -2.75 pts (max drop 1.5)
