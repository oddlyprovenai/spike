# Hand check of the answers M14 re-scoring changed (M16 2b)

Every prediction whose parsed letter changed between the original run and its `-rescored` copy (33: 27 in medicine `sweep/final`, 6 in finance round 2 `sweep-default/select`; finance round 2 `sweep/select` changed none). Checked by reading each answer on 2026-11-23: does the parsed letter equal the option the answer states (its final statement when it changes its mind)?

**Result: 31 of 33 match; 2 are misread** (#8, #23: both answers state the gold letter B in their first line and are scored wrong).

| # | run | task | item | variant | before | after | gold | check |
|---|---|---|---|---|---|---|---|---|
| 1 | medicine/sweep/final-rescored | medmcqa-val | 1163160d-9432-4143-98af-ef59704fc876 | base | – | C | A | ok |
| 2 | medicine/sweep/final-rescored | medmcqa-val | 51250c61-30fe-47d0-b5cf-e9ce5abcac6e | base | – | B | D | ok |
| 3 | medicine/sweep/final-rescored | medmcqa-val | 5641b32f-91e7-4a52-bd8a-a1db071d0d45 | base | – | A | B | ok |
| 4 | medicine/sweep/final-rescored | medmcqa-val | 5c578aa4-a6fd-4de5-b0f6-adb926564122 | base | – | B | A | ok |
| 5 | medicine/sweep/final-rescored | medmcqa-val | 6fd1e538-3654-423e-9803-83f850493c22 | base | A | D | A | ok (truncated at max_tokens; opens with **D**) |
| 6 | medicine/sweep/final-rescored | medmcqa-val | 98893c1c-a979-476e-8b82-ef3bd2a02da7 | base | – | D | A | ok |
| 7 | medicine/sweep/final-rescored | medmcqa-val | a02c508f-6cf6-4699-b134-e50fd2d84fee | base | D | C | D | ok (truncated at max_tokens; opens with **C**) |
| 8 | medicine/sweep/final-rescored | medmcqa-val | b3aa72de-f85c-407f-892b-9dae7d953417 | base | – | A | B | **misread: the answer opens with **B** and concludes Linezolid (B); the extractor read "Rifampicin (A):" from a per-option bullet** |
| 9 | medicine/sweep/final-rescored | medmcqa-val | f5b89559-4ce3-4dd5-b950-5624eb6f4ca8 | base | – | D | A | ok |
| 10 | medicine/sweep/final-rescored | mmlu-pro-health | 6001 | base | – | E | E | ok (opens with **F**, ends "Final Answer Selection: E": the final statement is E) |
| 11 | medicine/sweep/final-rescored | mmlu-pro-health | 6146 | base | – | D | J | ok |
| 12 | medicine/sweep/final-rescored | mmlu-pro-health | 6179 | base | – | E | E | ok |
| 13 | medicine/sweep/final-rescored | mmlu-pro-health | 6314 | base | – | J | J | ok |
| 14 | medicine/sweep/final-rescored | mmlu-pro-health | 6374 | base | – | G | G | ok |
| 15 | medicine/sweep/final-rescored | mmlu-pro-health | 6467 | base | – | B | B | ok |
| 16 | medicine/sweep/final-rescored | mmlu-pro-health | 6474 | base | E | D | D | ok (opens "Answer: E", ends "Final Answer Selection: D": the final statement is D) |
| 17 | medicine/sweep/final-rescored | mmlu-pro-health | 6502 | base | – | C | G | ok |
| 18 | medicine/sweep/final-rescored | mmlu-pro-health | 6516 | base | G | B | B | ok |
| 19 | medicine/sweep/final-rescored | mmlu-pro-health | 6522 | base | J | F | F | ok |
| 20 | medicine/sweep/final-rescored | mmlu-pro-health | 6568 | base | – | F | F | ok |
| 21 | medicine/sweep/final-rescored | mmlu-pro-health | 6586 | base | B | C | C | ok |
| 22 | medicine/sweep/final-rescored | mmlu-pro-health | 6628 | base | – | D | D | ok |
| 23 | medicine/sweep/final-rescored | mmlu-pro-health | 6636 | base | – | C | B | **misread: the answer opens with **B** and argues B is the incorrect statement; the extractor read "(Option C is correct)" from the justification** |
| 24 | medicine/sweep/final-rescored | mmlu-pro-health | 6701 | base | A | I | I | ok (opens "Answer: A", ends "Final Answer Selection: I": the final statement is I) |
| 25 | medicine/sweep/final-rescored | mmlu-pro-health | 6722 | base | – | B | B | ok |
| 26 | medicine/sweep/final-rescored | mmlu-pro-health | 6723 | base | – | J | A | ok |
| 27 | medicine/sweep/final-rescored | mmlu-pro-health | 6742 | base | H | I | I | ok |
| 28 | finance/round2/sweep-default/select-rescored | mmlu-pro-general-select | 10951 | spike-finance-it2600-s1 | – | I | A | ok (the whole answer is option I's text) |
| 29 | finance/round2/sweep-default/select-rescored | mmlu-pro-general-select | 2190 | spike-finance-it2600-s1 | – | A | F | ok (the whole answer is option A's text) |
| 30 | finance/round2/sweep-default/select-rescored | mmlu-pro-general-select | 2555 | spike-finance-it2600-s1 | – | A | A | ok (the whole answer is option A's text) |
| 31 | finance/round2/sweep-default/select-rescored | mmlu-pro-general-select | 5351 | spike-finance-it2600-s1 | – | A | F | ok (the whole answer is option A's text) |
| 32 | finance/round2/sweep-default/select-rescored | mmlu-pro-general-select | 5852 | spike-finance-it2600-s1 | – | I | B | ok (the whole answer is option I's text) |
| 33 | finance/round2/sweep-default/select-rescored | mmlu-pro-general-select | 5351 | spike-finance-it10000-s1 | – | A | F | ok (the whole answer is option A's text) |
