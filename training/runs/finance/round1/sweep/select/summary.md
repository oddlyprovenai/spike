# SPIKE eval 20261106-162059

Model `Qwen3.5-4B-Q4_K_M.gguf`, llama.cpp `b11669-620d2225c`, greedy, thinking off, max_tokens 2048, host `macOS-27.0-arm64-arm-64bit`.

| task | variant | n | accuracy | 95% CI | Δ vs base (pts) | McNemar p | unparsed | truncated |
|---|---|---|---|---|---|---|---|---|
| finqa-test-select | base | 300 | 0.713 | 0.660–0.762 |  |  | 28 | 22 |
| finqa-test-select | spike-finance-it4400-s0.5 | 300 | 0.727 | 0.674–0.774 | +1.33 | 0.7239 | 0 | 0 |
| finqa-test-select | spike-finance-it8825-s0.25 | 300 | 0.743 | 0.691–0.789 | +3.00 | 0.1628 | 13 | 13 |
| finqa-test-select | spike-finance-it8825-s0.35 | 300 | 0.757 | 0.705–0.802 | +4.33 | 0.06599 | 7 | 4 |
| mmlu-pro-general-select | base | 400 | 0.645 | 0.597–0.690 |  |  | 0 | 16 |
| mmlu-pro-general-select | spike-finance-it4400-s0.5 | 400 | 0.590 | 0.541–0.637 | -5.50 | 0.01832 | 7 | 5 |
| mmlu-pro-general-select | spike-finance-it8825-s0.25 | 400 | 0.590 | 0.541–0.637 | -5.50 | 0.01408 | 6 | 11 |
| mmlu-pro-general-select | spike-finance-it8825-s0.35 | 400 | 0.600 | 0.551–0.647 | -4.50 | 0.05666 | 3 | 9 |
| tatqa-test-select | base | 300 | 0.703 | 0.649–0.752 |  |  | 0 | 3 |
| tatqa-test-select | spike-finance-it4400-s0.5 | 300 | 0.763 | 0.712–0.808 | +6.00 | 0.01535 | 0 | 0 |
| tatqa-test-select | spike-finance-it8825-s0.25 | 300 | 0.707 | 0.653–0.755 | +0.33 | 1 | 0 | 0 |
| tatqa-test-select | spike-finance-it8825-s0.35 | 300 | 0.740 | 0.688–0.786 | +3.67 | 0.1173 | 0 | 0 |
| **finance-select (pooled)** | base | 600 | 0.708 | 0.671–0.743 |  |  | 28 | 25 |
| **finance-select (pooled)** | spike-finance-it4400-s0.5 | 600 | 0.745 | 0.709–0.778 | +3.67 | 0.05682 | 0 | 0 |
| **finance-select (pooled)** | spike-finance-it8825-s0.25 | 600 | 0.725 | 0.688–0.759 | +1.67 | 0.2954 | 13 | 13 |
| **finance-select (pooled)** | spike-finance-it8825-s0.35 | 600 | 0.748 | 0.712–0.781 | +4.00 | 0.01163 | 7 | 4 |
| **general-select (pooled)** | base | 400 | 0.645 | 0.597–0.690 |  |  | 0 | 16 |
| **general-select (pooled)** | spike-finance-it4400-s0.5 | 400 | 0.590 | 0.541–0.637 | -5.50 | 0.01832 | 7 | 5 |
| **general-select (pooled)** | spike-finance-it8825-s0.25 | 400 | 0.590 | 0.541–0.637 | -5.50 | 0.01408 | 6 | 11 |
| **general-select (pooled)** | spike-finance-it8825-s0.35 | 400 | 0.600 | 0.551–0.647 | -4.50 | 0.05666 | 3 | 9 |
