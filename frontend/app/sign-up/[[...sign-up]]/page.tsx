import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <div style={{
      minHeight: "100vh",
      backgroundColor: "#0a0a0a",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      gap: "1rem",
    }}>
      <SignUp />
      <p style={{ fontSize: 12, color: "#8a8a8a", maxWidth: 340, textAlign: "center", lineHeight: 1.6 }}>
        By creating an account, you agree to BidSight&rsquo;s{" "}
        <a href="/legal/terms" style={{ color: "#5FD3A6" }}>Terms of Service</a> and{" "}
        <a href="/legal/privacy" style={{ color: "#5FD3A6" }}>Privacy Policy</a>.
      </p>
    </div>
  );
}