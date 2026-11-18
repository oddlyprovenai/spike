import { useEffect, useRef, useState } from "react";
import { api } from "../api";
import { lang, t } from "../i18n";
import { useRestoreFocus } from "../useRestoreFocus";
import type { Project } from "../types";
import { IconClose } from "./Icons";

export type SampleInfo = { id: string; name: string; description: string; feature: string; files: number; bytes: number };

export const SPL = lang === "es"
  ? {
      samples: "Proyectos de ejemplo", hint: "Seis proyectos listos para probar, con datos inventados. Un clic y se abren como un proyecto normal.",
      import: "Importar", importing: "Importando…", loading: "Cargando…", files: "archivos", failed: "No se pudo importar el ejemplo: ",
    }
  : {
      samples: "Sample projects", hint: "Six projects ready to try, with invented data. One click and they open as a normal project.",
      import: "Import", importing: "Importing…", loading: "Loading…", files: "files", failed: "The sample could not be imported: ",
    };

/** The bundled sample projects (G39): a list with a one-click import in the user's UI language. */
export function SampleProjects({ onClose, onImported }: { onClose: () => void; onImported: (p: Project) => void }) {
  const [samples, setSamples] = useState<SampleInfo[] | null>(null);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const dialogRef = useRef<HTMLDivElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  useRestoreFocus();

  useEffect(() => {
    closeRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
        return;
      }
      if (e.key === "Tab" && dialogRef.current) {
        const focusable = [...dialogRef.current.querySelectorAll<HTMLElement>(
          'button:not(:disabled), [href], input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex]:not([tabindex="-1"])',
        )];
        if (!focusable.length) return;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (e.shiftKey && (document.activeElement === first || !dialogRef.current.contains(document.activeElement))) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && (document.activeElement === last || !dialogRef.current.contains(document.activeElement))) {
          e.preventDefault();
          first.focus();
        }
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  useEffect(() => {
    let live = true;
    api.get<SampleInfo[]>(`/api/samples?lang=${lang}`).then((rows) => live && setSamples(rows))
      .catch((e) => live && setError(String((e as Error).message)));
    return () => { live = false; };
  }, []);

  const run = async (id: string) => {
    if (busy) return;
    setBusy(id);
    setError("");
    try {
      onImported(await api.post<Project>(`/api/samples/${id}/import?lang=${lang}`, {}));
    } catch (e) {
      setError(SPL.failed + String((e as Error).message));
      setBusy("");
    }
  };

  return (
    <div className="modal-backdrop" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div ref={dialogRef} className="modal small" role="dialog" aria-modal="true" aria-busy={!!busy} aria-label={SPL.samples}>
        <div className="modal-head">
          <h2>{SPL.samples}</h2>
          <button ref={closeRef} type="button" className="icon-btn" onClick={onClose} aria-label={t.close}><IconClose /></button>
        </div>
        <div className="form padded" style={{ overflowY: "auto" }}>
          <p className="hint">{SPL.hint}</p>
          {!samples && !error && <p className="hint" role="status">{SPL.loading}</p>}
          {(samples ?? []).map((s) => (
            <div key={s.id} data-testid={`sample-${s.id}`} className="row"
              style={{ gap: 12, alignItems: "center", padding: "10px 0", borderTop: "1px solid var(--border)" }}>
              <div style={{ flex: 1, minWidth: 0 }}>
                <strong>{s.name}</strong> <span className="hint">· {s.feature} · {s.files} {SPL.files}</span>
                <div className="hint">{s.description}</div>
              </div>
              <button type="button" className="btn primary" data-testid={`sample-import-${s.id}`} disabled={!!busy}
                onClick={() => run(s.id)}>{busy === s.id ? SPL.importing : SPL.import}</button>
            </div>
          ))}
          {error && <div className="error-box" role="alert">{error}</div>}
        </div>
      </div>
    </div>
  );
}
