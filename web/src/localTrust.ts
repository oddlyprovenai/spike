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
  | "remote_blocked";

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
};

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
  const resolvedProvider =
    (providerId ? providers.find((p) => p.id === providerId) : undefined) ??
    (activeSpecialist?.active_provider ? providers.find((p) => p.id === activeSpecialist.active_provider) : undefined) ??
    providers.find((p) => p.id === "local") ??
    providers[0] ??
    null;

  const isLocal = resolvedProvider ? Boolean(resolvedProvider.local) : true;
  const resolvedId = resolvedProvider?.id ?? "local";
  const providerName = resolvedProvider?.name ?? "Local (llama.cpp)";
  const model = resolvedProvider?.model ?? "";

  let residency: ResidencyKind;
  if (isLocal) {
    const running = resolvedId === "local" ? Boolean(engine?.running) : true;
    residency = running ? "local_running" : "local_stopped";
  } else if (resolvedProvider?.paid && !resolvedProvider.allow_paid) {
    residency = "remote_blocked";
  } else if (resolvedProvider?.share_files) {
    residency = "remote_shared";
  } else {
    residency = "remote_protected";
  }

  const rssMb = isLocal && resolvedId === "local" ? engine?.rss_mb ?? null : null;
  const rssGiB = rssMb != null && rssMb > 0 ? (rssMb / 1024).toFixed(1) : null;

  const estimatedTokens = Math.max(0, Math.ceil(charCount / 4));

  const capCtx =
    typeof resolvedProvider?.capabilities_effective?.context_length === "number"
      ? (resolvedProvider.capabilities_effective.context_length as number)
      : null;
  const rawCtx = isLocal && resolvedId === "local" ? (engine?.context ?? capCtx) : capCtx;
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
  };
}
