import "./LocalTrustBar.css";
import { useEffect, useRef, useState } from "react";
import { t } from "../i18n";
import { computeTrustSnapshot, type ResidencyKind, type RuntimeSnapshot } from "../localTrust";
import type { ProviderInfo, Specialist } from "../types";
import type { SettingsTab } from "./SettingsDialog";

function fmt(template: string, values: Record<string, string | number>): string {
  let out = template;
  for (const [k, v] of Object.entries(values)) {
    out = out.replaceAll(`{${k}}`, String(v));
  }
  return out;
}

function residencyBadge(kind: ResidencyKind): string {
  switch (kind) {
    case "local_running":
      return t.localTrust.badgeLocalRunning;
    case "local_stopped":
      return t.localTrust.badgeLocalStopped;
    case "remote_protected":
      return t.localTrust.badgeRemoteProtected;
    case "remote_shared":
      return t.localTrust.badgeRemoteShared;
    case "remote_blocked":
      return t.localTrust.badgeRemoteBlocked;
  }
}

function residencyDetail(kind: ResidencyKind, provider: string): string {
  switch (kind) {
    case "local_running":
      return fmt(t.localTrust.detailLocalRunning, { provider });
    case "local_stopped":
      return fmt(t.localTrust.detailLocalStopped, { provider });
    case "remote_protected":
      return fmt(t.localTrust.detailRemoteProtected, { provider });
    case "remote_shared":
      return fmt(t.localTrust.detailRemoteShared, { provider });
    case "remote_blocked":
      return fmt(t.localTrust.detailRemoteBlocked, { provider });
  }
}

export function LocalTrustBar({
  mode,
  providerId,
  providers,
  specialists,
  engine,
  charCount,
  onOpenSettings,
}: {
  mode: string;
  providerId: string | null;
  providers: ProviderInfo[];
  specialists: Specialist[];
  engine: RuntimeSnapshot | null;
  charCount: number;
  onOpenSettings: (tab: SettingsTab) => void;
}) {
  const [open, setOpen] = useState(false);
  const wrapRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);

  const snap = computeTrustSnapshot({ mode, providerId, providers, specialists, engine, charCount });
  const pct = snap.contextRatio != null ? Math.round(snap.contextRatio * 100) : null;
  const showCtxTag = pct != null && (snap.estimatedTokens > 0 || snap.pressure !== "ok");

  useEffect(() => {
    if (!open) return;
    const onPointerDown = (event: MouseEvent) => {
      const el = wrapRef.current;
      if (el && event.target instanceof Node && !el.contains(event.target)) {
        setOpen(false);
      }
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        event.stopPropagation();
        setOpen(false);
        triggerRef.current?.focus();
      }
    };
    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  const modeDescription =
    snap.execution === "auto"
      ? t.localTrust.modeAuto
      : snap.execution === "adapter_loaded"
        ? t.localTrust.modeAdapter
        : t.localTrust.modeProfile;

  const targetTab: SettingsTab = snap.isLocal && snap.providerId === "local" ? "engine" : "providers";
  const settingsLabel = targetTab === "engine" ? t.localTrust.openEngine : t.localTrust.openProviders;
  const providerLabel = snap.model ? `${snap.providerName} · ${snap.model}` : snap.providerName;

  return (
    <div ref={wrapRef} className="local-trust" data-testid="local-trust-bar">
      <button
        ref={triggerRef}
        type="button"
        data-testid="local-trust-trigger"
        className={`local-trust-pill state-${snap.residency} pressure-${snap.pressure}`}
        aria-expanded={open}
        aria-controls="local-trust-panel"
        title={t.localTrust.pillHint}
        onClick={() => setOpen((v) => !v)}
      >
        <span className={`local-trust-dot state-${snap.residency}`} aria-hidden="true" />
        <span>{residencyBadge(snap.residency)}</span>
        {showCtxTag && (
          <span className={`local-trust-ctx-tag pressure-${snap.pressure}`}>
            {fmt(t.localTrust.badgeCtxShort, { pct })}
          </span>
        )}
      </button>

      {open && (
        <section
          id="local-trust-panel"
          className="local-trust-popover"
          role="region"
          aria-label={t.localTrust.panelTitle}
        >
          <h3 className="local-trust-title">{t.localTrust.panelTitle}</h3>
          <p className="local-trust-detail">{residencyDetail(snap.residency, providerLabel)}</p>

          <div className="local-trust-block">
            <span className="local-trust-label">{t.localTrust.modeHeading}</span>
            <span className="local-trust-detail">
              {snap.specialistName ? `${snap.specialistName} — ${modeDescription}` : modeDescription}
            </span>
          </div>

          {snap.rssGiB && (
            <div className="local-trust-block">
              <span className="local-trust-label">{t.localTrust.memoryHeading}</span>
              <span className="local-trust-mono">{fmt(t.localTrust.memoryRss, { gib: snap.rssGiB })}</span>
            </div>
          )}

          <div className="local-trust-block">
            <span className="local-trust-label">{t.localTrust.meterLabel}</span>
            {snap.contextLimit != null && pct != null ? (
              <>
                <div
                  className="local-trust-meter"
                  role="meter"
                  aria-valuemin={0}
                  aria-valuemax={snap.contextLimit}
                  aria-valuenow={Math.min(snap.estimatedTokens, snap.contextLimit)}
                  aria-label={t.localTrust.meterLabel}
                >
                  <div
                    className={`local-trust-meter-fill pressure-${snap.pressure}`}
                    style={{ width: `${Math.min(100, Math.max(2, pct))}%` }}
                  />
                </div>
                <span className="local-trust-mono">
                  {fmt(t.localTrust.ctxSummary, {
                    used: snap.estimatedTokens.toLocaleString(),
                    limit: snap.contextLimit.toLocaleString(),
                    pct,
                  })}
                </span>
                {snap.pressure === "warn" && <p className="local-trust-alert">{t.localTrust.ctxWarn}</p>}
                {snap.pressure === "high" && (
                  <p className="local-trust-alert pressure-high">{t.localTrust.ctxHigh}</p>
                )}
              </>
            ) : (
              <span className="local-trust-mono">
                {fmt(t.localTrust.ctxUnknown, { used: snap.estimatedTokens.toLocaleString() })}
              </span>
            )}
          </div>

          <button
            type="button"
            data-testid="local-trust-settings"
            className="btn small"
            onClick={() => {
              setOpen(false);
              onOpenSettings(targetTab);
            }}
          >
            {settingsLabel}
          </button>
        </section>
      )}
    </div>
  );
}
