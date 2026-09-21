export default function RefundPolicy() {
  return (
    <>
      <h1>Refund Policy</h1>
      <p className="legal-updated">Last updated: 21 September 2026</p>

      <div className="legal-notice">
        This is a working draft, not a substitute for legal advice — review it
        against RBI/Razorpay merchant requirements and consumer protection rules
        before publishing.
      </div>

      <h2>1. How billing works today</h2>
      <p>
        BidSight&rsquo;s Professional plan is billed as a single payment that
        activates your plan for 30 days. It does not auto-renew — you&rsquo;ll need to
        come back and pay again to extend it once it expires. (We&rsquo;ll add
        auto-renewal and a cancellation flow before relying on this for real
        subscriptions — until then, nothing charges your card automatically.)
      </p>

      <h2>2. First-purchase refunds</h2>
      <p>
        If you&rsquo;re unhappy with your first Professional purchase, email
        [support@yourdomain.com] within 7 days of payment and we&rsquo;ll refund it in
        full, no questions asked. Refunds are issued to the original payment
        method via Razorpay and typically take 5&ndash;7 business days to reflect.
      </p>

      <h2>3. After 7 days</h2>
      <p>
        Since each payment simply activates a fixed 30-day period rather than an
        ongoing subscription, we don&rsquo;t offer partial or pro-rated refunds after
        the 7-day window — you get the full period you paid for either way.
      </p>

      <h2>4. Failed or duplicate charges</h2>
      <p>
        If a payment fails to activate your plan, or you&rsquo;re charged twice due to
        a technical error, email [support@yourdomain.com] with your payment ID and
        we&rsquo;ll refund the erroneous charge in full.
      </p>

      <h2>5. How to request a refund</h2>
      <p>
        Email [support@yourdomain.com] from the address on your account with your
        Razorpay payment ID (shown in your billing receipt). We aim to respond
        within 2 business days.
      </p>
    </>
  );
}
