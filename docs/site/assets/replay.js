/* Zero-tracker offline terminal replay for SPIKE GitHub Pages.
 * No network APIs, no cookies, no storage. Figures match docs/STATUS.md & docs/results/specialists.json.
 */
(function () {
  "use strict";

  var SCENARIOS = {
    en: [
      {
        id: "install",
        caption: "Simulated replay 1/4: 3-command clean install & SHA-256 verification",
        lines: [
          { t: "prompt", v: "lab@mac-studio ~ % git clone https://github.com/oddlyprovenai/spike.git && cd spike" },
          { t: "out", v: "Cloning into 'spike'... done." },
          { t: "prompt", v: "lab@mac-studio spike % ./scripts/install.sh --yes" },
          { t: "out", v: "Python: Python 3.13 (isolated pipx environment)" },
          { t: "ok", v: "[ok] Qwen3.5-4B-Q4_K_M.gguf · license apache-2.0 · SHA-256 verified" },
          { t: "ok", v: "[ok] spike doctor --strict · 127.0.0.1 loopback only · paid APIs blocked" },
          { t: "prompt", v: "lab@mac-studio spike % spike serve --open" },
          { t: "info", v: "SPIKE listening on http://127.0.0.1:8740 (zero external requests)" }
        ]
      },
      {
        id: "router",
        caption: "Simulated replay 2/4: ~1 ms lexical router (116/130 = 0.89 on blind holdout)",
        lines: [
          { t: "prompt", v: "lab@mac-studio ~ % spike ask \"Differential diagnosis cues for acute pericarditis vs STEMI?\"" },
          { t: "info", v: "[router 0.8 ms · 0 LLM calls] -> Spike Medicine (accepted LoRA loaded, SHA-256 21caa0a0...)" },
          { t: "out", v: "Note: general medical information, not clinical advice or a medical device." },
          { t: "prompt", v: "lab@mac-studio ~ % spike ask \"Compare portfolio historical VaR and max drawdown from returns.csv\"" },
          { t: "info", v: "[router 0.9 ms · 0 LLM calls] -> Spike Finance (beta prompt profile · rounds 1 & 2 rejected)" },
          { t: "ok", v: "Blind holdout benchmark: 116/130 = 0.89 (95% Wilson CI 0.83-0.93) · zero-cost dispatch" }
        ]
      },
      {
        id: "gates",
        caption: "Simulated replay 3/4: Pre-registered acceptance gates — rejections published too",
        lines: [
          { t: "prompt", v: "lab@mac-studio ~ % python scripts/results_index.py --check && echo OK" },
          { t: "err", v: "[round 1 · 2026-10-20] spike-medicine: +31.92 pts medicine, -7.62 pts general (limit -1.50) -> REJECTED" },
          { t: "ok", v: "[round 2 · 2026-11-05] spike-medicine-it13270-s0.5: 31.9% -> 67.0% (2,318 items), -0.62 general -> ACCEPTED" },
          { t: "warn", v: "Caveat: 409 of 1,000 MedMCQA base answers were unparsed by initial scorer (readable-only: 0.467 -> 0.660; PubMedQA 0 unparsed: +38.20 pts)." },
          { t: "err", v: "[rounds 1 & 2 · 2026-11-09/11] spike-finance: -3.00 / -2.75 pts general-select -> REJECTED (stays beta)" }
        ]
      },
      {
        id: "hardware",
        caption: "Simulated replay 4/4: Measured 16 GB CPU-only & Apple Silicon receipts",
        lines: [
          { t: "prompt", v: "lab@mac-studio ~ % spike bench --context 1024,8192" },
          { t: "out", v: "16 GB x86 (4 cores, CPU only, q8_0 KV): 1K -> 6.2 tok/s (52 s TTFT) | 8K -> 5.1 tok/s (13 min TTFT)" },
          { t: "out", v: "Memory on 16 GB x86: 3.6 GiB anonymous RSS (6.1 GiB total RSS with mmap)" },
          { t: "ok", v: "Apple M4 Max (Metal --gpu-layers 99): 1K -> 82 tok/s (0.9 s TTFT) | 8K -> 80 tok/s (7.2 s TTFT, 3.6 GiB RSS)" }
        ]
      }
    ],
    es: [
      {
        id: "install",
        caption: "Simulación 1/4: Instalación limpia en 3 comandos y verificación SHA-256",
        lines: [
          { t: "prompt", v: "lab@mac-studio ~ % git clone https://github.com/oddlyprovenai/spike.git && cd spike" },
          { t: "out", v: "Clonando en 'spike'... listo." },
          { t: "prompt", v: "lab@mac-studio spike % ./scripts/install.sh --yes" },
          { t: "out", v: "Python: Python 3.13 (entorno aislado pipx)" },
          { t: "ok", v: "[ok] Qwen3.5-4B-Q4_K_M.gguf · licencia apache-2.0 · SHA-256 verificado" },
          { t: "ok", v: "[ok] spike doctor --strict · solo 127.0.0.1 · llamadas de pago bloqueadas" },
          { t: "prompt", v: "lab@mac-studio spike % spike serve --open" },
          { t: "info", v: "SPIKE escuchando en http://127.0.0.1:8740 (cero peticiones externas)" }
        ]
      },
      {
        id: "router",
        caption: "Simulación 2/4: Enrutador léxico en ~1 ms (116/130 = 0.89 en partición ciega)",
        lines: [
          { t: "prompt", v: "lab@mac-studio ~ % spike ask \"Claves diferenciales entre pericarditis aguda e IAM con elevación del ST\"" },
          { t: "info", v: "[router 0.8 ms · 0 llamadas LLM] -> Spike Medicine (adaptador aceptado, SHA-256 21caa0a0...)" },
          { t: "out", v: "Aviso: información general, no consejo médico ni producto sanitario." },
          { t: "prompt", v: "lab@mac-studio ~ % spike ask \"Calcula VaR histórico y drawdown máximo de cartera desde retornos.csv\"" },
          { t: "info", v: "[router 0.9 ms · 0 llamadas LLM] -> Spike Finance (perfil beta · rondas 1 y 2 rechazadas)" },
          { t: "ok", v: "Holdout ciego: 116/130 = 0.89 (IC Wilson 95% 0.83-0.93) · despacho sin coste de modelo" }
        ]
      },
      {
        id: "gates",
        caption: "Simulación 3/4: Puertas estadísticas fijadas antes de entrenar (también publicamos rechazos)",
        lines: [
          { t: "prompt", v: "lab@mac-studio ~ % python scripts/results_index.py --check && echo OK" },
          { t: "err", v: "[ronda 1 · 2026-10-20] spike-medicine: +31.92 pts medicina, -7.62 pts general (límite -1.50) -> RECHAZADO" },
          { t: "ok", v: "[ronda 2 · 2026-11-05] spike-medicine-it13270-s0.5: 31.9% -> 67.0% (2,318 ítems), -0.62 general -> ACEPTADO" },
          { t: "warn", v: "Advertencia: 409 de 1,000 respuestas base en MedMCQA quedaron sin parsear (sobre legibles: 0.467 -> 0.660; PubMedQA 0 no parseadas: +38.20 pts)." },
          { t: "err", v: "[rondas 1 y 2 · 2026-11-09/11] spike-finance: -3.00 / -2.75 pts general-select -> RECHAZADO (sigue en beta)" }
        ]
      },
      {
        id: "hardware",
        caption: "Simulación 4/4: Velocidad medida en 16 GB sin GPU y en Apple Silicon",
        lines: [
          { t: "prompt", v: "lab@mac-studio ~ % spike bench --context 1024,8192" },
          { t: "out", v: "16 GB x86 (4 núcleos, solo CPU, KV q8_0): 1K -> 6.2 tok/s (52 s TTFT) | 8K -> 5.1 tok/s (13 min TTFT)" },
          { t: "out", v: "Memoria en 16 GB x86: 3.6 GiB RSS anónima (6.1 GiB RSS total con mmap)" },
          { t: "ok", v: "Apple M4 Max (Metal --gpu-layers 99): 1K -> 82 tok/s (0.9 s TTFT) | 8K -> 80 tok/s (7.2 s TTFT, 3.6 GiB RSS)" }
        ]
      }
    ]
  };

  var CLASS_MAP = {
    prompt: "term-prompt",
    info: "term-info",
    warn: "term-warn",
    err: "term-err",
    ok: "term-ok",
    out: ""
  };

  function initReplay() {
    var root = document.getElementById("spike-replay");
    if (!root) return;

    var lang = document.documentElement.lang === "es" ? "es" : "en";
    var list = SCENARIOS[lang];
    var screen = document.getElementById("replay-screen");
    var caption = document.getElementById("replay-caption");
    var replayBtn = document.getElementById("replay-restart");
    var tabs = Array.prototype.slice.call(root.querySelectorAll('[role="tab"]'));
    var timer = null;
    var activeIndex = 0;
    var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function clearTimer() {
      if (timer !== null) {
        window.clearTimeout(timer);
        timer = null;
      }
    }

    function appendLine(item) {
      var span = document.createElement("span");
      var cls = CLASS_MAP[item.t] || "";
      if (cls) span.className = cls;
      span.textContent = item.v + "\n";
      screen.appendChild(span);
    }

    function renderScenario(idx, animate) {
      clearTimer();
      activeIndex = idx;
      var sc = list[idx] || list[0];
      tabs.forEach(function (tab, i) {
        var sel = i === idx;
        tab.setAttribute("aria-selected", sel ? "true" : "false");
        tab.tabIndex = sel ? 0 : -1;
      });
      if (caption) caption.textContent = sc.caption;
      screen.textContent = "";

      if (!animate || reduced) {
        sc.lines.forEach(appendLine);
        return;
      }

      var step = 0;
      function tick() {
        if (step >= sc.lines.length) {
          timer = null;
          return;
        }
        appendLine(sc.lines[step]);
        step += 1;
        timer = window.setTimeout(tick, 220);
      }
      tick();
    }

    tabs.forEach(function (tab, idx) {
      tab.addEventListener("click", function () {
        renderScenario(idx, true);
      });
      tab.addEventListener("keydown", function (ev) {
        var next = null;
        if (ev.key === "ArrowRight") next = (idx + 1) % tabs.length;
        else if (ev.key === "ArrowLeft") next = (idx - 1 + tabs.length) % tabs.length;
        else if (ev.key === "Home") next = 0;
        else if (ev.key === "End") next = tabs.length - 1;
        if (next !== null) {
          ev.preventDefault();
          tabs[next].focus();
          renderScenario(next, true);
        }
      });
    });

    if (replayBtn) {
      replayBtn.addEventListener("click", function () {
        renderScenario(activeIndex, true);
      });
    }

    renderScenario(0, false);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initReplay);
  } else {
    initReplay();
  }
})();
