import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center gap-6 p-8">
      <div className="text-center space-y-3">
        <h1 className="text-5xl font-bold tracking-tight">BidSight</h1>
        <p className="text-xl text-muted-foreground">
          See opportunities before everyone else.
        </p>
      </div>
      <Link href="/dashboard">
        <Button size="lg">Go to Dashboard</Button>
      </Link>
    </main>
  );
}