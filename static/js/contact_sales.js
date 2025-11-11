// Contact Sales page enhancements: phone mask, country code, query prefill
(function(){
  function $(sel){ return document.querySelector(sel); }
  function on(el, ev, fn){ el && el.addEventListener(ev, fn); }

  const phoneInput = $('#phone');
  const countrySelect = $('#country_code');
  const inquirySelect = $('#inquiry_type');

  // Add class for spacing above message if not present via markup
  const msg = $('#message');
  if (msg && msg.closest('.field')) {
    msg.closest('.field').classList.add('field--message');
  }

  // US phone mask: (XXX)-XXX-XXXX, keep only first 10 digits
  function formatUS(value){
    const digits = (value || '').replace(/\D+/g,'').slice(0,10);
    const p1 = digits.slice(0,3);
    const p2 = digits.slice(3,6);
    const p3 = digits.slice(6,10);
    let out = '';
    if (p1) out = `(${p1}`;
    if (p1.length === 3) out = `(${p1})`;
    if (p2) out += `-${p2}`;
    if (p3) out += `-${p3}`;
    return out;
  }

  if (phoneInput){
    on(phoneInput, 'input', (e)=>{
      const caretToEnd = document.activeElement === phoneInput && phoneInput.selectionStart === phoneInput.value.length;
      const v = e.target.value;
      const formatted = formatUS(v);
      e.target.value = formatted;
      if (caretToEnd) {
        // keep caret at end for smoother typing
        const len = e.target.value.length;
        e.target.setSelectionRange(len,len);
      }
    });
  }

  // Prefill inquiry from URL query (?inquiry=Shopify etc.)
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

  // On submit, prefix phone with country code (e.g., "+1 (555)-123-4567")
  const form = document.querySelector('form.contact-form');
  if (form){
    on(form, 'submit', ()=>{
      if (phoneInput){
        const code = countrySelect ? (countrySelect.value || '').replace('-CA','') : '';
        const num = phoneInput.value.trim();
        if (code && num){ phoneInput.value = `${code} ${num}`; }
      }
    });
  }
})();

