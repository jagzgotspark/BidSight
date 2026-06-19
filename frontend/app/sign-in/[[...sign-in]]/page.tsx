import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <div style={{
      minHeight: "100vh",
      backgroundColor: "#0a0a0a",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
    }}>
      <SignIn />
    </div>
  );
}