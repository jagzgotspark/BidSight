import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <div style={{
      minHeight: "100vh",
      backgroundColor: "#0a0a0a",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
    }}>
      <SignUp />
    </div>
  );
}