# Copias de seguridad, borrado total, paleta de comandos, espacio de tarea e inspector de skills

Idioma: **Español** | [English](../en/workspace-governance.md) · [Índice de la guía](README.md)

![Privacidad, copias de seguridad y gobierno del espacio local](../images/privacy-and-spend.png)

## Qué hace

Reúne los controles de propiedad de datos y navegación local incorporados para `v0.1`: copias de seguridad en `.zip` con sumas SHA-256 y vista previa antes de restaurar, borrado total con palabra de confirmación, **Paleta de comandos** (`Ctrl+K` / `⌘K`) y visita guiada repetible, seis proyectos de ejemplo bilingües en un clic, el **Espacio de tarea** unificado para respuestas multipaso y sesiones Dev en la app, el inspector con filtro de licencia para importar `SKILL.md` desde GitHub y el registro local redactado de errores.

## Cómo se usa paso a paso

1. **Muévete rápido con la Paleta de comandos (`Ctrl+K` / `⌘K`):** pulsa `Ctrl+K` (`⌘K` en Mac) desde cualquier pantalla para cambiar de vista, elegir especialista, abrir un proyecto, buscar en el historial o iniciar una sesión Dev usando flechas, `Intro` y `Esc`. Puedes repetir la **Visita guiada** o consultar todos los atajos en **Ajustes → Ayuda**.
2. **Prueba con los Proyectos de ejemplo:** abre **Proyectos** e importa en un clic cualquiera de los seis casos listos en español e inglés (hoja de gastos, encargo de informe, minipágina web, manual largo, flujo visual o caso financiero simulado), sin realizar peticiones externas.
3. **Audita cada acción en el Espacio de tarea:** pulsa **Ver tarea** en cualquier respuesta multipaso o abre el panel lateral de una **Sesión Dev** (`/api/dev/*`) para revisar el estado de cada paso, cada permiso concedido o denegado (`permitido una vez`, `permitido siempre`, `denegado`, `bloqueado por ajustes`), los archivos cambiados con botón de deshacer y los entregables — reconstruido íntegramente desde los eventos guardados incluso tras reiniciar el servidor.
4. **Instala una `SKILL.md` desde GitHub con revisión previa (`Ajustes → Skills`):** pega el enlace del repositorio para abrir una vista previa (`POST /api/skills/import-github/preview`). SPIKE comprueba que la licencia sea permisiva (`MIT`, `Apache-2.0`, `BSD` o `ISC`), muestra `SKILL.md`, cada archivo y su SHA-256 antes de escribir nada en disco y deja la skill **desactivada** hasta que tú la actives. Ningún modelo puede iniciar una instalación.
5. **Exporta, restaura o borra todos tus datos (`Ajustes → Privacidad`):**
   - **Exportar copia (`GET /api/backup/export`):** descarga un `.zip` con ajustes, conversaciones, Memoria neuronal, proyectos y skills propias con SHA-256 por archivo — **nunca** incluye claves de API ni secretos de conectores.
   - **Restaurar (`POST /api/backup/preview` → `POST /api/backup/restore`):** previsualiza primero el contenido y pide confirmación antes de sobrescribir archivos existentes (`overwrite=1`).
   - **Borrar todos mis datos:** exige escribir la palabra de confirmación; los modelos `.gguf` descargados y las claves guardadas en el llavero del sistema **solo** se eliminan si marcas sus casillas independientes, y SPIKE se niega a borrar una carpeta que no sea exclusivamente suya.
6. **Copia diagnósticos sin datos privados (`Ajustes → Errores`):** consulta los últimos fallos internos de la aplicación (sin textos de mensajes, contenidos de archivos ni claves; con rutas acortadas) y pulsa **Copiar como issue** para copiar texto plano al portapapeles sin enviar nada por red.

## Límites reales

- Las rutas de copia de seguridad, restauración, borrado total, sesiones Dev y registro de errores solo aceptan peticiones **desde el propio ordenador donde corre SPIKE** (`403` ante otro origen o host).
- El archivo `.zip` de copia de seguridad excluye deliberadamente claves de API y secretos de conectores; tras restaurar en otro equipo, vuelve a introducir las claves externas en **Ajustes → Proveedores**.
- El Espacio de tarea reconstruye de forma determinista los eventos guardados; la eficacia real del modelo local de 4B resolviendo sesiones de programación completas sobre repositorios reales **no está medida** aún con pesos reales ([../../STATUS.md](../../STATUS.md)).

## Cómo comprobarlo

- Ejecuta las pruebas offline de copias de seguridad, borrado seguro, visita guiada y paleta, proyectos de ejemplo, Espacio de tarea, importación de skills desde GitHub y registro local de errores:
  `.venv/bin/python -m pytest -q tests/test_backup_g34.py tests/test_wipe_g36.py tests/test_onboarding_g33.py tests/test_samples.py tests/test_dev_api.py tests/test_skill_import_o3.py tests/test_error_log_g43.py`
- Ejecuta las pruebas de componentes web:
  `cd web && npx vitest run src/dataBackup.test.tsx src/taskSpace.test.tsx src/devSessions.test.tsx src/errorLog.test.tsx`
