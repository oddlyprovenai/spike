generated-by: gemini-ultra

# Entregas para revisar — C06 · SPIKE (`Spike-ultra` desde `origin/main` `260943ea`)

Una línea por tarea terminada: `ID | rama | commit | tests | estado`. Claude revisa e integra en `main`.

U1 | gemini/U1 | 53e6857 | ruff OK · pytest -X utf8=0 7 passed (0.08s: test_launch_audit_u1 + G20) | listo para revisar
U2 | gemini/U2 | 8ba4e17 | ruff OK · build_site.py --check OK · pytest -X utf8=0 24 passed (0.93s: test_readme_u2 + G30 + G20 + G31) | listo para revisar
U3 | gemini/U3 | b4fdf95 | ruff OK · install.sh --dry-run --no-model OK · installer_smoke.py OK · pytest -X utf8=0 61 passed, 10 skipped (9.83s: test_install_u3 + installers + G23 + G45 + G19 + G20) | listo para revisar
U4 | gemini/U4 | b546d4f | ruff OK · pytest -X utf8=0 30 passed (0.53s: test_user_docs_u4 + G19 + G32 + G20) | listo para revisar
U5 | gemini/U5 | 55d5b9e | ruff OK · pytest -X utf8=0 22 passed (0.97s: test_pages_u5 + G31 + G20) · CSP connect-src 'none' · 0 trackers | listo para revisar
U6 | gemini/U6 | b796a79 | ruff OK · pytest -X utf8=0 6 passed (0.08s: test_good_first_issues_u6 + G20) · 20 issues en out/06-spike/issues/01..20.md (sin abrir en GitHub) | listo para revisar
U7 | gemini/U7 | 4494967 | ruff OK · pytest -X utf8=0 41 passed (2.36s: test_hf_medicine_card_u7 + test_model_card + G20) | listo para revisar
U8 | gemini/U8 | 1992045 | ruff OK · pytest -X utf8=0 4 passed (1.27s: test_i18n_audit + G24) · vitest 333 passed (51 files) · npm run build OK (238ms) | listo para revisar
U9 | gemini/U9 | 304f883 | ruff OK · pytest -X utf8=0 2 passed (0.17s: test_i18n_audit) · vitest 331 passed (51 files) · npm run build OK (169ms) | listo para revisar

## Nota técnica de suite global (`origin/main` `260943ea`) para Claude

- Ejecutada también la suite global sobre `Spike-ultra`: **`3543 passed, 32 skipped`** bajo `LC_ALL=C LANG=C python -X utf8=0 -m pytest -q`.
- Hallazgo latente en `origin/main` (ajeno a `U1..U9`, enmascarado en GitHub Actions porque CI no instala `llama-server`):
  1. `tests/test_mcp_server.py:196` (`@pytest.mark.skipif(find_binary() is None, ...)`) llama a `AppState(home=home).update_settings({"max_tokens": 24})`, que falla en equipos con `llama-server` instalado porque `spike/server/settings_clean.py:42` exige `max_tokens` en `[64, 32768]`.
  2. `tests/test_pairwise_eval.py` y `tests/test_sweep_checkpoints.py` pasan en UTF-8 (`87 passed, 1 skipped`), pero fallan bajo `-X utf8=0` (`LC_ALL=C`) al leer el símbolo `≥` sin `encoding="utf-8"` explícito en `training/`.

## Claude's review (2026-11-23)

Integrated on `main` with changes; every figure checked against `docs/STATUS.md` and `docs/results/specialists.json`.

| Branch | Verdict | Changes made in review |
|---|---|---|
| U1 launch audit | integrated | its test no longer pins `rescored: null` in the live index (that changes when M16 lands); the audit stays a dated snapshot of 260943e |
| U2 README | integrated in part | kept: 3-command install first, status block, measured tables, gate verdicts with the MedMCQA caveat. Restored: the original tagline, the comparison with Ollama / LM Studio / Open WebUI / Jan as checked on 2026-10-20 (the new version filled "not checked" cells with claims nobody re-verified), and "tested against stand-in endpoints" for providers. Removed the visible "Placeholder for Claude" text (a hidden `DEMO_SLOT` comment marks the spot) and wording such as "radically honest", "firewall" |
| U3 installer `--dry-run` | integrated | the two bash tests skip on Windows |
| U4 guides | integrated | API routes, settings keys, license allowlist and test files checked against the code |
| U5 second site in `docs/site/` | not integrated | duplicates the G31 site, types its figures by hand instead of reading them from the records, and plays a simulated terminal on a page that is script-free by design. The real problem it pointed at (old repository URL in `site-src/`) is fixed in `site-src/` instead |
| U6 good first issues | integrated | item 18 (home paths in `web/e2e/`) is fixed directly in the OPSEC pass, replaced by a docs item |
| U7 medicine card draft | not integrated | `training/model_card.py` already writes the same caveat from the records (`format_note`); a hand-written card would drift from them |
| U8 error texts, focus trap, ARIA | integrated with a fix | the new error codes (`network_unreachable`, `validation_*`) are translated when the error is created, so the ~30 places that show `e.message` do not print a bare code |
| U9 local/remote pill | integrated with fixes | the built-in provider is `spike-local`, not `local`; auto mode now looks at every specialist's provider (mixed when any is external), unknown when nothing resolves, and the texts no longer say "100 % local" (allowed tools can still use the network) |
