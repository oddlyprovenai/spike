# Crea tu primer especialista propio

Idioma: **Español** | [English](../en/first-specialist.md) · [Índice de la guía](README.md)

![Especialistas y configuración de paquetes propios](../images/specialists.png)

## Qué hace

Permite ampliar SPIKE más allá de los 13 dominios incluidos creando tu propio especialista de dominio — con su `system_prompt`, lista explícita de herramientas permitidas, palabras clave ponderadas en español e inglés para el enrutador léxico, documentos de referencia exclusivos del especialista y una skill `SKILL.md` asociada — y exportarlo como un paquete `.zip` libre de secretos (`format: "spike-pack"`, `version: 1`). Quienes contribuyan desde Apple Silicon pueden además registrar una receta de adaptador LoRA sujeta a la pasarela de licencias abiertas y a los criterios estadísticos contra el olvido.

## Cómo se usa paso a paso

### Parte 1 — Crear un especialista personalizado y su paquete (2 minutos, sin entrenar pesos)

1. **Define la ficha del especialista (`custom_specialists`):** asígnale un `id` en minúsculas, su `system_prompt`, solo las `tools` que necesite y `keywords` de palabra completa en la escala del enrutador (umbral `2.0`: `4` = jerga inequívoca del dominio, `3` = término claro del dominio, `2` = enruta solo salvo que otro gane, `1–1.5` = pista débil que solo suma acompañada):

```json
{
  "id": "logistics",
  "name": "Spike Logistics",
  "domain": "Supply chain, inventory and freight operations",
  "description": "Calculates safety stock, reorder points, lead-time buffers and freight terms from workspace spreadsheets.",
  "adapter": null,
  "adapter_status": "none",
  "sensitive": false,
  "tools": ["calculator", "read_file", "data_describe", "data_sql", "ask_user"],
  "keywords": {
    "incoterms": 4,
    "fob": 3,
    "albarán": 4,
    "albaran": 4,
    "reorder point": 4,
    "punto de pedido": 4,
    "safety stock": 4,
    "stock de seguridad": 4,
    "lead time": 3,
    "inventario": 2
  },
  "system_prompt": "You are Spike Logistics. Compute reorder points, safety stock and freight terms using calculator or data_sql instead of mental arithmetic. State assumptions clearly and never invent carrier rates."
}
```

2. **Añádelo en Ajustes o por API local:** abre **Ajustes → Especialistas** para registrarlo (o actualiza `custom_specialists` mediante `PATCH /api/settings` en `127.0.0.1:8740`). Al tener `adapter_status: "none"`, SPIKE lo muestra con honestidad como perfil de instrucciones sobre el modelo base compartido (o proveedor externo asignado).
3. **Acompáñalo de una `SKILL.md` validada:** guarda un archivo UTF-8 en `~/.spike/skills/inventory-reorder-audit/SKILL.md` y compruébalo sin red con `spike skills validate`:

```markdown
---
name: inventory-reorder-audit
description: Audit SKU lead times, demand variance, and reorder thresholds with SQL before recommending stock buffers.
license: Apache-2.0
---
# Inventory Reorder Audit

1. Inspect schema and row counts first with `data_describe`.
2. Compute mean demand, standard deviation, and reorder point via `data_sql` or `calculator` — never estimate numbers in prose.
3. Flag SKUs with negative or missing lead times before summarizing findings.
```

4. **Adjunta conocimiento exclusivo del especialista (opcional):** sube manuales o tablas que **solo** este especialista recordará desde **Ajustes → Especialistas** o `POST /api/specialist-documents` (`{"specialist": "logistics", "filename": "incoterms-notas.md", "text": "..."}`).
5. **Exporta o comparte como Paquete (`spike-pack`):** pulsa **Exportar paquete** (`GET /api/pack/export`) para obtener un `.zip` con `pack.json` y `skills/<nombre>/SKILL.md` validado contra [`specialist-pack.schema.json`](../../schemas/specialist-pack.schema.json). Las claves, cabeceras y variables de entorno se excluyen siempre. Impórtalo en otro equipo con `POST /api/pack/import`.

### Parte 2 — Flujo opcional de adaptador LoRA (contribuidores en Apple Silicon)

Si deseas entrenar un adaptador GGUF de `~42 MB` (`training/`):

1. **Verifica antes las licencias de datos (`training/datasets.yaml`):** `training/spike_train/licenses.py` solo admite licencias abiertas permisivas (`Apache-2.0`, `MIT`, `BSD`, `CC-BY-4.0`, `CC0`, `ODC-By`). **Está prohibido usar salidas generadas por Claude, GPT, Gemini o Llama 3.1** (`prepare.py` y `model_card.py` bloquean cualquier fuente no permitida).
2. **Fija los criterios de aceptación antes de entrenar (`training/configs/<id>.yaml`):** escribe la hipótesis (`hypothesis`), la mejora mínima en el dominio (`min_gain_points: 3.0`, `max_p_value: 0.05`) y la caída máxima tolerable en conocimiento general (`max_drop_points: 1.5`) *antes* de lanzar el entrenamiento.
3. **Descontaminación de 13-gramas y barrido contra el olvido:** `prepare.py` elimina solapamientos con los conjuntos de evaluación; `fix_forgetting.py` y `sweep_checkpoints.py` eligen punto de control y escala LoRA sobre particiones `*-select` y ejecutan la suite final una sola vez.
4. **Instalación verificada:** `spike adapters install` comprueba el veredicto y el SHA-256 y rechaza cualquier adaptador que no supere su puerta (detalles en [../../TRAINING.md](../../TRAINING.md) y [../../SPECIALISTS.md](../../SPECIALISTS.md)).

## Límites reales

- Los especialistas personalizados creados en Ajustes o importados en un paquete funcionan como **perfiles de instrucciones** (`β` / `none`); SPIKE nunca los etiqueta como adaptadores entrenados sin un recibo de aceptación verificado (`spike/specialists/acceptance/<id>.json` o versión activa en Evolución).
- El enrutador léxico compara palabras completas (ignorando mayúsculas y tildes); incluye las formas flexionadas habituales si buscas enrutado en ~1 ms sin llamada al modelo.
- El grado en que el modelo local de 4B sigue una `SKILL.md` o instrucciones nuevas **no está medido** hasta que registres al menos 3 preguntas de evaluación propias en **Ajustes → Evolución** (`spike evolve check`); consulta [../../STATUS.md](../../STATUS.md).

## Cómo comprobarlo

- Valida tus skills sin conexión: `.venv/bin/spike skills validate`.
- Ejecuta la prueba automática de esta guía (carga el JSON del especialista anterior, enruta consultas en español e inglés y verifica la exportación/importación del paquete `.zip` contra el esquema v1): `.venv/bin/python -m pytest -q tests/test_user_docs_u4.py tests/test_packs_reliability.py tests/test_specialists_status.py`.
