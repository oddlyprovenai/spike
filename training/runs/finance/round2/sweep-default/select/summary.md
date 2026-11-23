# SPIKE eval 20261110-173355

Model `Qwen3.5-4B-Q4_K_M.gguf`, llama.cpp `b11669-620d2225c`, greedy, thinking off, max_tokens 2048, host `macOS-27.0-arm64-arm-64bit`.

| task | variant | n | accuracy | 95% CI | Δ vs base (pts) | McNemar p | unparsed | truncated |
|---|---|---|---|---|---|---|---|---|
| finqa-test-select | base | 300 | 0.703 | 0.649–0.752 |  |  | 26 | 24 |
| finqa-test-select | spike-finance-it10000-s1 | 300 | 0.730 | 0.677–0.777 | +2.67 | 0.4557 | 1 | 0 |
| finqa-test-select | spike-finance-it20063-s0.5 | 300 | 0.757 | 0.705–0.802 | +5.33 | 0.04794 | 0 | 0 |
| finqa-test-select | spike-finance-it2600-s1 | 300 | 0.730 | 0.677–0.777 | +2.67 | 0.403 | 0 | 0 |
| finqa-test-select | spike-finance-it5000-s1 | 300 | 0.737 | 0.684–0.783 | +3.33 | 0.2954 | 0 | 0 |
| mmlu-pro-general-select | base | 400 | 0.647 | 0.600–0.693 |  |  | 1 | 13 |
| mmlu-pro-general-select | spike-finance-it10000-s1 | 400 | 0.545 | 0.496–0.593 | -10.25 | 2e-05 | 18 | 1 |
| mmlu-pro-general-select | spike-finance-it20063-s0.5 | 400 | 0.620 | 0.572–0.666 | -2.75 | 0.2351 | 3 | 2 |
| mmlu-pro-general-select | spike-finance-it2600-s1 | 400 | 0.522 | 0.474–0.571 | -12.50 | 0 | 20 | 3 |
| mmlu-pro-general-select | spike-finance-it5000-s1 | 400 | 0.570 | 0.521–0.618 | -7.75 | 0.000371 | 13 | 5 |
| tatqa-test-select | base | 300 | 0.703 | 0.649–0.752 |  |  | 0 | 3 |
| tatqa-test-select | spike-finance-it10000-s1 | 300 | 0.757 | 0.705–0.802 | +5.33 | 0.04022 | 0 | 0 |
| tatqa-test-select | spike-finance-it20063-s0.5 | 300 | 0.790 | 0.740–0.832 | +8.67 | 0.000106 | 0 | 0 |
| tatqa-test-select | spike-finance-it2600-s1 | 300 | 0.770 | 0.719–0.814 | +6.67 | 0.01046 | 0 | 0 |
| tatqa-test-select | spike-finance-it5000-s1 | 300 | 0.790 | 0.740–0.832 | +8.67 | 0.000862 | 0 | 0 |
| **finance-select (pooled)** | base | 600 | 0.703 | 0.666–0.739 |  |  | 26 | 27 |
| **finance-select (pooled)** | spike-finance-it10000-s1 | 600 | 0.743 | 0.707–0.777 | +4.00 | 0.05321 | 1 | 0 |
| **finance-select (pooled)** | spike-finance-it20063-s0.5 | 600 | 0.773 | 0.738–0.805 | +7.00 | 3.9e-05 | 0 | 0 |
| **finance-select (pooled)** | spike-finance-it2600-s1 | 600 | 0.750 | 0.714–0.783 | +4.67 | 0.01582 | 0 | 0 |
| **finance-select (pooled)** | spike-finance-it5000-s1 | 600 | 0.763 | 0.728–0.796 | +6.00 | 0.002194 | 0 | 0 |
| **general-select (pooled)** | base | 400 | 0.647 | 0.600–0.693 |  |  | 1 | 13 |
| **general-select (pooled)** | spike-finance-it10000-s1 | 400 | 0.545 | 0.496–0.593 | -10.25 | 2e-05 | 18 | 1 |
| **general-select (pooled)** | spike-finance-it20063-s0.5 | 400 | 0.620 | 0.572–0.666 | -2.75 | 0.2351 | 3 | 2 |
| **general-select (pooled)** | spike-finance-it2600-s1 | 400 | 0.522 | 0.474–0.571 | -12.50 | 0 | 20 | 3 |
| **general-select (pooled)** | spike-finance-it5000-s1 | 400 | 0.570 | 0.521–0.618 | -7.75 | 0.000371 | 13 | 5 |
