// Mobile drawer logic
const openBtn = document.getElementById('openMenu');
const closeBtn = document.getElementById('closeMenu');
const drawer = document.getElementById('drawer');
const backdrop = document.getElementById('backdrop');

function openDrawer() {
  drawer.classList.add('open');
  drawer.setAttribute('aria-hidden', 'false');
  backdrop.classList.add('show');
  backdrop.hidden = false;
  document.body.style.overflow = 'hidden';
}
function closeDrawer() {
  drawer.classList.remove('open');
  drawer.setAttribute('aria-hidden', 'true');
  backdrop.classList.remove('show');
  setTimeout(() => { backdrop.hidden = true; }, 200);
  document.body.style.overflow = '';
}

openBtn?.addEventListener('click', openDrawer);
closeBtn?.addEventListener('click', closeDrawer);
backdrop?.addEventListener('click', closeDrawer);

// Respect reduced motion
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  document.querySelectorAll('*').forEach(el => el.style.setProperty('transition', 'none', 'important'));
}
