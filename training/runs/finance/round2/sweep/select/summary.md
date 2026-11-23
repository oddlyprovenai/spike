# SPIKE eval 20261111-212829

Model `Qwen3.5-4B-Q4_K_M.gguf`, llama.cpp `b11669-620d2225c`, greedy, thinking off, max_tokens 2048, host `macOS-27.0-arm64-arm-64bit`.

| task | variant | n | accuracy | 95% CI | Δ vs base (pts) | McNemar p | unparsed | truncated |
|---|---|---|---|---|---|---|---|---|
| finqa-test-select | base | 300 | 0.703 | 0.649–0.752 |  |  | 26 | 24 |
| finqa-test-select | spike-finance-it10000-s0.5 | 300 | 0.750 | 0.698–0.796 | +4.67 | 0.09795 | 1 | 0 |
| finqa-test-select | spike-finance-it20063-s0.25 | 300 | 0.757 | 0.705–0.802 | +5.33 | 0.01659 | 12 | 10 |
| finqa-test-select | spike-finance-it20063-s0.35 | 300 | 0.760 | 0.709–0.805 | +5.67 | 0.01862 | 5 | 8 |
| mmlu-pro-general-select | base | 400 | 0.642 | 0.594–0.688 |  |  | 0 | 17 |
| mmlu-pro-general-select | spike-finance-it10000-s0.5 | 400 | 0.590 | 0.541–0.637 | -5.25 | 0.03961 | 10 | 4 |
| mmlu-pro-general-select | spike-finance-it20063-s0.25 | 400 | 0.605 | 0.556–0.652 | -3.75 | 0.07218 | 4 | 11 |
| mmlu-pro-general-select | spike-finance-it20063-s0.35 | 400 | 0.593 | 0.544–0.640 | -5.00 | 0.01686 | 3 | 11 |
| tatqa-test-select | base | 300 | 0.700 | 0.646–0.749 |  |  | 1 | 5 |
| tatqa-test-select | spike-finance-it10000-s0.5 | 300 | 0.777 | 0.726–0.820 | +7.67 | 0.001403 | 0 | 0 |
| tatqa-test-select | spike-finance-it20063-s0.25 | 300 | 0.720 | 0.667–0.768 | +2.00 | 0.4177 | 0 | 0 |
| tatqa-test-select | spike-finance-it20063-s0.35 | 300 | 0.753 | 0.702–0.799 | +5.33 | 0.01133 | 0 | 0 |
| **finance-select (pooled)** | base | 600 | 0.702 | 0.664–0.737 |  |  | 27 | 29 |
| **finance-select (pooled)** | spike-finance-it10000-s0.5 | 600 | 0.763 | 0.728–0.796 | +6.17 | 0.00057 | 1 | 0 |
| **finance-select (pooled)** | spike-finance-it20063-s0.25 | 600 | 0.738 | 0.702–0.772 | +3.67 | 0.01685 | 12 | 10 |
| **finance-select (pooled)** | spike-finance-it20063-s0.35 | 600 | 0.757 | 0.721–0.789 | +5.50 | 0.000378 | 5 | 8 |
| **general-select (pooled)** | base | 400 | 0.642 | 0.594–0.688 |  |  | 0 | 17 |
| **general-select (pooled)** | spike-finance-it10000-s0.5 | 400 | 0.590 | 0.541–0.637 | -5.25 | 0.03961 | 10 | 4 |
| **general-select (pooled)** | spike-finance-it20063-s0.25 | 400 | 0.605 | 0.556–0.652 | -3.75 | 0.07218 | 4 | 11 |
| **general-select (pooled)** | spike-finance-it20063-s0.35 | 400 | 0.593 | 0.544–0.640 | -5.00 | 0.01686 | 3 | 11 |
