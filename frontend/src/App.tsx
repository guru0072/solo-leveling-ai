import { useEffect, useState } from "react";
import { signup, login, generateMissions, getMissions } from "./api";

interface Mission {
  id: string;
  user_id: string;
  title: string;
  description: string;
  xp_reward: number;
  goal: any;
  status: string;
}

/**
 * WHAT:
 *   Root component for the frontend.
 * WHY:
 *   - Handles auth (signup/login).
 *   - Stores token.
 *   - Shows missions using protected endpoints.
 * HOW:
 *   - Uses useState for form fields and auth state.
 *   - Talks to backend via helper functions in api.ts.
 */
function App() {
  // ---------------------------
  // Auth-related state
  // ---------------------------
  const [authMode, setAuthMode] = useState<"login" | "signup">("signup");
  const [email, setEmail] = useState("navin@example.com");
  const [password, setPassword] = useState("mypass123");
  const [displayName, setDisplayName] = useState("Navin");
  const [token, setToken] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);

  // ---------------------------
  // Missions-related state
  // ---------------------------
  const [missions, setMissions] = useState<Mission[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * WHAT:
   *   On initial load, check if a token is stored.
   * WHY:
   *   So user doesn't have to log in again after refresh.
   * HOW:
   *   Read from localStorage once and update React state.
   */
  useEffect(() => {
    const storedToken = localStorage.getItem("solo_token");
    const storedUserId = localStorage.getItem("solo_user_id");
    if (storedToken) {
      setToken(storedToken);
    }
    if (storedUserId) {
      setUserId(storedUserId);
    }
  }, []);

  /**
   * WHAT:
   *   Handle signup form submit.
   * WHY:
   *   Create new user and get token from /auth/signup.
   * HOW:
   *   Call signup(), store token + userId in state and localStorage.
   */
  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const res = await signup({
        email,
        password,
        display_name: displayName,
        height_cm: 173,
        weight_kg: 75,
        activity_level: "sedentary",
      });

      // Expecting { status, user_id, token }
      setToken(res.token);
      setUserId(res.user_id);
      localStorage.setItem("solo_token", res.token);
      localStorage.setItem("solo_user_id", res.user_id);
    } catch (err: any) {
      setError(err.message || "Signup failed");
    }
  };

  /**
   * WHAT:
   *   Handle login form submit.
   * WHY:
   *   Verify credentials and get token from /auth/login.
   * HOW:
   *   Call login(), store token + userId.
   */
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const res = await login({ email, password });
      setToken(res.token);
      setUserId(res.user_id);
      localStorage.setItem("solo_token", res.token);
      localStorage.setItem("solo_user_id", res.user_id);
    } catch (err: any) {
      setError(err.message || "Login failed");
    }
  };

  /**
   * WHAT:
   *   Log out user.
   * WHY:
   *   Clear token and user-specific data.
   * HOW:
   *   Remove from state and localStorage.
   */
  const handleLogout = () => {
    setToken(null);
    setUserId(null);
    setMissions([]);
    localStorage.removeItem("solo_token");
    localStorage.removeItem("solo_user_id");
  };

  /**
   * WHAT:
   *   Ask backend to generate missions for current user.
   * WHY:
   *   Uses protected endpoint /missions/generate.
   * HOW:
   *   Calls generateMissions(), then refreshes missions list.
   */
  const handleGenerateMissions = async () => {
    setError(null);
    setLoading(true);
    try {
      await generateMissions();
      const res = await getMissions();
      setMissions(res);
    } catch (err: any) {
      setError(err.message || "Failed to generate missions");
    } finally {
      setLoading(false);
    }
  };

  /**
   * WHAT:
   *   Initial load of missions if token is present.
   * WHY:
   *   So after login, user sees missions without manual refresh.
   * HOW:
   *   When token changes and is non-null, call getMissions().
   */
  useEffect(() => {
    const loadMissions = async () => {
      if (!token) return;
      try {
        const res = await getMissions();
        setMissions(res);
      } catch (err) {
        // ignore for now
      }
    };
    loadMissions();
  }, [token]);

  return (
    <div
      style={{
        fontFamily: "system-ui, sans-serif",
        padding: "2rem",
        maxWidth: "800px",
        margin: "0 auto",
      }}
    >
      <h1>Solo Leveling AI — Prototype</h1>
      <p style={{ color: "#555" }}>
        FastAPI + React + JWT | Anime-style fitness agent backend
      </p>

      {/* Auth section */}
      <section
        style={{
          marginTop: "1.5rem",
          padding: "1rem",
          border: "1px solid #ddd",
          borderRadius: "8px",
        }}
      >
        <div
          style={{
            marginBottom: "1rem",
            display: "flex",
            gap: "1rem",
            alignItems: "center",
          }}
        >
          <button
            onClick={() => setAuthMode("signup")}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "4px",
              border: authMode === "signup" ? "2px solid #000" : "1px solid #aaa",
              background: authMode === "signup" ? "#eee" : "#fff",
            }}
          >
            Signup
          </button>
          <button
            onClick={() => setAuthMode("login")}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "4px",
              border: authMode === "login" ? "2px solid #000" : "1px solid #aaa",
              background: authMode === "login" ? "#eee" : "#fff",
            }}
          >
            Login
          </button>

          {token && (
            <span style={{ marginLeft: "auto", fontSize: "0.9rem" }}>
              Logged in as <strong>{email}</strong>{" "}
              <button onClick={handleLogout} style={{ marginLeft: "0.5rem" }}>
                Logout
              </button>
            </span>
          )}
        </div>

        <form onSubmit={authMode === "signup" ? handleSignup : handleLogin}>
          <div style={{ marginBottom: "0.5rem" }}>
            <label>
              Email:{" "}
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={{ width: "100%" }}
                required
              />
            </label>
          </div>

          <div style={{ marginBottom: "0.5rem" }}>
            <label>
              Password:{" "}
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{ width: "100%" }}
                required
              />
            </label>
          </div>

          {authMode === "signup" && (
            <div style={{ marginBottom: "0.5rem" }}>
              <label>
                Display Name:{" "}
                <input
                  type="text"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  style={{ width: "100%" }}
                />
              </label>
            </div>
          )}

          {error && (
            <p style={{ color: "red", marginTop: "0.5rem" }}>{error}</p>
          )}

          <button
            type="submit"
            style={{ marginTop: "0.5rem", padding: "0.5rem 1rem" }}
          >
            {authMode === "signup" ? "Create Account" : "Login"}
          </button>
        </form>
      </section>

      {/* Missions section */}
      <section
        style={{
          marginTop: "1.5rem",
          padding: "1rem",
          border: "1px solid #ddd",
          borderRadius: "8px",
        }}
      >
        <h2>Daily Missions</h2>

        {!token && (
          <p style={{ color: "#777" }}>
            Log in or sign up to generate and view your missions.
          </p>
        )}

        {token && (
          <>
            <button
              onClick={handleGenerateMissions}
              disabled={loading}
              style={{ padding: "0.5rem 1rem", marginBottom: "1rem" }}
            >
              {loading ? "Generating..." : "Generate Missions"}
            </button>

            {missions.length === 0 && !loading && (
              <p>No missions yet. Click &quot;Generate Missions&quot;.</p>
            )}

            <ul>
              {missions.map((m) => (
                <li key={m.id} style={{ marginBottom: "0.75rem" }}>
                  <strong>{m.title}</strong> — {m.description} (XP:{" "}
                  {m.xp_reward})
                </li>
              ))}
            </ul>
          </>
        )}
      </section>
    </div>
  );
}

export default App;
