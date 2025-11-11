// Mobile drawer + accordion controller
(function () {
  const drawer = document.getElementById('drawer');
  const backdrop = document.getElementById('backdrop');
  const openBtn = document.getElementById('openMenu');
  const closeBtn = document.getElementById('closeMenu');

  const servicesBtn = document.getElementById('servicesToggle');
  const servicesMenu = document.getElementById('servicesMenu');

  const mobileServicesBtn = document.getElementById('mobileServicesToggle');
  const mobileServices = document.getElementById('mobileServices');

  // Helpers
  const openDrawer = () => {
    drawer.classList.add('open');
    drawer.setAttribute('aria-hidden', 'false');
    backdrop.hidden = false;
    requestAnimationFrame(() => backdrop.classList.add('show'));
    document.documentElement.style.overflow = 'hidden';
    openBtn?.setAttribute('aria-expanded', 'true');
  };

  const closeDrawer = () => {
    drawer.classList.remove('open');
    drawer.setAttribute('aria-hidden', 'true');
    backdrop.classList.remove('show');
    setTimeout(() => (backdrop.hidden = true), 220);
    document.documentElement.style.overflow = '';
    openBtn?.setAttribute('aria-expanded', 'false');
  };

  // Wire up drawer
  openBtn?.addEventListener('click', openDrawer);
  closeBtn?.addEventListener('click', closeDrawer);
  backdrop?.addEventListener('click', closeDrawer);
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeDrawer();
  });

  // Desktop "Services" toggle (click to stick open; hover CSS still works)
  if (servicesBtn && servicesMenu) {
    servicesBtn.addEventListener('click', () => {
      const isOpen = servicesMenu.classList.toggle('open');
      servicesBtn.setAttribute('aria-expanded', String(isOpen));
    });
    document.addEventListener('click', (e) => {
      if (!servicesMenu.contains(e.target) && !servicesBtn.contains(e.target)) {
        servicesMenu.classList.remove('open');
        servicesBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // Mobile services accordion
  if (mobileServicesBtn && mobileServices) {
    mobileServicesBtn.addEventListener('click', () => {
      const isHidden = mobileServices.hasAttribute('hidden');
      if (isHidden) {
        mobileServices.removeAttribute('hidden');
        mobileServicesBtn.setAttribute('aria-expanded', 'true');
      } else {
        mobileServices.setAttribute('hidden', '');
        mobileServicesBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }
})();
