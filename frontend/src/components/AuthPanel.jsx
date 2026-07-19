import React, { useMemo, useState } from "react";
import { api, setToken } from "../api";

const PASSWORD_REGEX =
  /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;

export default function AuthPanel({ onLogin, runAction }) {
  const [mode, setMode] = useState("login");

  const [email, setEmail] = useState("");

  const [password, setPassword] = useState("");

  const [confirmPassword, setConfirmPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);

  const [submitting, setSubmitting] = useState(false);

  const emailValid = useMemo(
    () => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email),
    [email]
  );

  const passwordValid = useMemo(
    () => PASSWORD_REGEX.test(password),
    [password]
  );

  const passwordsMatch =
    mode === "login" || password === confirmPassword;

  const canSubmit =
    emailValid &&
    passwordValid &&
    passwordsMatch &&
    !submitting;

  async function submit(e) {
    e.preventDefault();

    if (!canSubmit) return;

    setSubmitting(true);

    try {
      const payload =
        mode === "register"
          ? await runAction("Register", () =>
              api.register(email, password)
            )
          : await runAction("Sign in", () =>
              api.login(email, password)
            );

      if (mode === "register") {
        setMode("login");
        setPassword("");
        setConfirmPassword("");
        return;
      }

      if (!payload.access_token) {
        throw new Error(payload.message || "Login failed");
      }

      setToken(payload.access_token);

      await onLogin();

    } catch {
      // handled by toast
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-panel">

        <div>
          <p className="eyebrow">
            Secure Multimodal Medical AI
          </p>

          <h1>NIGHTINGALE</h1>

          <p className="muted">
            Securely understand medical reports using AI,
            OCR, Retrieval-Augmented Generation and semantic search.
          </p>
        </div>

        <form
          className="stack"
          onSubmit={submit}
        >

          <div className="segmented">
            <button
              type="button"
              className={mode === "login" ? "active" : ""}
              onClick={() => setMode("login")}
            >
              Sign In
            </button>

            <button
              type="button"
              className={mode === "register" ? "active" : ""}
              onClick={() => setMode("register")}
            >
              Register
            </button>
          </div>

          <label>
            Email Address

            <input
              type="email"
              placeholder="example@gmail.com"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />

            {!emailValid && email.length > 0 && (
              <small className="error">
                Please enter a valid email address.
              </small>
            )}
          </label>

          <label>
            Password

            <div className="password-input">

              <input
                type={showPassword ? "text" : "password"}
                placeholder="Enter your password"
                autoComplete={
                  mode === "login"
                    ? "current-password"
                    : "new-password"
                }
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />

              <button
                type="button"
                className="toggle-password"
                onClick={() =>
                  setShowPassword((v) => !v)
                }
              >
                {showPassword ? "Hide" : "Show"}
              </button>

            </div>
          </label>

          {mode === "register" && (
            <>
              <div className="password-rules">

                <strong>Password Requirements</strong>

                <ul>

                  <li className={password.length >= 8 ? "valid" : ""}>
                    Minimum 8 characters
                  </li>

                  <li className={/[A-Z]/.test(password) ? "valid" : ""}>
                    One uppercase letter
                  </li>

                  <li className={/[a-z]/.test(password) ? "valid" : ""}>
                    One lowercase letter
                  </li>

                  <li className={/\d/.test(password) ? "valid" : ""}>
                    One number
                  </li>

                </ul>

              </div>

              <label>
                Confirm Password

                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="Confirm password"
                  value={confirmPassword}
                  onChange={(e) =>
                    setConfirmPassword(e.target.value)
                  }
                />

                {!passwordsMatch &&
                  confirmPassword.length > 0 && (
                    <small className="error">
                      Passwords do not match.
                    </small>
                  )}
              </label>
            </>
          )}

          <button
            className="primary"
            disabled={!canSubmit}
            type="submit"
          >
            {submitting
              ? "Please wait..."
              : mode === "login"
              ? "Sign In"
              : "Create Account"}
          </button>

          <p className="auth-footer">
            Secure • AI Powered • Patient Scoped
          </p>

        </form>

      </section>
    </main>
  );
}