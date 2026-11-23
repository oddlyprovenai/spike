import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { computeTrustSnapshot, estimateThreadChars } from "./localTrust";
import { LocalTrustBar } from "./components/LocalTrustBar";
import { t } from "./i18n";
import type { ProviderInfo, Specialist } from "./types";

const localProvider: ProviderInfo = {
  id: "local",
  kind: "openai_compat",
  name: "Local (llama.cpp)",
  base_url: "http://127.0.0.1:8090/v1",
  model: "Qwen3.5-4B-Q4_K_M.gguf",
  paid: false,
  allow_paid: false,
  local: true,
  share_files: false,
  has_key: false,
  capabilities_effective: null,
};

const cloudProtected: ProviderInfo = {
  id: "anthropic",
  kind: "anthropic",
  name: "Anthropic",
  base_url: "https://api.anthropic.com",
  model: "claude-sonnet-4-6",
  paid: true,
  allow_paid: true,
  local: false,
  share_files: false,
  has_key: true,
  capabilities_effective: null,
};

const cloudShared: ProviderInfo = {
  ...cloudProtected,
  id: "openai-shared",
  name: "OpenAI Team",
  share_files: true,
};

const cloudBlocked: ProviderInfo = {
  ...cloudProtected,
  id: "openai-blocked",
  name: "OpenAI Locked",
  allow_paid: false,
};

const medicineAdapterSpec: Specialist = {
  id: "medicine",
  name: "Spike Medicine",
  domain: "medicine",
  description: "Clinical literature specialist",
  adapter: "spike-medicine-it13270-s0.5.gguf",
  adapter_status: "evaluated",
  adapter_accepted: true,
  sensitive: true,
  tools: [],
  active_provider: "local",
  active_mode: "adapter_loaded",
};

const financeProfileSpec: Specialist = {
  id: "finance",
  name: "Spike Finance",
  domain: "finance",
  description: "Quantitative finance specialist",
  adapter: null,
  adapter_status: "evaluated",
  adapter_accepted: false,
  sensitive: true,
  tools: [],
  active_provider: "anthropic",
  active_mode: "instruction_profile",
};

describe("computeTrustSnapshot (U9 local-AI residency & context budget)", () => {
  it("reports local_running with live RSS GiB, adapter_loaded mode, and context ratio", () => {
    const snap = computeTrustSnapshot({
      mode: "medicine",
      providerId: null,
      providers: [localProvider, cloudProtected],
      specialists: [medicineAdapterSpec, financeProfileSpec],
      engine: { running: true, context: 8192, rss_mb: 6246.4 },
      charCount: 4096,
    });
    expect(snap.residency).toBe("local_running");
    expect(snap.isLocal).toBe(true);
    expect(snap.rssGiB).toBe("6.1");
    expect(snap.execution).toBe("adapter_loaded");
    expect(snap.estimatedTokens).toBe(1024);
    expect(snap.contextLimit).toBe(8192);
    expect(snap.pressure).toBe("ok");
  });

  it("distinguishes remote_protected, remote_shared, and remote_blocked providers", () => {
    const protectedSnap = computeTrustSnapshot({
      mode: "finance",
      providerId: null,
      providers: [localProvider, cloudProtected, cloudShared, cloudBlocked],
      specialists: [medicineAdapterSpec, financeProfileSpec],
      engine: { running: false, context: 8192, rss_mb: null },
      charCount: 800,
    });
    expect(protectedSnap.residency).toBe("remote_protected");
    expect(protectedSnap.providerId).toBe("anthropic");
    expect(protectedSnap.execution).toBe("instruction_profile");

    const sharedSnap = computeTrustSnapshot({
      mode: "auto",
      providerId: "openai-shared",
      providers: [localProvider, cloudProtected, cloudShared, cloudBlocked],
      specialists: [],
      engine: null,
      charCount: 800,
    });
    expect(sharedSnap.residency).toBe("remote_shared");

    const blockedSnap = computeTrustSnapshot({
      mode: "auto",
      providerId: "openai-blocked",
      providers: [localProvider, cloudProtected, cloudShared, cloudBlocked],
      specialists: [],
      engine: null,
      charCount: 800,
    });
    expect(blockedSnap.residency).toBe("remote_blocked");
  });

  it("raises warn at >=75% and high at >=90% of local context window", () => {
    const warnSnap = computeTrustSnapshot({
      mode: "auto",
      providerId: "local",
      providers: [localProvider],
      specialists: [],
      engine: { running: true, context: 8192, rss_mb: 3686.4 },
      charCount: 25000, // 6250 est tokens / 8192 = 76.3%
    });
    expect(warnSnap.pressure).toBe("warn");

    const highSnap = computeTrustSnapshot({
      mode: "auto",
      providerId: "local",
      providers: [localProvider],
      specialists: [],
      engine: { running: true, context: 8192, rss_mb: 3686.4 },
      charCount: 30500, // 7625 est tokens / 8192 = 93.1%
    });
    expect(highSnap.pressure).toBe("high");
  });

  it("estimates thread character count across user and assistant turns", () => {
    const count = estimateThreadChars([
      { kind: "user", text: "Hello world" },
      { kind: "assistant", run: { text: "Measured response" } },
    ]);
    expect(count).toBe("Hello world".length + "Measured response".length);
  });
});

