// ==========================================================================
// ASANTE CHURCH INTERNATIONAL — main.js
// 1. Mobile hamburger menu (keyboard friendly)
// 2. Gentle fade-in of sections as you scroll
// ==========================================================================

document.addEventListener('DOMContentLoaded', function () {

  // ---------- 1. Mobile menu ----------
  const menuToggle = document.getElementById('menu-toggle');
  const mainNav = document.getElementById('main-nav');

  if (menuToggle && mainNav) {
    function setMenu(open) {
      mainNav.classList.toggle('is-open', open);
      menuToggle.classList.toggle('is-active', open);
      menuToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      menuToggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    }

    menuToggle.addEventListener('click', function () {
      setMenu(!mainNav.classList.contains('is-open'));
    });

    // Close the menu when a link is tapped
    mainNav.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        setMenu(false);
      });
    });

    // Close the menu with the Escape key, and return focus to the button
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && mainNav.classList.contains('is-open')) {
        setMenu(false);
        menuToggle.focus();
      }
    });
  }

  // ---------- 2. Fade-in on scroll ----------
  // Skipped for people who asked their device for reduced motion,
  // and for old browsers that don't support IntersectionObserver.
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if ('IntersectionObserver' in window && !reduceMotion) {
    document.documentElement.classList.add('js');

    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0, rootMargin: '0px 0px -8% 0px' });

    document.querySelectorAll('main .section, main .cta-section').forEach(function (el) {
      el.classList.add('reveal');
      observer.observe(el);
    });
  }
});