import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

describe("Agent API", () => {
  beforeEach(() => {
    import.meta.env.VITE_AGENT_ENDPOINT = "http://localhost:8001/api/pydantic-agent";
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("sends a message and returns parsed response", async () => {
    const mockResponse = { response: "Hello from AI Cloud!" };

    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    } as Response);

    const res = await fetch("http://localhost:8001/api/pydantic-agent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: "Hi" }),
    });
    const data = await res.json();

    expect(data).toEqual(mockResponse);
  });

  it("throws on API error response", async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
    } as Response);

    const res = await fetch("http://localhost:8001/api/pydantic-agent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: "Hi" }),
    });

    expect(res.ok).toBe(false);
    expect(res.status).toBe(500);
  });
});