describe("LocalTrustBar interactive accessibility & disclosure", () => {
  let host: HTMLDivElement;
  let root: Root;

  beforeEach(() => {
    (globalThis as unknown as { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
    host = document.createElement("div");
    document.body.append(host);
    root = createRoot(host);
  });

  afterEach(() => {
    act(() => root.unmount());
    host.remove();
    vi.restoreAllMocks();
  });

  it("toggles the trust disclosure popover, exposes meter ARIA attributes, and restores focus on Escape", async () => {
    const onOpenSettings = vi.fn();
    await act(async () => {
      root.render(
        <LocalTrustBar
          mode="medicine"
          providerId="local"
          providers={[localProvider]}
          specialists={[medicineAdapterSpec]}
          engine={{ running: true, context: 8192, rss_mb: 6246.4 }}
          charCount={26000}
          onOpenSettings={onOpenSettings}
        />,
      );
    });

    const trigger = host.querySelector<HTMLButtonElement>('[data-testid="local-trust-trigger"]');
    expect(trigger).not.toBeNull();
    expect(trigger?.getAttribute("aria-expanded")).toBe("false");
    expect(host.querySelector("#local-trust-panel")).toBeNull();

    await act(async () => {
      trigger!.focus();
      trigger!.click();
    });

    expect(trigger?.getAttribute("aria-expanded")).toBe("true");
    const panel = host.querySelector("#local-trust-panel");
    expect(panel).not.toBeNull();
    expect(panel?.textContent).toContain("6.1 GiB");
    expect(panel?.textContent).toContain(t.localTrust.modeAdapter);

    const meter = panel?.querySelector('[role="meter"]');
    expect(meter).not.toBeNull();
    expect(meter?.getAttribute("aria-valuemax")).toBe("8192");
    expect(meter?.getAttribute("aria-valuenow")).toBe("6500");

    // Pressing Escape closes the popover and restores focus to trigger
    await act(async () => {
      panel!.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
    });
    expect(host.querySelector("#local-trust-panel")).toBeNull();
    expect(document.activeElement).toBe(trigger);

    // Re-open and click settings jump button
    await act(async () => {
      trigger!.click();
    });
    const settingsBtn = host.querySelector<HTMLButtonElement>('[data-testid="local-trust-settings"]');
    expect(settingsBtn).not.toBeNull();
    await act(async () => {
      settingsBtn!.click();
    });
    expect(onOpenSettings).toHaveBeenCalledWith("engine");
    expect(host.querySelector("#local-trust-panel")).toBeNull();
  });
});
