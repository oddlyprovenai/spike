# Instalación y primer arranque

Idioma: **Español** | [English](../en/installation.md) · [Índice de la guía](README.md)

![Instalación y primer arranque](../images/installation.png)

## Qué hace

Instala SPIKE en 3 comandos o menos como aplicación Python aislada (`pipx`) junto con la interfaz web compilada, prepara el motor local `llama-server` (`llama.cpp`) y descarga opcionalmente el modelo base `Qwen3.5-4B` (`Q4_K_M`, 2,55 GiB) tras comprobar su licencia Apache-2.0 y su hash SHA-256. Los instaladores nativos candidatos (`.dmg`, `.exe`, `.AppImage`) incluyen además un asistente de primer arranque que comprueba disco libre (mínimo 6 GiB) y memoria RAM (mínimo 8 GiB) antes de iniciar cualquier descarga.

## Cómo se usa paso a paso

1. **Instalación limpia en 3 comandos (macOS y Linux):**
   ```bash
   git clone https://github.com/oddlyprovenai/spike.git && cd spike
   ./scripts/install.sh --yes               # añade --no-model para omitir los 2,7 GB del modelo, o --dry-run para simular
   spike serve --open
   ```
2. **Instalación limpia en 3 comandos (Windows PowerShell 5.1 o 7):**
   ```powershell
   git clone https://github.com/oddlyprovenai/spike.git; cd spike
   powershell -ExecutionPolicy Bypass -File scripts\install.ps1 -Yes   # añade -NoModel o -DryRun según necesites
   spike serve --open
   ```
3. **Simulación en seco sin tocar el equipo (`--dry-run`):** ejecuta `./scripts/install.sh --dry-run` (o `scripts\install.ps1 -DryRun`) para revisar qué intérprete Python (3.11–3.13), entorno `pipx`, compilación web, binario `llama-server` y comprobación `spike doctor --strict` se ejecutarían, sin modificar archivos ni descargar pesos.
4. **Entorno virtual manual (desarrollo):** `python3 -m venv .venv && .venv/bin/pip install -e ".[dev,docs,finance,data,motion,keyring]"` y `cd web && npm ci && npm run build`.
5. Ejecuta `spike doctor` en cualquier momento para verificar Python, `llama-server`, `~/.spike`, manifiestos SHA-256 de modelos y almacén de claves, y abre `http://127.0.0.1:8740`.

## Límites reales

- En una máquina de 16 GB x86 solo con CPU (4 núcleos, AVX-512), `Qwen3.5-4B Q4_K_M` genera a **5,1–6,2 tok/s** hasta 8K tokens de contexto (52 s hasta la primera palabra a 1K; 773 s a 8K) usando **3,6 GiB** de memoria anónima (6,1 GiB RSS con el archivo mapeado). Un contexto de 32K en CPU tarda ~1,5 h hasta la primera palabra, por lo que SPIKE inicia equipos solo CPU con ventana de 8K.
- En Apple Silicon M4 Max con Metal (`--gpu-layers 99`), genera a **80–82 tok/s** (0,86 s hasta la primera palabra a 1K; 7,2 s a 8K) con 3,6 GiB RSS.
- Los instaladores nativos candidatos (`.dmg`, `.exe`, `.AppImage`) están probados en runners limpios de GitHub Actions (Windows Server 2022 y Ubuntu 24.04 con modelo real; runner macOS con modelo diminuto de prueba porque el runner gratuito tiene 7,0 GiB de RAM frente a la guarda de 8 GiB), aún no están publicados y no llevan firma de pago; consulta [../../STATUS.md](../../STATUS.md).

## Cómo comprobarlo

- Previsualiza los pasos sin cambios con `./scripts/install.sh --dry-run --no-model`.
- Ejecuta `.venv/bin/spike doctor` y confirma el estado del entorno local.
- Ejecuta las suites offline de instaladores, primer arranque y lanzador: `.venv/bin/python -m pytest -q tests/test_installers.py tests/test_install_u3.py tests/test_first_run_g23.py tests/test_launcher_setup.py tests/test_installer_smoke_g45.py`.
- Ejecuta la prueba de humo aislada sin modelo: `python scripts/installer_smoke.py --wheel dist/spike_ai-*.whl` (o `python scripts/installer_smoke.py --use-python .venv/bin/python`). Levanta SPIKE en un puerto libre de loopback con `SPIKE_HOME`, `HOME` y `SPIKE_API_TOKEN` temporales, verifica `/api/health` y `/v1/models` (200 con token y 401 sin él), detiene el proceso, limpia la carpeta temporal y comprueba que `~/.spike` permanece intacto.

### Qué cubre la prueba de humo del instalador y qué no

- Cubre: que el paquete incluye servidor e interfaz web funcionales, que arranca en limpio, que responden `/api/health` y `/v1/models`, que se exige el token de acceso y que el cierre no deja residuos.
- No sustituye a probar los instaladores nativos en escritorios domésticos reales, no prueba los diálogos de Gatekeeper/SmartScreen sin firma y no descarga ni carga pesos reales (`--no-local`).
