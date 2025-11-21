const API_BASE_URL = "http://127.0.0.1:8000";

/**
 * WHAT:
 *   Helper to call our FastAPI backend.
 * WHY:
 *   Avoid repeating fetch boilerplate everywhere and easily attach JWT token.
 * HOW:
 *   - Reads token from localStorage.
 *   - Adds Authorization header if token exists.
 *   - Sends JSON body & parses JSON response.
 */
export async function apiFetch(
  path: string,
  options: RequestInit = {}
): Promise<any> {
  const token = localStorage.getItem("solo_token");

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    // Attach Bearer token only if present
    (headers as any)["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    // Try to read error body; fallback to status text
    const text = await res.text();
    throw new Error(text || `Request failed with status ${res.status}`);
  }

  // Try parse JSON; if empty, return null
  try {
    return await res.json();
  } catch {
    return null;
  }
}

/**
 * WHAT: Signup wrapper.
 * WHY: Makes /auth/signup easy to call from components.
 */
export function signup(data: {
  email: string;
  password: string;
  display_name?: string;
  height_cm?: number;
  weight_kg?: number;
  activity_level?: string;
}) {
  return apiFetch("/auth/signup", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * WHAT: Login wrapper.
 * WHY: Makes /auth/login easy to call from components.
 */
export function login(data: { email: string; password: string }) {
  return apiFetch("/auth/login", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * WHAT: Generate missions.
 * WHY: Calls protected /missions/generate.
 */
export function generateMissions() {
  return apiFetch("/missions/generate", {
    method: "POST",
  });
}

/**
 * WHAT: Get missions.
 * WHY: Calls protected /missions.
 */
export function getMissions() {
  return apiFetch("/missions");
}
