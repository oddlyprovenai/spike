# SPIKE eval 20261106-142733

Model `Qwen3.5-4B-Q4_K_M.gguf`, llama.cpp `b11669-620d2225c`, greedy, thinking off, max_tokens 2048, host `macOS-27.0-arm64-arm-64bit`.

| task | variant | n | accuracy | 95% CI | Δ vs base (pts) | McNemar p | unparsed | truncated |
|---|---|---|---|---|---|---|---|---|
| finqa-test-select | base | 300 | 0.707 | 0.653–0.755 |  |  | 25 | 22 |
| finqa-test-select | spike-finance-it1200-s1 | 300 | 0.710 | 0.656–0.758 | +0.33 | 1 | 0 | 0 |
| finqa-test-select | spike-finance-it2200-s1 | 300 | 0.750 | 0.698–0.796 | +4.33 | 0.1421 | 0 | 0 |
| finqa-test-select | spike-finance-it4400-s1 | 300 | 0.770 | 0.719–0.814 | +6.33 | 0.02041 | 0 | 0 |
| finqa-test-select | spike-finance-it8825-s0.5 | 300 | 0.737 | 0.684–0.783 | +3.00 | 0.3057 | 1 | 0 |
| mmlu-pro-general-select | base | 400 | 0.632 | 0.584–0.678 |  |  | 1 | 17 |
| mmlu-pro-general-select | spike-finance-it1200-s1 | 400 | 0.532 | 0.483–0.581 | -10.00 | 7.9e-05 | 27 | 0 |
| mmlu-pro-general-select | spike-finance-it2200-s1 | 400 | 0.565 | 0.516–0.613 | -6.75 | 0.005014 | 11 | 0 |
| mmlu-pro-general-select | spike-finance-it4400-s1 | 400 | 0.565 | 0.516–0.613 | -6.75 | 0.004512 | 9 | 1 |
| mmlu-pro-general-select | spike-finance-it8825-s0.5 | 400 | 0.603 | 0.554–0.649 | -3.00 | 0.2299 | 5 | 3 |
| tatqa-test-select | base | 300 | 0.703 | 0.649–0.752 |  |  | 0 | 3 |
| tatqa-test-select | spike-finance-it1200-s1 | 300 | 0.730 | 0.677–0.777 | +2.67 | 0.3663 | 0 | 0 |
| tatqa-test-select | spike-finance-it2200-s1 | 300 | 0.743 | 0.691–0.789 | +4.00 | 0.1337 | 0 | 0 |
| tatqa-test-select | spike-finance-it4400-s1 | 300 | 0.767 | 0.716–0.811 | +6.33 | 0.01445 | 0 | 0 |
| tatqa-test-select | spike-finance-it8825-s0.5 | 300 | 0.777 | 0.726–0.820 | +7.33 | 0.002088 | 0 | 0 |
| **finance-select (pooled)** | base | 600 | 0.705 | 0.667–0.740 |  |  | 25 | 25 |
| **finance-select (pooled)** | spike-finance-it1200-s1 | 600 | 0.720 | 0.683–0.754 | +1.50 | 0.488 | 0 | 0 |
| **finance-select (pooled)** | spike-finance-it2200-s1 | 600 | 0.747 | 0.710–0.780 | +4.17 | 0.0287 | 0 | 0 |
| **finance-select (pooled)** | spike-finance-it4400-s1 | 600 | 0.768 | 0.733–0.800 | +6.33 | 0.000534 | 0 | 0 |
| **finance-select (pooled)** | spike-finance-it8825-s0.5 | 600 | 0.757 | 0.721–0.789 | +5.17 | 0.003854 | 1 | 0 |
| **general-select (pooled)** | base | 400 | 0.632 | 0.584–0.678 |  |  | 1 | 17 |
| **general-select (pooled)** | spike-finance-it1200-s1 | 400 | 0.532 | 0.483–0.581 | -10.00 | 7.9e-05 | 27 | 0 |
| **general-select (pooled)** | spike-finance-it2200-s1 | 400 | 0.565 | 0.516–0.613 | -6.75 | 0.005014 | 11 | 0 |
| **general-select (pooled)** | spike-finance-it4400-s1 | 400 | 0.565 | 0.516–0.613 | -6.75 | 0.004512 | 9 | 1 |
| **general-select (pooled)** | spike-finance-it8825-s0.5 | 400 | 0.603 | 0.554–0.649 | -3.00 | 0.2299 | 5 | 3 |
