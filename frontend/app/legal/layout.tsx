import Link from "next/link";

const styles = `
  .legal-page { font-family: 'DM Sans', -apple-system, sans-serif; background: #F5F4F0; min-height: 100vh; color: #0D1117; }
  .legal-nav { display: flex; align-items: center; justify-content: space-between; padding: 1.25rem 2rem; border-bottom: 0.5px solid rgba(13,17,23,0.1); background: #FFFFFF; }
  .legal-logo { font-size: 16px; font-weight: 500; letter-spacing: -0.3px; text-decoration: none; color: #0D1117; }
  .legal-tabs { display: flex; gap: 1.25rem; font-size: 13px; flex-wrap: wrap; }
  .legal-tabs a { color: #3A4250; text-decoration: none; }
  .legal-tabs a:hover { color: #0D1117; }
  .legal-body { max-width: 760px; margin: 0 auto; padding: 3rem 2rem 5rem; }
  .legal-body h1 { font-family: 'DM Serif Display', serif; font-size: 36px; margin-bottom: 0.5rem; }
  .legal-updated { color: #7A8394; font-size: 13px; margin-bottom: 2.5rem; }
  .legal-body h2 { font-size: 18px; font-weight: 600; margin: 2rem 0 0.75rem; }
  .legal-body p, .legal-body li { font-size: 14px; line-height: 1.7; color: #3A4250; }
  .legal-body ul, .legal-body ol { margin: 0.5rem 0 1rem 1.25rem; }
  .legal-body li { margin-bottom: 0.4rem; }
  .legal-body a.inline { color: #0F6E56; }
  .legal-notice { background: #FAEEDA; border: 1px solid rgba(186,117,23,0.25); color: #854F0B; font-size: 13px; padding: 0.9rem 1.1rem; border-radius: 8px; margin-bottom: 2rem; line-height: 1.6; }
`;

export default function LegalLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="legal-page">
      <style>{styles}</style>
      <nav className="legal-nav">
        <Link href="/" className="legal-logo">BidSight</Link>
        <div className="legal-tabs">
          <Link href="/legal/privacy">Privacy Policy</Link>
          <Link href="/legal/terms">Terms of Service</Link>
          <Link href="/legal/refund">Refund Policy</Link>
          <Link href="/legal/cookies">Cookie Policy</Link>
        </div>
      </nav>
      <div className="legal-body">{children}</div>
    </div>
  );
}
