/* LG Service — motion & interactions */
(function () {
  'use strict';

  var root = document.documentElement;
  var body = document.body;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia('(pointer: fine)').matches;

  var yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // Without GSAP (blocked CDN) or with reduced motion: show everything statically.
  if (!window.gsap || !window.ScrollTrigger || reduce) {
    root.classList.remove('js');
    var ld = document.querySelector('.loader');
    if (ld) ld.remove();
    initUI(null);
    return;
  }

  gsap.registerPlugin(ScrollTrigger);
  gsap.config({ nullTargetWarn: false });
  var $ = function (sel) { return document.querySelector(sel); };

  /* ---------- Smooth scroll ---------- */
  var lenis = null;
  if (window.Lenis) {
    lenis = new Lenis({ duration: 1.15, easing: function (t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); } });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add(function (time) { lenis.raf(time * 1000); });
    gsap.ticker.lagSmoothing(0);
  }

  /* ---------- Split headings into words ---------- */
  document.querySelectorAll('.split').forEach(function (el) {
    var words = el.textContent.trim().split(/\s+/);
    el.setAttribute('aria-label', el.textContent.trim());
    el.innerHTML = words.map(function (w) {
      return '<span class="w" aria-hidden="true"><span>' + w + '</span></span>';
    }).join(' ');
  });

  initUI(lenis);

  /* ---------- Loader → hero intro ---------- */
  var intro = gsap.timeline({ paused: true });
  intro
    .to('.hero__title .word', { y: 0, duration: 1.1, ease: 'expo.out', stagger: 0.06 })
    .fromTo('.hl', { '--hl': 0 }, { '--hl': 1, duration: .8, ease: 'expo.inOut' }, '-=.7')
    .to('.hero .eyebrow', { opacity: 1, duration: .6 }, '-=1')
    .fromTo('.hero .reveal-up', { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: .9, ease: 'power3.out', stagger: .1 }, '-=.8')
    .to('.hero__ctas', { opacity: 1, duration: .1 }, '<')
    .to('.hero__img', { clipPath: 'inset(0% 0 0 0 round 28px)', duration: 1.4, ease: 'expo.inOut' }, 0.1)
    .fromTo('.hero__img img', { scale: 1.3 }, { scale: 1, duration: 1.8, ease: 'expo.out' }, 0.3)
    .fromTo('.float-card', { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: .9, ease: 'back.out(1.6)', stagger: .15 }, '-=1');

  // Loader shown once per visit on the home page only, then the hero intro plays.
  var loader = $('.loader');
  var seen = false;
  try { seen = sessionStorage.getItem('lg-intro') === '1'; sessionStorage.setItem('lg-intro', '1'); } catch (e) {}
  if (loader && !seen) {
    if (lenis) lenis.stop();
    gsap.timeline({ onComplete: function () { loader.remove(); } })
      .to('.loader__bar span', { scaleX: 1, duration: .7, ease: 'power2.inOut' })
      .to('.loader__inner', { opacity: 0, y: -20, duration: .3 })
      .to('.loader__panel--1', { yPercent: -100, duration: .9, ease: 'expo.inOut' }, '-=.1')
      .to('.loader__panel--2', { yPercent: 100, duration: .9, ease: 'expo.inOut' }, '<')
      .add(function () { intro.play(); if (lenis) lenis.start(); }, '-=.7');
  } else {
    if (loader) loader.remove();
    if ($('.hero')) intro.play();
  }

  /* ---------- Header hide on scroll, progress bar ---------- */
  var header = document.querySelector('.header');
  ScrollTrigger.create({
    start: 0, end: 'max',
    onUpdate: function (self) {
      gsap.set('.progress', { scaleX: self.progress });
      var scrolled = self.scroll() > 200;
      header.classList.toggle('is-hidden', scrolled && self.direction === 1 && !body.classList.contains('menu-open'));
    }
  });

  /* ---------- Hero parallax ---------- */
  if ($('.hero')) {
  gsap.to('.hero__img img', { yPercent: 10, ease: 'none', scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true } });
  gsap.to('.hero__text', { y: -80, opacity: .3, ease: 'none', scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true } });
  gsap.to('.hero__glow', { scale: 1.4, x: -100, ease: 'none', scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true } });
  gsap.to('.float-card--a', { y: -60, ease: 'none', scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true } });
  gsap.to('.float-card--b', { y: -120, ease: 'none', scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true } });
  }

  /* ---------- Marquee reacts to scroll velocity ---------- */
  var track = $('.marquee__track');
  if (track) ScrollTrigger.create({
    trigger: '.marquee', start: 'top bottom', end: 'bottom top',
    onUpdate: function (self) {
      var v = gsap.utils.clamp(-6, 6, self.getVelocity() / 400);
      gsap.to(track, { skewX: -v, duration: .4, overwrite: true });
    }
  });
  if (track) gsap.fromTo('.marquee', { rotate: -4 }, { rotate: 1, ease: 'none', scrollTrigger: { trigger: '.marquee', start: 'top bottom', end: 'bottom top', scrub: true } });

  /* ---------- Generic reveals (outside hero) ---------- */
  gsap.utils.toArray('.split').forEach(function (el) {
    gsap.from(el.querySelectorAll('.w > span'), {
      yPercent: 110, duration: 1, ease: 'expo.out', stagger: .035,
      scrollTrigger: { trigger: el, start: 'top 85%' }
    });
  });

  gsap.utils.toArray('.reveal-up').forEach(function (el) {
    if (el.closest('.hero')) return;
    gsap.fromTo(el, { y: 40, opacity: 0 }, {
      y: 0, opacity: 1, duration: 1, ease: 'power3.out',
      scrollTrigger: { trigger: el, start: 'top 88%' }
    });
  });

  ScrollTrigger.batch('.reveal-card', {
    start: 'top 88%',
    onEnter: function (els) {
      gsap.fromTo(els, { y: 80, opacity: 0, rotateX: -12 }, { y: 0, opacity: 1, rotateX: 0, duration: 1.2, ease: 'expo.out', stagger: .12 });
    }
  });

  gsap.utils.toArray('.reveal-stagger').forEach(function (list) {
    gsap.fromTo(list.children, { y: 24, opacity: 0, scale: .96 }, {
      y: 0, opacity: 1, scale: 1, duration: .7, ease: 'back.out(1.7)', stagger: .07,
      scrollTrigger: { trigger: list, start: 'top 88%' }
    });
  });

  /* ---------- Image clip reveals + parallax ---------- */
  gsap.utils.toArray('.clip-reveal').forEach(function (el) {
    if (el.closest('.hero')) return;
    gsap.to(el, { clipPath: 'inset(0% 0 0 0 round 22px)', duration: 1.4, ease: 'expo.inOut', scrollTrigger: { trigger: el, start: 'top 85%' } });
    var img = el.querySelector('img');
    if (img) {
      gsap.fromTo(img, { yPercent: -6 }, { yPercent: 6, ease: 'none', scrollTrigger: { trigger: el, start: 'top bottom', end: 'bottom top', scrub: true } });
    }
  });
  gsap.fromTo('.metaux__bg', { yPercent: -8 }, { yPercent: 8, ease: 'none', scrollTrigger: { trigger: '.metaux', start: 'top bottom', end: 'bottom top', scrub: true } });
  gsap.utils.toArray('.year').forEach(function (el) {
    gsap.fromTo(el, { xPercent: 30 }, { xPercent: -10, ease: 'none', scrollTrigger: { trigger: el.parentNode, start: 'top bottom', end: 'bottom top', scrub: true } });
  });
  gsap.fromTo('.footer__giant', { yPercent: 40, letterSpacing: '0.04em' }, { yPercent: 0, letterSpacing: '-0.06em', ease: 'none', scrollTrigger: { trigger: '.footer', start: 'top bottom', end: 'bottom bottom', scrub: true } });
  gsap.utils.toArray('.sticker, .badge-round').forEach(function (el) {
    gsap.from(el, { scale: 0, rotate: -60, duration: 1, ease: 'back.out(1.8)', scrollTrigger: { trigger: el.parentNode, start: 'top 75%' } });
  });

  /* ---------- Debarras section rises over the previous ---------- */
  if ($('.debarras:not(.debarras--page)')) gsap.from('.debarras', { y: 80, ease: 'none', scrollTrigger: { trigger: '.debarras', start: 'top bottom', end: 'top 40%', scrub: true } });

  /* ---------- Counters ---------- */
  gsap.utils.toArray('.count').forEach(function (el) {
    var to = +el.dataset.to, from = +(el.dataset.from || 0), o = { v: from };
    el.textContent = from;
    gsap.to(o, {
      v: to, duration: 2, ease: 'power3.out',
      scrollTrigger: { trigger: el, start: 'top 90%' },
      onUpdate: function () { el.textContent = Math.round(o.v); }
    });
  });

  /* ---------- Steps progress line ---------- */
  var steps = gsap.utils.toArray('.step');
  var line = $('.steps__line span');
  if (line) {
  gsap.set(line, { '--p': 0 });
  ScrollTrigger.create({
    trigger: '.steps', start: 'top 75%', end: 'bottom 45%', scrub: true,
    onUpdate: function (self) {
      line.style.setProperty('--p', self.progress);
      steps.forEach(function (s, i) { s.classList.toggle('is-on', self.progress >= i / (steps.length - 1) - .02); });
    }
  });
  gsap.fromTo(steps, { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: .9, ease: 'power3.out', stagger: .12, scrollTrigger: { trigger: '.steps', start: 'top 85%' } });
  }

  /* ---------- Icon line drawing ---------- */
  document.querySelectorAll('.eng .draw').forEach(function (p) {
    var len = p.getTotalLength ? p.getTotalLength() : 200;
    gsap.set(p, { strokeDasharray: len, strokeDashoffset: len });
    gsap.to(p, { strokeDashoffset: 0, duration: 1.6, ease: 'power2.inOut', scrollTrigger: { trigger: p.closest('.eng'), start: 'top 85%' } });
  });

  /* ---------- Big phone number ---------- */
  if ($('.bigcta')) gsap.from('.bigcta__mask > span', { yPercent: 110, duration: 1.2, ease: 'expo.out', scrollTrigger: { trigger: '.bigcta', start: 'top 75%' } });

  /* ---------- Pointer effects (desktop only) ---------- */
  if (finePointer) {
    // Custom cursor
    var dot = document.querySelector('.cursor__dot');
    var ring = document.querySelector('.cursor__ring');
    var cursor = document.querySelector('.cursor');
    var dx = gsap.quickTo(dot, 'x', { duration: .1 }), dy = gsap.quickTo(dot, 'y', { duration: .1 });
    var rx = gsap.quickTo(ring, 'x', { duration: .45, ease: 'power3' }), ry = gsap.quickTo(ring, 'y', { duration: .45, ease: 'power3' });
    window.addEventListener('mousemove', function (e) { dx(e.clientX); dy(e.clientY); rx(e.clientX); ry(e.clientY); });
    document.querySelectorAll('a, button, .card, input, textarea, select, label').forEach(function (el) {
      el.addEventListener('mouseenter', function () { cursor.classList.add('is-hover'); });
      el.addEventListener('mouseleave', function () { cursor.classList.remove('is-hover'); });
    });

    // Magnetic buttons
    document.querySelectorAll('.magnetic').forEach(function (el) {
      var k = +(el.dataset.strength || .35);
      var mx = gsap.quickTo(el, 'x', { duration: .6, ease: 'elastic.out(1, .4)' });
      var my = gsap.quickTo(el, 'y', { duration: .6, ease: 'elastic.out(1, .4)' });
      el.addEventListener('mousemove', function (e) {
        var r = el.getBoundingClientRect();
        mx((e.clientX - r.left - r.width / 2) * k);
        my((e.clientY - r.top - r.height / 2) * k);
      });
      el.addEventListener('mouseleave', function () { mx(0); my(0); });
    });

    // 3D tilt cards
    document.querySelectorAll('.tilt').forEach(function (card) {
      var rX = gsap.quickTo(card, 'rotationX', { duration: .6, ease: 'power3' });
      var rY = gsap.quickTo(card, 'rotationY', { duration: .6, ease: 'power3' });
      card.addEventListener('mousemove', function (e) {
        var r = card.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width - .5, py = (e.clientY - r.top) / r.height - .5;
        rY(px * 10); rX(-py * 10);
      });
      card.addEventListener('mouseleave', function () { rX(0); rY(0); });
    });

    // Hero image follows pointer slightly
    var hero = $('.hero');
    if (hero) {
    var hx = gsap.quickTo('.hero__media', 'x', { duration: 1, ease: 'power3' });
    var hy = gsap.quickTo('.hero__media', 'y', { duration: 1, ease: 'power3' });
    hero.addEventListener('mousemove', function (e) {
      hx((e.clientX / innerWidth - .5) * -24);
      hy((e.clientY / innerHeight - .5) * -24);
    });
    }
  }

  window.addEventListener('load', function () { ScrollTrigger.refresh(); });

  /* ======================================================
     UI that works with or without animations
     ====================================================== */
  function initUI(lenis) {
    // Anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        var id = a.getAttribute('href');
        if (id.length < 2) return;
        var target = document.querySelector(id);
        if (!target) return;
        e.preventDefault();
        closeMenu();
        if (lenis) lenis.scrollTo(id === '#contenu' ? 0 : target, { offset: -20, duration: 1.4 });
        else target.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' });
      });
    });

    // Mobile menu
    var burger = document.querySelector('.burger');
    var menu = document.querySelector('.menu');
    function closeMenu() {
      body.classList.remove('menu-open');
      burger.setAttribute('aria-expanded', 'false');
      menu.setAttribute('aria-hidden', 'true');
      if (lenis) lenis.start();
    }
    burger.addEventListener('click', function () {
      var open = !body.classList.contains('menu-open');
      if (!open) return closeMenu();
      body.classList.add('menu-open');
      burger.setAttribute('aria-expanded', 'true');
      menu.setAttribute('aria-hidden', 'false');
      if (lenis) lenis.stop();
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeMenu(); });

    // Contact form → opens the visitor's mail app with a prefilled message
    var form = document.getElementById('contact-form');
    if (!form) return;
    var msg = form.querySelector('.form__msg');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var ok = true;
      form.querySelectorAll('[required]').forEach(function (f) {
        var bad = f.type === 'checkbox' ? !f.checked : !f.value.trim() || (f.type === 'email' && !/^\S+@\S+\.\S+$/.test(f.value));
        var wrap = f.closest('.field');
        if (wrap) wrap.classList.toggle('is-error', bad);
        if (bad) ok = false;
      });
      if (!ok) {
        msg.textContent = 'Merci de remplir les champs obligatoires.';
        msg.classList.add('is-error');
        if (window.gsap) gsap.fromTo(form, { x: -8 }, { x: 0, duration: .5, ease: 'elastic.out(1, .3)' });
        return;
      }
      var d = new FormData(form);
      var subject = 'Demande de devis – ' + d.get('type');
      var bodyTxt = 'Nom : ' + d.get('name') + '\nE-mail : ' + d.get('email') + '\nTéléphone : ' + d.get('tel') +
        '\nBesoin : ' + d.get('type') + '\n\n' + d.get('message');
      window.location.href = 'mailto:contact@debarras-lg-service.fr?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(bodyTxt);
      msg.classList.remove('is-error');
      msg.textContent = 'Merci de nous avoir contactés. Votre messagerie va s\'ouvrir pour envoyer la demande.';
    });
  }
})();
