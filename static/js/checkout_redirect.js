// Redirect to Stripe Checkout for DNE.
// Cache form values locally before redirect; after Stripe returns, a bridge page posts them.
(() => {
  const stripeLinks = {
    // Set your Payment Link to redirect back to /stop-my-spam/submit/?paid=1
    // The template sets window.__STRIPE_LINKS.dne based on environment.
    dne: (window.__STRIPE_LINKS && window.__STRIPE_LINKS.dne) || "https://buy.stripe.com/test_eVqfZi1zkeEE79I5pvcEw01",
  };

  function val(id){ const el = document.getElementById(id); return el ? el.value.trim() : ''; }

  const dneBtn = document.getElementById('dneCheckout');
  if (dneBtn){
    dneBtn.addEventListener('click', () => {
      const form = dneBtn.closest('form');
      if (form && !form.checkValidity()) { form.reportValidity(); return; }
      const normalize = (val) => (val || '').replace(/\D/g, '');
      const primary_phone = normalize(val('primary_phone'));
      const secondary_phone = normalize(val('secondary_phone'));
      if (primary_phone.length !== 10) {
        alert('Primary Phone must be 10 digits (numbers only).');
        return;
      }
      if (secondary_phone && secondary_phone.length !== 10) {
        alert('Secondary Phone must be 10 digits (numbers only).');
        return;
      }
      const payload = {
        first_name: val('first_name'),
        last_name: val('last_name'),
        primary_email: val('primary_email'),
        secondary_email: val('secondary_email'),
        primary_phone,
        secondary_phone,
        address1: val('address1'),
        address2: val('address2'),
        city: val('city'),
        region: val('region'),
        postal: val('postal'),
        country: val('country'),
        notes: val('notes'),
        acknowledge: (document.getElementById('dne_ack')?.checked ? 'true' : 'false'),
        weekly_status_opt_in: (document.getElementById('dne_weekly_opt_in')?.checked ? 'true' : 'false'),
        t: Date.now(),
      };
      localStorage.setItem('dneForm', JSON.stringify(payload));
      window.location.href = stripeLinks.dne;
    });
  }

})();
