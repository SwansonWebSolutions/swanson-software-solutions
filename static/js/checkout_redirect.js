// Redirect to Stripe Checkout for DNE/DNC.
// Cache form values locally before redirect; after Stripe returns, a bridge page posts them.
(() => {
  const stripeLinks = {
    // Set your Payment Link to redirect back to /stop-my-spam/submit/?paid=1
    // dne: 'https://buy.stripe.com/4gM14ofqafII3Xw7xDcEw02', # live
    dne: "https://buy.stripe.com/test_eVqfZi1zkeEE79I5pvcEw01",
    // Set your Payment Link to redirect back to /do-not-call-me/submit/?paid=1
    // dnc: 'https://buy.stripe.com/eVqfZi1zkeEE79I5pvcEw01', # live
    dnc: "https://buy.stripe.com/test_4gM14ofqafII3Xw7xDcEw02"
  };

  function val(id){ const el = document.getElementById(id); return el ? el.value.trim() : ''; }

  const dneBtn = document.getElementById('dneCheckout');
  if (dneBtn){
    dneBtn.addEventListener('click', () => {
      const form = dneBtn.closest('form');
      if (form && !form.checkValidity()) { form.reportValidity(); return; }
      const payload = {
        first_name: val('first_name'),
        last_name: val('last_name'),
        primary_email: val('primary_email'),
        secondary_email: val('secondary_email'),
        address1: val('address1'),
        address2: val('address2'),
        city: val('city'),
        region: val('region'),
        postal: val('postal'),
        country: val('country'),
        notes: val('notes'),
        acknowledge: (document.getElementById('dne_ack')?.checked ? 'true' : 'false'),
        t: Date.now(),
      };
      localStorage.setItem('dneForm', JSON.stringify(payload));
      window.location.href = stripeLinks.dne;
    });
  }

  const dncBtn = document.getElementById('dncCheckout');
  if (dncBtn){
    dncBtn.addEventListener('click', () => {
      const form = dncBtn.closest('form');
      if (form && !form.checkValidity()) { form.reportValidity(); return; }
      const payload = {
        full_name: val('full_name'),
        phone: val('phone'),
        notes: val('notes'),
        acknowledge: (document.getElementById('dnc_ack')?.checked ? 'true' : 'false'),
        t: Date.now(),
      };
      localStorage.setItem('dncForm', JSON.stringify(payload));
      window.location.href = stripeLinks.dnc;
    });
  }
})();
