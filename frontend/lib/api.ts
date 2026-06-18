import axios from "axios";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: BASE,
  headers: { "Content-Type": "application/json" },
});

// ── Company Profile ──────────────────────────────────────────
// These need a token passed in since they're called outside React components
export async function getProfile(token: string | null) {
  try {
    const res = await axios.get(`${BASE}/match/profile`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.data;
  } catch (err: any) {
    if (err?.response?.status === 404) return null;
    throw err;
  }
}

export async function saveProfile(
  token: string | null,
  data: import("../types/profile").CompanyProfileCreate
) {
  const res = await axios.post(`${BASE}/match/profile`, data, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
}

export default api;