# SPIKE eval 20261123-133149

Model `Qwen3.5-4B-Q4_K_M.gguf`, llama.cpp `b11669-620d2225c`, greedy, thinking off, max_tokens 2048, host `macOS-27.0-arm64-arm-64bit`.

Data revisions: `finqa-test` @ `0f16e2867bef`, `tatqa-test` @ `870accc41953`, `mmlu-pro` (not pinned).

| task | variant | n | accuracy | 95% CI | Δ vs base (pts) | McNemar p | unparsed | truncated |
|---|---|---|---|---|---|---|---|---|
| finqa-test-select | base | 300 | 0.703 | 0.649–0.752 |  |  | 26 | 24 |
| finqa-test-select | spike-finance-it13375-s0.5 | 300 | 0.760 | 0.709–0.805 | +5.67 | 0.03634 | 3 | 0 |
| finqa-test-select | spike-finance-it1600-s1 | 300 | 0.700 | 0.646–0.749 | -0.33 | 1 | 1 | 0 |
| finqa-test-select | spike-finance-it3400-s1 | 300 | 0.720 | 0.667–0.768 | +1.67 | 0.653 | 0 | 0 |
| finqa-test-select | spike-finance-it6600-s1 | 300 | 0.737 | 0.684–0.783 | +3.33 | 0.275 | 0 | 0 |
| mmlu-pro-general-select | base | 400 | 0.642 | 0.594–0.688 |  |  | 0 | 17 |
| mmlu-pro-general-select | spike-finance-it13375-s0.5 | 400 | 0.583 | 0.534–0.630 | -6.00 | 0.01375 | 7 | 7 |
| mmlu-pro-general-select | spike-finance-it1600-s1 | 400 | 0.555 | 0.506–0.603 | -8.75 | 0.000127 | 3 | 0 |
| mmlu-pro-general-select | spike-finance-it3400-s1 | 400 | 0.557 | 0.508–0.605 | -8.50 | 0.000222 | 6 | 2 |
| mmlu-pro-general-select | spike-finance-it6600-s1 | 400 | 0.560 | 0.511–0.608 | -8.25 | 0.000264 | 1 | 1 |
| tatqa-test-select | base | 300 | 0.703 | 0.649–0.752 |  |  | 0 | 3 |
| tatqa-test-select | spike-finance-it13375-s0.5 | 300 | 0.783 | 0.733–0.826 | +8.00 | 0.000536 | 0 | 0 |
| tatqa-test-select | spike-finance-it1600-s1 | 300 | 0.713 | 0.660–0.762 | +1.00 | 0.7877 | 0 | 0 |
| tatqa-test-select | spike-finance-it3400-s1 | 300 | 0.730 | 0.677–0.777 | +2.67 | 0.3409 | 0 | 0 |
| tatqa-test-select | spike-finance-it6600-s1 | 300 | 0.783 | 0.733–0.826 | +8.00 | 0.004272 | 0 | 0 |
| **finance-select (pooled)** | base | 600 | 0.703 | 0.666–0.739 |  |  | 26 | 27 |
| **finance-select (pooled)** | spike-finance-it13375-s0.5 | 600 | 0.772 | 0.736–0.803 | +6.83 | 7.8e-05 | 3 | 0 |
| **finance-select (pooled)** | spike-finance-it1600-s1 | 600 | 0.707 | 0.669–0.742 | +0.33 | 0.9302 | 1 | 0 |
| **finance-select (pooled)** | spike-finance-it3400-s1 | 600 | 0.725 | 0.688–0.759 | +2.17 | 0.2981 | 0 | 0 |
| **finance-select (pooled)** | spike-finance-it6600-s1 | 600 | 0.760 | 0.724–0.792 | +5.67 | 0.004188 | 0 | 0 |
| **general-select (pooled)** | base | 400 | 0.642 | 0.594–0.688 |  |  | 0 | 17 |
| **general-select (pooled)** | spike-finance-it13375-s0.5 | 400 | 0.583 | 0.534–0.630 | -6.00 | 0.01375 | 7 | 7 |
| **general-select (pooled)** | spike-finance-it1600-s1 | 400 | 0.555 | 0.506–0.603 | -8.75 | 0.000127 | 3 | 0 |
| **general-select (pooled)** | spike-finance-it3400-s1 | 400 | 0.557 | 0.508–0.605 | -8.50 | 0.000222 | 6 | 2 |
| **general-select (pooled)** | spike-finance-it6600-s1 | 400 | 0.560 | 0.511–0.608 | -8.25 | 0.000264 | 1 | 1 |
