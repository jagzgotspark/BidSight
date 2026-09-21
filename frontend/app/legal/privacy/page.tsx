export default function PrivacyPolicy() {
  return (
    <>
      <h1>Privacy Policy</h1>
      <p className="legal-updated">Last updated: 21 September 2026</p>

      <div className="legal-notice">
        This is a working draft, not a substitute for legal advice. Fields marked
        [IN BRACKETS] need your actual business details filled in before this goes
        live, and we'd recommend a lawyer review it against the Digital Personal
        Data Protection Act, 2023 (India) and any other jurisdictions you serve
        before publishing.
      </div>

      <p>
        BidSight (&ldquo;we&rdquo;, &ldquo;us&rdquo;) operates an AI-assisted tender discovery
        platform for Indian government procurement. This policy explains what
        personal data we collect, why, and how you can control it.
      </p>

      <h2>1. Who we are</h2>
      <p>
        Data controller: [YOUR LEGAL ENTITY NAME], [REGISTERED ADDRESS], India.
        Contact for privacy matters: [privacy@yourdomain.com].
      </p>

      <h2>2. Data we collect</h2>
      <ul>
        <li><strong>Account data</strong> — name and email address, collected via Clerk when you sign up.</li>
        <li><strong>Company profile</strong> — services offered, tech stack, certifications, team size, geography, and budget range, which you enter voluntarily to get AI match scores. We do not ask for or store your GSTIN, PAN, or any government ID.</li>
        <li><strong>Bid tracking &amp; proposals</strong> — pipeline notes, past-project descriptions, and proposal drafts you create inside the product.</li>
        <li><strong>Billing data</strong> — plan, subscription status, and payment status. Card and UPI details are entered directly into Razorpay&rsquo;s checkout and never touch our servers.</li>
        <li><strong>Usage &amp; technical data</strong> — login timestamps and basic request logs for security and debugging.</li>
      </ul>
      <p>We do not collect phone numbers, physical addresses, or government ID numbers, and we don&rsquo;t run any analytics or advertising trackers on the product today (see our <a className="inline" href="/legal/cookies">Cookie Policy</a>).</p>

      <h2>3. How we use your data</h2>
      <ul>
        <li>To operate your account and show you tender opportunities.</li>
        <li>To generate AI match scores and draft proposals — this means sending your company profile and a tender&rsquo;s public details to our AI provider (Groq) as part of that request. Groq does not receive your account email or payment details.</li>
        <li>To send deadline and match alerts to your email, when enabled.</li>
        <li>To process payments and manage your subscription via Razorpay.</li>
        <li>To secure the platform and investigate abuse.</li>
      </ul>

      <h2>4. Who we share it with</h2>
      <p>We don&rsquo;t sell your data. We share the minimum necessary with the processors that make the product work:</p>
      <ul>
        <li><strong>Clerk</strong> — authentication and session management.</li>
        <li><strong>Razorpay</strong> — payment processing (PCI-DSS compliant; we never see full card numbers).</li>
        <li><strong>Groq</strong> — AI inference for match scoring and proposal drafting.</li>
        <li><strong>Google (Gmail SMTP)</strong> — delivery of alert emails.</li>
        <li><strong>Render / Vercel</strong> — infrastructure hosting for our backend and frontend.</li>
      </ul>
      <p>Some of these processors may process data outside India. We only use providers with their own data-protection commitments in place.</p>

      <h2>5. Data retention</h2>
      <p>
        We keep account and profile data for as long as your account is active, plus
        [90 days] afterward in case you return, then delete it. Tender data itself is
        public government procurement information, not personal data, and is retained
        for platform functionality regardless of account status.
      </p>

      <h2>6. Your rights</h2>
      <p>Under the DPDP Act, 2023 and equivalent laws, you can:</p>
      <ul>
        <li>Access the personal data we hold about you.</li>
        <li>Correct inaccurate data.</li>
        <li>Request erasure of your account and associated data.</li>
        <li>Withdraw consent for optional processing (e.g. AI scoring) at any time — this may limit some features.</li>
      </ul>
      <p>To exercise any of these, email [privacy@yourdomain.com]. We&rsquo;ll respond within 30 days.</p>

      <h2>7. Grievance Officer</h2>
      <p>[NAME], [designation], reachable at [grievance@yourdomain.com], for complaints about how we handle your data.</p>

      <h2>8. Children</h2>
      <p>BidSight is a B2B product not directed at anyone under 18.</p>

      <h2>9. Changes to this policy</h2>
      <p>We&rsquo;ll post updates here and change the &ldquo;Last updated&rdquo; date above. Material changes will be emailed to active users.</p>
    </>
  );
}
