// Contact Sales page enhancements: query prefill, submit feedback, and conversion tracking
(function(){
  function $(sel){ return document.querySelector(sel); }
  function on(el, ev, fn){ el && el.addEventListener(ev, fn); }

  const inquirySelect = $('#inquiry_type');

  // Prefill inquiry from URL query (?inquiry=web, ai, app, support, or general)
  try {
    const params = new URLSearchParams(window.location.search);
    const q = params.get('inquiry');
    if (q && inquirySelect){
      const options = Array.from(inquirySelect.options);
      const match = options.find(o => (o.text || o.value).toLowerCase() === q.toLowerCase());
      if (match){
        inquirySelect.value = match.value || match.text;
      }
    }
  } catch(_){}

  const form = document.querySelector('form.contact-form');
  if (form){
    const submitButton = form.querySelector('.cf-submit');

    // The success flag is rendered only after the server accepts the inquiry.
    if (form.dataset.conversionReady === 'true' && typeof window.gtag === 'function') {
      window.gtag('event', 'generate_lead', {
        event_category: 'contact',
        event_label: 'contact_sales_form',
        value: 1
      });
    }

    on(form, 'submit', ()=>{
      if (submitButton){
        submitButton.disabled = true;
        submitButton.innerHTML = 'Sending… <i class="fa-solid fa-spinner fa-spin" aria-hidden="true"></i>';
      }
    });
  }
})();
