import { beforeEach, describe, expect, it, vi } from "vitest";
import { api } from "./api";

function mockJsonResponse(body: unknown, init: ResponseInit = {}): Response {
  return new Response(JSON.stringify(body), {
    status: init.status ?? 200,
    headers: { "Content-Type": "application/json", ...(init.headers || {}) },
  });
}

describe("api()", () => {
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
  });

  it("prefixes the configured API base and parses JSON", async () => {
    fetchMock.mockResolvedValueOnce(mockJsonResponse({ ok: true, n: 1 }));
    const data = await api("/health");
    expect(data).toEqual({ ok: true, n: 1 });
    const [url] = fetchMock.mock.calls[0];
    expect(url).toMatch(/\/health$/);
  });

  it("sends JSON content-type when body is not FormData", async () => {
    fetchMock.mockResolvedValueOnce(mockJsonResponse({}));
    await api("/x", { method: "POST", body: JSON.stringify({ a: 1 }) });
    const [, opts] = fetchMock.mock.calls[0];
    expect((opts.headers as Record<string, string>)["Content-Type"]).toBe("application/json");
  });

  it("omits Content-Type when body is FormData (browser sets the boundary)", async () => {
    fetchMock.mockResolvedValueOnce(mockJsonResponse({}));
    const fd = new FormData();
    fd.append("file", new Blob(["hi"]), "hi.txt");
    await api("/upload", { method: "POST", body: fd });
    const [, opts] = fetchMock.mock.calls[0];
    expect((opts.headers as Record<string, string>)["Content-Type"]).toBeUndefined();
  });

  it("attaches Bearer token from localStorage when present", async () => {
    localStorage.setItem("token", "abc.def.ghi");
    fetchMock.mockResolvedValueOnce(mockJsonResponse({}));
    await api("/auth/me");
    const [, opts] = fetchMock.mock.calls[0];
    expect((opts.headers as Record<string, string>).Authorization).toBe("Bearer abc.def.ghi");
  });

  it("omits Authorization when no token is set", async () => {
    fetchMock.mockResolvedValueOnce(mockJsonResponse({}));
    await api("/public");
    const [, opts] = fetchMock.mock.calls[0];
    expect((opts.headers as Record<string, string>).Authorization).toBeUndefined();
  });

  it("throws with server-provided detail on non-2xx", async () => {
    fetchMock.mockResolvedValueOnce(
      mockJsonResponse({ detail: "Complete intake first" }, { status: 400 }),
    );
    await expect(api("/onboarding/placement")).rejects.toThrow("Complete intake first");
  });

  it("throws a generic message when error body is not JSON", async () => {
    fetchMock.mockResolvedValueOnce(new Response("oops", { status: 500 }));
    await expect(api("/boom")).rejects.toThrow(/Request failed: 500/);
  });

  it("allows the caller to override headers", async () => {
    fetchMock.mockResolvedValueOnce(mockJsonResponse({}));
    await api("/x", { headers: { "X-Trace": "t1" } });
    const [, opts] = fetchMock.mock.calls[0];
    expect((opts.headers as Record<string, string>)["X-Trace"]).toBe("t1");
  });
});
