import TenderFeed from "@/components/tenders/TenderFeed";

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b px-6 py-4 flex items-center justify-between">
        <span className="text-xl font-semibold tracking-tight">BidSight</span>
        <nav className="flex gap-4 text-sm text-muted-foreground">
          <span className="text-foreground font-medium">Tenders</span>
          <a href="/dashboard/pipeline" className="hover:text-foreground">Pipeline</a>
          <a href="/dashboard/proposals" className="hover:text-foreground">Proposals</a>
        </nav>
      </header>
      <main className="max-w-6xl mx-auto px-6 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold">Opportunity Feed</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Latest tenders from GeM and CPPP portals
          </p>
        </div>
        <TenderFeed />
      </main>
    </div>
  );
}