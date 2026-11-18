import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { api, streamPost } from "./api";
import { DataBackup } from "./components/DataBackup";
import { ErrorLog } from "./components/ErrorLog";
import { SampleProjects } from "./components/SampleProjects";
import { SkillImport } from "./components/SkillImport";
import { projectError, t } from "./i18n";

const fsSpec = "node:" + "fs";
const { readFileSync } = await (import(/* @vite-ignore */ fsSpec) as Promise<{
  readFileSync(path: string, encoding: string): string;
}>);

let host: HTMLDivElement;
let root: Root;

function typeInto(field: HTMLInputElement, value: string) {
  act(() => {
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")!.set!.call(field, value);
    field.dispatchEvent(new Event("input", { bubbles: true }));
  });
}

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
  vi.unstubAllGlobals();
});

describe("U8 — API error normalization & i18n coverage", () => {
  it("translates browser network failures into actionable local-server messages while keeping AbortError intact", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));
    await expect(api.get("/api/health")).rejects.toThrow(/spike serve/);

    const abortErr = new DOMException("Aborted", "AbortError");
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(abortErr));
    await expect(streamPost("/api/chat", { message: "hi" }, () => {})).rejects.toBe(abortErr);
  });

  it("formats FastAPI 422 validation arrays cleanly on both JSON and SSE routes without [object Object]", async () => {
    const detail = [{ type: "missing", loc: ["body", "url"], msg: "Field required" }];
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: false,
      status: 422,
      statusText: "Unprocessable Entity",
      json: async () => ({ detail }),
    }));

    let msgJson = "";
    try {
      await api.post("/api/skills/import-github/preview", {});
    } catch (e) {
      msgJson = (e as Error).message;
    }
    expect(msgJson).not.toContain("[object Object]");
    expect(msgJson).not.toContain('[{"type"');
    expect(msgJson).toContain("url");

    let msgStream = "";
    try {
      await streamPost("/api/chat", {}, () => {});
    } catch (e) {
      msgStream = (e as Error).message;
    }
    expect(msgStream).not.toContain("[object Object]");
    expect(msgStream).toContain("url");
  });

  it("translates backup, pack, and upload error strings in both Spanish and English", () => {
    const cases = [
      "request refused: it comes from another web site",
      "your data can only be exported or deleted on the computer SPIKE runs on",
      "the backup is too large",
      "unsupported content type",
      "invalid Content-Length header",
      "not a SPIKE pack (format/version)",
      "the archive has no valid pack.json",
      "no skill found in the archive (expected <name>/SKILL.md)",
      "invalid specialist in pack: missing system_prompt",
      "unexpected entry 'evil.sh'",
      "network_unreachable",
      "validation_field:url",
    ];
    for (const raw of cases) {
      const es = projectError(raw, "es");
      const en = projectError(raw, "en");
      expect(es, `untranslated ES for ${raw}`).not.toBe(raw);
      expect(en, `untranslated EN for ${raw}`).not.toBe(raw);
      expect(es).not.toBe(en);
    }
  });
});

describe("U8 — Keyboard, focus-ring, and ARIA live-region polish", () => {
  it("keeps DataBackup's file input keyboard-focusable (.sr-only, not hidden) and styles label.btn:focus-within", () => {
    act(() => root.render(<DataBackup />));
    const input = host.querySelector<HTMLInputElement>('[data-testid="backup-file"]')!;
    expect(input.hidden).toBe(false);
    expect(input.className).toContain("sr-only");

    const css = readFileSync("src/styles.css", "utf-8");
    expect(css).toContain("label.btn:focus-within");
  });

  it("moves initial focus into SampleProjects modal and traps Tab inside the dialog", async () => {
    vi.spyOn(api, "get").mockResolvedValue([
      { id: "expenses", name: "Expenses", description: "Demo", feature: "Data", files: 2, bytes: 120 },
    ] as never);
    await act(async () => {
      root.render(<SampleProjects onClose={() => {}} onImported={() => {}} />);
    });
    const dialog = host.querySelector<HTMLElement>('[role="dialog"]')!;
    expect(dialog.contains(document.activeElement)).toBe(true);

    const importBtn = host.querySelector<HTMLButtonElement>('[data-testid="sample-import-expenses"]')!;
    importBtn.focus();
    act(() => {
      dialog.dispatchEvent(new KeyboardEvent("keydown", { key: "Tab", bubbles: true }));
    });
    expect(dialog.contains(document.activeElement)).toBe(true);
  });

  it("submits SkillImport preview on Enter key and announces completion with role=status", async () => {
    vi.spyOn(api, "post").mockImplementation(async (urlPath: string) => {
      if (urlPath.endsWith("/preview")) {
        return {
          preview_id: "p1",
          sha256: "abc123",
          name: "demo-skill",
          description: "desc",
          skill_md: "---\nname: demo-skill\n---",
          can_install: true,
          license: { id: "MIT", status: "allowed", source: "LICENSE", can_enable: true },
          issues: [],
          files: [{ path: "SKILL.md", size: 24, binary: false, text: "---" }],
          source: { owner: "org", repo: "repo", ref: "main", path: "" },
        } as never;
      }
      return { ok: true } as never;
    });

    act(() => root.render(<SkillImport onInstalled={() => {}} />));
    const urlInput = host.querySelector<HTMLInputElement>('[data-testid="skill-import-url"]')!;
    typeInto(urlInput, "https://github.com/org/repo");
    await act(async () => {
      urlInput.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
    });

    const installBtn = host.querySelector<HTMLButtonElement>('[data-testid="skill-import-install"]')!;
    expect(installBtn).not.toBeNull();
    await act(async () => installBtn.click());

    const doneBox = host.querySelector<HTMLElement>('[data-testid="skill-import-done"]')!;
    expect(doneBox.getAttribute("role")).toBe("status");
  });

  it("catches ErrorLog clear failures cleanly into a status message instead of an unhandled rejection", async () => {
    vi.spyOn(api, "get").mockResolvedValue({
      path: "~/.spike/logs/errors.log",
      entries: [{ time: 1700000000, kind: "route", where: "GET /api/x", type: "ValueError", frames: [], version: "0.1.0" }],
    } as never);
    vi.spyOn(api, "del").mockRejectedValueOnce(new Error("offline"));

    await act(async () => root.render(<ErrorLog />));
    const clearBtn = [...host.querySelectorAll("button")].find((b) => b.textContent === t.errorLog.clear)!;
    await act(async () => clearBtn.click());

    const status = host.querySelector('[role="status"]');
    expect(status?.textContent).toBeTruthy();
  });
});
