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

  // Anchor focus (minimal): when clicking a hash link, focus the target heading after scroll.
  document.addEventListener('click', (e) => {
    const a = e.target.closest && e.target.closest('a[href^="#"]');
    if (!a) return;
    const hash = a.getAttribute('href');
    if (!hash || hash.length < 2) return;
    const target = document.getElementById(hash.slice(1));
    if (!target) return;
    // Let native navigation happen; then focus.
    setTimeout(() => {
      if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
    }, 0);
  });

  // In mobile: allow CTA to open left drawer
  const openLeftCTA = qs('[data-ds-open-left]');
  if (openLeftCTA) {
    openLeftCTA.addEventListener('click', (e) => {
      // If desktop panels are visible, do nothing special.
      if (window.matchMedia('(min-width: 980px)').matches) return;
      e.preventDefault();
      openDrawer('left');
    });
  }

  // Language menu (simple; avoids bootstrap dependency)
  const langBtn = qs('[data-ds-menu="lang"]');
  const langMenu = langBtn ? qs('.ds-menu', langBtn.parentElement) : null;

  function closeLang() {
    if (!langBtn || !langMenu) return;
    langBtn.setAttribute('aria-expanded', 'false');
    langMenu.hidden = true;
  }

  if (langBtn && langMenu) {
    function openLang() {
      langBtn.setAttribute('aria-expanded', 'true');
      langMenu.hidden = false;
      const firstItem = qs('[role="menuitem"]', langMenu);
      firstItem?.focus();
    }

    langBtn.addEventListener('click', () => {
      const isOpen = langBtn.getAttribute('aria-expanded') === 'true';
      isOpen ? closeLang() : openLang();
    });

    // Arrow key navigation inside menu
    langMenu.addEventListener('keydown', (e) => {
      const items = qsa('[role="menuitem"]', langMenu);
      const idx = items.indexOf(document.activeElement);
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        items[(idx + 1) % items.length]?.focus();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        items[(idx - 1 + items.length) % items.length]?.focus();
      } else if (e.key === 'Tab') {
        closeLang();
      }
    });

    document.addEventListener('click', (e) => {
      if (!langBtn.contains(e.target) && !langMenu.contains(e.target)) closeLang();
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeLang();
    });
  }
})();
