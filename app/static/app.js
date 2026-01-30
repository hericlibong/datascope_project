// DataScope UI v2 (Phase 1) — minimal JS: drawers + a11y + simple menu
(() => {
  const qs = (sel, root = document) => root.querySelector(sel);
  const qsa = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const scrim = qs('[data-ds-scrim]');
  const left = qs('#ds-drawer-left');
  const right = qs('#ds-drawer-right');

  const bodyLock = (locked) => {
    document.documentElement.style.overflow = locked ? 'hidden' : '';
  };

  let lastFocus = null;

  function setExpanded(btn, expanded) {
    btn.setAttribute('aria-expanded', expanded ? 'true' : 'false');
  }

  function openDrawer(side) {
    const drawer = side === 'left' ? left : right;
    if (!drawer) return;
    lastFocus = document.activeElement;
    drawer.setAttribute('aria-hidden', 'false');
    if (scrim) scrim.setAttribute('aria-hidden', 'false');
    bodyLock(true);

    const btn = qs(`[data-ds-drawer-open="${side}"]`);
    if (btn) setExpanded(btn, true);

    // Focus first focusable element inside drawer, else drawer itself.
    const focusable = qsa('a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])', drawer)
      .filter(el => !el.hasAttribute('disabled'));
    (focusable[0] || drawer).focus?.();
  }

  function closeDrawers() {
    [left, right].forEach((drawer) => {
      if (!drawer) return;
      drawer.setAttribute('aria-hidden', 'true');
    });
    if (scrim) scrim.setAttribute('aria-hidden', 'true');
    bodyLock(false);

    qsa('[data-ds-drawer-open]').forEach(btn => setExpanded(btn, false));
    if (lastFocus && lastFocus.focus) lastFocus.focus();
    lastFocus = null;
  }

  qsa('[data-ds-drawer-open]').forEach((btn) => {
    btn.addEventListener('click', () => openDrawer(btn.getAttribute('data-ds-drawer-open')));
  });

  if (scrim) {
    scrim.addEventListener('click', closeDrawers);
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeDrawers();
  });

  // Language menu (simple; avoids bootstrap dependency)
  const langBtn = qs('[data-ds-menu="lang"]');
  const langMenu = langBtn ? qs('.ds-menu', langBtn.parentElement) : null;

  function closeLang() {
    if (!langBtn || !langMenu) return;
    langBtn.setAttribute('aria-expanded', 'false');
    langMenu.hidden = true;
  }

  if (langBtn && langMenu) {
    langBtn.addEventListener('click', () => {
      const isOpen = langBtn.getAttribute('aria-expanded') === 'true';
      langBtn.setAttribute('aria-expanded', isOpen ? 'false' : 'true');
      langMenu.hidden = isOpen;
    });

    document.addEventListener('click', (e) => {
      if (!langBtn.contains(e.target) && !langMenu.contains(e.target)) closeLang();
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeLang();
    });
  }
})();
