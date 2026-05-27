import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import Login from "@/pages/Login";

// Mock useAuth hook
vi.mock("@/hooks/useAuth", () => ({
  useAuth: () => ({
    signIn: vi.fn().mockResolvedValue(undefined),
    signUp: vi.fn().mockResolvedValue(undefined),
  }),
}));

describe("Login Page", () => {
  it("renders login form", () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    expect(screen.getByText("AI Cloud Agent")).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Sign In" })).toBeInTheDocument();
  });

  it("toggles between sign in and sign up", () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    const toggleButton = screen.getByRole("button", { name: "Sign Up" });
    fireEvent.click(toggleButton);

    expect(screen.getByRole("button", { name: "Sign Up" })).toBeInTheDocument();
  });

  it("updates email input on change", () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    const emailInput = screen.getByLabelText("Email") as HTMLInputElement;
    fireEvent.change(emailInput, { target: { value: "test@example.com" } });

    expect(emailInput.value).toBe("test@example.com");
  });
});
