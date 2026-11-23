# Checkpoint sweep: finance

Recipe `training/configs/finance.yaml`, trained at commit `7a1559c652b59dd867127a0486945eddac09f44c` for 13375 iterations. Chosen on `finance-select, general-select` (the recipe's rule with the suites renamed), measured against the base model in one run (`training/runs/finance/sweep/select`).

| candidate | asked | iteration | scale | finance-select Δ pts (p) | general-select Δ pts | passes |
|---|---|---|---|---|---|---|
| spike-finance-it1600-s1 | 0.125 | 1600 | 1 | +0.33 (0.9302) | -8.75 | no |
| spike-finance-it3400-s1 | 0.25 | 3400 | 1 | +2.17 (0.2981) | -8.50 | no |
| spike-finance-it6600-s1 | 0.5 | 6600 | 1 | +5.67 (0.004188) | -8.25 | no |
| spike-finance-it13375-s0.5 | 1@0.5 | 13375 | 0.5 | +6.83 (7.8e-05) | -6.00 | no |

Chosen: none, no candidate passed.
- spike-finance-it1600-s1: finance-select: +0.33 pts (need ≥ 3.0), p = 0.9302 (need ≤ 0.05); general-select: -8.75 pts (max drop 1.5)
- spike-finance-it3400-s1: finance-select: +2.17 pts (need ≥ 3.0), p = 0.2981 (need ≤ 0.05); general-select: -8.50 pts (max drop 1.5)
- spike-finance-it6600-s1: finance-select: +5.67 pts (need ≥ 3.0), p = 0.004188 (need ≤ 0.05); general-select: -8.25 pts (max drop 1.5)
- spike-finance-it13375-s0.5: finance-select: +6.83 pts (need ≥ 3.0), p = 7.8e-05 (need ≤ 0.05); general-select: -6.00 pts (max drop 1.5)
