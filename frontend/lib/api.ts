import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
  headers: { "Content-Type": "application/json" },
});

// ── Company Profile ──────────────────────────────────────────
export async function getProfile() {
  try {
    const res = await api.get("/match/profile");
    return res.data;
  } catch (err: any) {
    if (err?.response?.status === 404) return null; // no profile yet → empty form
    throw err;
  }
}

export async function saveProfile(data: import("../types/profile").CompanyProfileCreate) {
  const res = await api.post("/match/profile", data);
  return res.data;
}

export default api;