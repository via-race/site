// VIA Race: the only JS on the site (~2 KB). No framework needed.

// Mobile menu
const toggle = document.querySelector('.menu-toggle');
const nav = document.getElementById('nav');
if (toggle && nav) {
  toggle.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
  });
  nav.addEventListener('click', (e) => { if (e.target.closest('a')) nav.classList.remove('open'); });
}

// Hero background video: only on wide screens, no reduced-motion, after page load
const video = document.querySelector('.hero__video[data-src]');
if (video && matchMedia('(min-width: 860px) and (prefers-reduced-motion: no-preference)').matches) {
  addEventListener('load', () => { video.src = video.dataset.src; }, { once: true });
} else if (video) {
  video.remove();
}

// Newsletter: POST the email (raw body) to the Cloudflare Worker, like the old site
document.querySelectorAll('form[data-newsletter]').forEach((form) => {
  const msg = form.querySelector('.msg');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = form.email.value.trim();
    msg.className = 'msg';
    msg.textContent = '…';
    try {
      const res = await fetch(form.action, { method: 'POST', body: email });
      if (!res.ok) throw new Error(res.status);
      msg.className = 'msg ok';
      msg.textContent = form.dataset.ok || 'Thanks! You\'re on the list.';
      form.reset();
    } catch {
      msg.className = 'msg err';
      msg.textContent = form.dataset.err || 'Something went wrong. Please try again.';
    }
  });
});

// Lightbox for [data-gallery] using native <dialog>
const galleries = document.querySelectorAll('[data-gallery]');
if (galleries.length) {
  const dlg = document.createElement('dialog');
  dlg.className = 'lightbox';
  const icon = (d) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="${d}"/></svg>`;
  dlg.innerHTML = `<figure><img alt=""></figure>
    <button class="lb-close" aria-label="Close">${icon('M6 6l12 12M18 6L6 18')}</button>
    <button class="lb-prev" aria-label="Previous">${icon('M15 5l-7 7 7 7')}</button>
    <button class="lb-next" aria-label="Next">${icon('M9 5l7 7-7 7')}</button>`;
  document.body.append(dlg);
  const img = dlg.querySelector('img');
  let items = [], i = 0;
  const show = (n) => { i = (n + items.length) % items.length; img.src = items[i].href; };
  galleries.forEach((g) => g.addEventListener('click', (e) => {
    const a = e.target.closest('a');
    if (!a) return;
    e.preventDefault();
    items = [...g.querySelectorAll('a')];
    show(items.indexOf(a));
    dlg.showModal();
  }));
  dlg.querySelector('.lb-close').onclick = () => dlg.close();
  dlg.querySelector('.lb-prev').onclick = () => show(i - 1);
  dlg.querySelector('.lb-next').onclick = () => show(i + 1);
  dlg.addEventListener('click', (e) => { if (e.target === dlg || e.target.tagName === 'FIGURE') dlg.close(); });
  dlg.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') show(i - 1);
    if (e.key === 'ArrowRight') show(i + 1);
  });
  let x0 = null;
  dlg.addEventListener('touchstart', (e) => { x0 = e.touches[0].clientX; }, { passive: true });
  dlg.addEventListener('touchend', (e) => {
    if (x0 === null) return;
    const dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 40) show(i + (dx < 0 ? 1 : -1));
    x0 = null;
  });
}
