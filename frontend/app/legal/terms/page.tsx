export default function TermsOfService() {
  return (
    <>
      <h1>Terms of Service</h1>
      <p className="legal-updated">Last updated: 21 September 2026</p>

      <div className="legal-notice">
        This is a working draft, not a substitute for legal advice. Fields marked
        [IN BRACKETS] need your actual business details filled in, and we&rsquo;d
        recommend a lawyer review this before it goes live — especially the
        liability and disclaimer sections given this product surfaces government
        procurement data.
      </div>

      <h2>1. Agreement</h2>
      <p>
        By creating a BidSight account, you agree to these Terms. If you&rsquo;re using
        BidSight on behalf of a company, you&rsquo;re confirming you have authority to
        bind that company to these Terms.
      </p>

      <h2>2. What BidSight is</h2>
      <p>
        BidSight aggregates publicly available government tender listings (from
        portals including GeM and CPPP) and uses AI to help you evaluate fit and
        draft proposals. We are not affiliated with any government body, and we do
        not submit bids on your behalf.
      </p>

      <h2>3. Accuracy disclaimer</h2>
      <p>
        Tender data is scraped from public sources and may be incomplete, delayed,
        or out of date. AI-generated match scores, summaries, and proposal drafts
        are decision support, not professional or legal advice — always verify
        deadlines, eligibility, and terms directly on the source portal before
        bidding. We are not liable for bids lost, missed, or rejected due to
        reliance on BidSight&rsquo;s data or AI output.
      </p>

      <h2>4. Your account</h2>
      <ul>
        <li>You&rsquo;re responsible for keeping your login credentials secure.</li>
        <li>You must provide accurate information in your company profile.</li>
        <li>One account per company unless you&rsquo;re on a plan that supports teams.</li>
      </ul>

      <h2>5. Acceptable use</h2>
      <p>You agree not to:</p>
      <ul>
        <li>Scrape, resell, or redistribute BidSight&rsquo;s aggregated data at scale.</li>
        <li>Reverse-engineer or attempt to bypass rate limits or access controls.</li>
        <li>Use the platform for any unlawful purpose or to submit fraudulent bids.</li>
      </ul>

      <h2>6. Subscriptions &amp; billing</h2>
      <p>
        Paid plans renew monthly via Razorpay. See our <a className="inline" href="/legal/refund">Refund Policy</a> for
        cancellation and refund terms. Prices are shown in INR and may change with
        30 days&rsquo; notice to active subscribers.
      </p>

      <h2>7. Termination</h2>
      <p>
        You may cancel anytime from your billing settings. We may suspend or
        terminate accounts that violate these Terms, with notice where practical.
      </p>

      <h2>8. Limitation of liability</h2>
      <p>
        To the maximum extent permitted by law, BidSight&rsquo;s total liability for
        any claim arising from your use of the platform is limited to the amount
        you paid us in the 3 months preceding the claim. We are not liable for
        indirect, incidental, or consequential damages, including lost business
        opportunities.
      </p>

      <h2>9. Governing law</h2>
      <p>These Terms are governed by the laws of India, with disputes subject to the courts of [YOUR CITY].</p>

      <h2>10. Contact</h2>
      <p>[YOUR LEGAL ENTITY NAME] · [support@yourdomain.com]</p>
    </>
  );
}
