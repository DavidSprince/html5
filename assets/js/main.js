/**
 * ReelsHub Vault — vanilla JS behaviours
 * (mirrors the interactivity of the original React build, with zero
 * framework/build-step dependency — plain HTML5 + CSS + JS.)
 */
(function () {
  'use strict';

  // ---------------------------------------------------------------------
  // Footer year
  // ---------------------------------------------------------------------
  var yearEl = document.getElementById('footer-year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // ---------------------------------------------------------------------
  // Header: scroll shadow
  // ---------------------------------------------------------------------
  var header = document.getElementById('site-header');
  if (header) {
    var onScroll = function () {
      if (window.scrollY > 8) {
        header.classList.add('shadow-sm', 'border-slate-200');
      } else {
        header.classList.remove('shadow-sm', 'border-slate-200');
      }
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // ---------------------------------------------------------------------
  // Mobile menu toggle
  // ---------------------------------------------------------------------
  var menuBtn = document.getElementById('mobile-menu-btn');
  var mobileMenu = document.getElementById('mobile-menu');
  var iconMenu = document.getElementById('icon-menu');
  var iconClose = document.getElementById('icon-close');
  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener('click', function () {
      var isOpen = mobileMenu.classList.toggle('open');
      iconMenu.classList.toggle('hidden', isOpen);
      iconClose.classList.toggle('hidden', !isOpen);
    });
  }

  // ---------------------------------------------------------------------
  // Scroll-reveal animations (progressive enhancement — IntersectionObserver)
  // ---------------------------------------------------------------------
  if ('IntersectionObserver' in window) {
    var revealObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            revealObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    );
    document.querySelectorAll('.reveal, .stagger').forEach(function (el) {
      revealObserver.observe(el);
    });
  } else {
    // No IntersectionObserver support — just show everything immediately.
    document.querySelectorAll('.reveal, .stagger').forEach(function (el) {
      el.classList.add('is-visible');
    });
  }

  // ---------------------------------------------------------------------
  // Bundles page: live search + category filter (client-side, no reload)
  // ---------------------------------------------------------------------
  if (window.__BUNDLES_PAGE__) {
    var grid = document.getElementById('bundle-grid');
    var emptyState = document.getElementById('empty-state');
    var searchInput = document.getElementById('search-input');
    var clearBtn = document.getElementById('clear-search');
    var filterBtns = document.querySelectorAll('.filter-btn');
    var cards = grid ? Array.prototype.slice.call(grid.children) : [];
    var activeGroup = 'all';

    // Pre-fill search box from ?q= query param
    var params = new URLSearchParams(window.location.search);
    var initialQuery = params.get('q') || '';
    var initialGroup = params.get('group');
    if (initialQuery && searchInput) searchInput.value = initialQuery;
    if (initialGroup) {
      var match = Array.prototype.find.call(filterBtns, function (b) {
        return b.dataset.group === initialGroup.toLowerCase();
      });
      if (match) activeGroup = match.dataset.group;
    }

    function applyFilters() {
      var query = (searchInput ? searchInput.value : '').trim().toLowerCase();
      var visibleCount = 0;
      cards.forEach(function (card) {
        var matchesGroup = activeGroup === 'all' || card.dataset.group === activeGroup;
        var haystack = (card.dataset.title + ' ' + card.dataset.group + ' ' + card.dataset.tags);
        var matchesQuery = !query || haystack.indexOf(query) !== -1;
        var visible = matchesGroup && matchesQuery;
        card.style.display = visible ? '' : 'none';
        if (visible) visibleCount++;
      });
      if (emptyState) emptyState.classList.toggle('hidden', visibleCount !== 0);
      if (clearBtn) clearBtn.classList.toggle('hidden', !query);
    }

    filterBtns.forEach(function (btn) {
      if (btn.dataset.group === activeGroup) {
        btn.classList.add('active', 'bg-indigo-600', 'text-white');
        btn.classList.remove('bg-white', 'border', 'border-slate-200', 'text-slate-600');
      }
      btn.addEventListener('click', function () {
        filterBtns.forEach(function (b) {
          b.classList.remove('active', 'bg-indigo-600', 'text-white');
          b.classList.add('bg-white', 'border', 'border-slate-200', 'text-slate-600');
        });
        btn.classList.add('active', 'bg-indigo-600', 'text-white');
        btn.classList.remove('bg-white', 'border', 'border-slate-200', 'text-slate-600');
        activeGroup = btn.dataset.group;
        applyFilters();
      });
    });

    if (searchInput) {
      searchInput.addEventListener('input', applyFilters);
    }
    if (clearBtn) {
      clearBtn.addEventListener('click', function () {
        searchInput.value = '';
        applyFilters();
      });
    }
    var searchForm = document.getElementById('search-form');
    if (searchForm) {
      searchForm.addEventListener('submit', function (e) {
        e.preventDefault();
        applyFilters();
      });
    }

    applyFilters();
  }

  // ---------------------------------------------------------------------
  // Contact form (static demo — wire up to Formspree/Getform/EmailJS or a
  // serverless function to actually receive messages)
  // ---------------------------------------------------------------------
  var contactForm = document.getElementById('contact-form');
  var contactSuccess = document.getElementById('contact-success');
  if (contactForm) {
    contactForm.addEventListener('submit', function (e) {
      e.preventDefault();
      // TODO: replace with a real fetch() call to your form backend, e.g.:
      // fetch('https://formspree.io/f/your-id', { method: 'POST', body: new FormData(contactForm) })
      contactForm.classList.add('hidden');
      if (contactSuccess) contactSuccess.classList.remove('hidden');
    });
  }
})();
