import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import Chat from "@/pages/Chat";

// Mock useAuth hook
vi.mock("@/hooks/useAuth", () => ({
  useAuth: () => ({
    user: { email: "test@example.com" },
    signOut: vi.fn().mockResolvedValue(undefined),
  }),
}));

describe("Chat Page", () => {
  it("renders chat interface", () => {
    render(<Chat />);

    expect(screen.getByPlaceholderText("Type your message...")).toBeInTheDocument();
    expect(screen.getByText("test@example.com")).toBeInTheDocument();
  });

  it("renders send button with send icon", () => {
    render(<Chat />);

    // The send button is an icon button without text, so we check by role
    const buttons = screen.getAllByRole("button");
    expect(buttons.length).toBeGreaterThanOrEqual(2); // Sign Out + Send
  });
});
