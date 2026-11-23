import type { ProviderInfo, Specialist } from "./types";

export type RuntimeSnapshot = {
  running: boolean;
  context?: number | null;
  rss_mb?: number | null;
  adapters?: string[];
};

export type ResidencyKind =
  | "local_running"
  | "local_stopped"
  | "remote_protected"
  | "remote_shared"
  | "remote_blocked"
  | "mixed"
  | "unknown";

export type ContextPressure = "ok" | "warn" | "high" | "unknown";

export type SpecialistExecution = "auto" | "adapter_loaded" | "instruction_profile";

export type TrustSnapshot = {
  residency: ResidencyKind;
  providerId: string;
  providerName: string;
  model: string;
  isLocal: boolean;
  rssGiB: string | null;
  estimatedTokens: number;
  contextLimit: number | null;
  contextRatio: number | null;
  pressure: ContextPressure;
  execution: SpecialistExecution;
  specialistName: string | null;
  /** Names of external providers the turn may reach (for "mixed"). */
  externalNames: string[];
};

export const LOCAL_ENGINE_ID = "spike-local";

export function estimateThreadChars(
  items: ReadonlyArray<{ kind: "user"; text: string } | { kind: "assistant"; run: { text: string } }>,
): number {
  let total = 0;
  for (const it of items) {
    total += it.kind === "user" ? it.text.length : it.run.text.length;
  }
  return total;
}

export function computeTrustSnapshot({
  mode,
  providerId,
  providers,
  specialists,
  engine,
  charCount,
}: {
  mode: string;
  providerId: string | null;
  providers: ProviderInfo[];
  specialists: Specialist[];
  engine: RuntimeSnapshot | null;
  charCount: number;
}): TrustSnapshot {
  const activeSpecialist = mode === "auto" ? undefined : specialists.find((s) => s.id === mode);
  const byId = (id: string | null | undefined) => (id ? providers.find((p) => p.id === id) : undefined);

  // Mirrors the server: explicit override, else the specialist's provider; in auto
  // any specialist may be routed to, so consider all of them.
  let candidates: ProviderInfo[] = [];
  if (providerId) {
    const p = byId(providerId);
    if (p) candidates = [p];
  } else if (activeSpecialist) {
    const p = byId(activeSpecialist.active_provider);
    if (p) candidates = [p];
  } else if (mode === "auto") {
    const seen = new Set<string>();
    for (const sp of specialists) {
      const p = byId(sp.active_provider);
      if (p && !seen.has(p.id)) {
        seen.add(p.id);
        candidates.push(p);
      }
    }
  }

  const resolvedProvider: ProviderInfo | null = candidates.length === 1 ? candidates[0] : candidates[0] ?? null;
  const external = candidates.filter((p) => !p.local);
  const isMixed = candidates.length > 1 && external.length > 0;
  const isLocal = resolvedProvider ? (isMixed ? false : candidates.every((p) => p.local)) : false;
  const resolvedId = isMixed ? "" : resolvedProvider?.id ?? "";
  const providerName = isMixed
    ? candidates.map((p) => p.name).join(", ")
    : resolvedProvider?.name ?? "";
  const model = !isMixed ? resolvedProvider?.model ?? "" : "";
  const isEngine = !isMixed && resolvedId === LOCAL_ENGINE_ID;

  let residency: ResidencyKind;
  if (!resolvedProvider) {
    residency = "unknown";
  } else if (isMixed) {
    residency = "mixed";
  } else if (isLocal) {
    const running = isEngine ? Boolean(engine?.running) : true;
    residency = running ? "local_running" : "local_stopped";
  } else if (resolvedProvider.paid && !resolvedProvider.allow_paid) {
    residency = "remote_blocked";
  } else if (resolvedProvider.share_files) {
    residency = "remote_shared";
  } else {
    residency = "remote_protected";
  }

  const rssMb = isEngine ? engine?.rss_mb ?? null : null;
  const rssGiB = rssMb != null && rssMb > 0 ? (rssMb / 1024).toFixed(1) : null;

  const estimatedTokens = Math.max(0, Math.ceil(charCount / 4));

  const capCtx = isMixed ? null :
    typeof resolvedProvider?.capabilities_effective?.context_length === "number"
      ? (resolvedProvider.capabilities_effective.context_length as number)
      : null;
  const rawCtx = isEngine ? (engine?.context ?? capCtx) : capCtx;
  const contextLimit = rawCtx != null && rawCtx > 0 ? rawCtx : null;
  const contextRatio = contextLimit ? Math.min(1, estimatedTokens / contextLimit) : null;

  const pressure: ContextPressure =
    contextRatio == null ? "unknown" : contextRatio >= 0.9 ? "high" : contextRatio >= 0.75 ? "warn" : "ok";

  const execution: SpecialistExecution =
    mode === "auto"
      ? "auto"
      : activeSpecialist?.active_mode === "adapter_loaded"
        ? "adapter_loaded"
        : "instruction_profile";

  return {
    residency,
    providerId: resolvedId,
    providerName,
    model,
    isLocal,
    rssGiB,
    estimatedTokens,
    contextLimit,
    contextRatio,
    pressure,
    execution,
    specialistName: activeSpecialist?.name ?? null,
    externalNames: external.map((p) => p.name),
  };
}
