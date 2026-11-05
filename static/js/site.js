/* Grupo Nordeste — interações do site (sem dependências) */
(function () {
  "use strict";
  var doc = document.documentElement;
  var body = document.body;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var store = {
    get: function (k, s) { try { return (s ? sessionStorage : localStorage).getItem(k); } catch (e) { return null; } },
    set: function (k, v, s) { try { (s ? sessionStorage : localStorage).setItem(k, v); } catch (e) {} }
  };

  /* ---------------------------------------------------------- cabeçalho */
  var hdr = document.querySelector(".hdr");
  if (hdr) {
    var over = hdr.classList.contains("hdr--over");
    var onScroll = function () {
      var stuck = window.scrollY > (over ? 120 : 10);
      if (over) hdr.classList.toggle("is-stuck", stuck);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ---------------------------------------------------------- menu mobile */
  var burger = document.querySelector(".hdr__burger");
  if (burger) {
    var toggle = function (open) {
      body.classList.toggle("menu-open", open);
      body.classList.toggle("no-scroll", open);
      burger.setAttribute("aria-expanded", open);
      burger.setAttribute("aria-label", open ? "Fechar menu" : "Abrir menu");
    };
    burger.addEventListener("click", function () { toggle(!body.classList.contains("menu-open")); });
    document.querySelectorAll(".nav a").forEach(function (a) { a.addEventListener("click", function () { toggle(false); }); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") toggle(false); });
  }

  /* ---------------------------------------------------------- animação ao rolar */
  var reveals = document.querySelectorAll("[data-reveal]");
  if ("IntersectionObserver" in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }

  /* ---------------------------------------------------------- contadores */
  var counters = document.querySelectorAll("[data-count]");
  var runCount = function (el) {
    var end = parseInt(el.getAttribute("data-count"), 10) || 0;
    if (reduce) { el.textContent = end; return; }
    var t0 = null, dur = 1800;
    var step = function (t) {
      if (!t0) t0 = t;
      var p = Math.min((t - t0) / dur, 1);
      el.textContent = Math.round(end * (1 - Math.pow(1 - p, 4)));
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };
  if ("IntersectionObserver" in window) {
    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { runCount(en.target); co.unobserve(en.target); } });
    }, { threshold: 0.5 });
    counters.forEach(function (el) { co.observe(el); });
  }

  /* ---------------------------------------------------------- slides do banner */
  var slides = document.querySelectorAll(".hero__slide");
  if (slides.length > 1 && !reduce) {
    var cur = 0;
    setInterval(function () {
      slides[cur].classList.remove("on");
      cur = (cur + 1) % slides.length;
      slides[cur].classList.add("on");
    }, 6500);
  }

  /* ---------------------------------------------------------- toasts */
  document.querySelectorAll(".toast").forEach(function (t, i) {
    setTimeout(function () { t.classList.add("out"); setTimeout(function () { t.remove(); }, 450); }, 6000 + i * 400);
  });

  /* ---------------------------------------------------------- faixa de aviso */
  document.querySelectorAll("[data-faixa]").forEach(function (f) {
    var k = "faixa:" + f.getAttribute("data-faixa");
    if (store.get(k, true)) { f.classList.add("is-hidden"); return; }
    var x = f.querySelector(".faixa__x");
    if (x) x.addEventListener("click", function () { f.classList.add("is-hidden"); store.set(k, "1", true); });
  });

  /* ---------------------------------------------------------- modais de aviso */
  var modais = Array.prototype.slice.call(document.querySelectorAll("[data-modal]"));
  var lastFocus = null;
  var fechar = function (m) {
    m.classList.add("closing");
    setTimeout(function () {
      m.hidden = true; m.classList.remove("closing"); body.classList.remove("no-scroll");
      if (lastFocus) lastFocus.focus();
      abrirProximo();
    }, 280);
  };
  var marcar = function (m) {
    var k = "modal:" + m.getAttribute("data-modal"), f = m.getAttribute("data-freq");
    if (f === "sessao") store.set(k, "1", true);
    if (f === "uma-vez") store.set(k, "1", false);
  };
  var podeAbrir = function (m) {
    var k = "modal:" + m.getAttribute("data-modal"), f = m.getAttribute("data-freq");
    if (f === "sessao") return !store.get(k, true);
    if (f === "uma-vez") return !store.get(k, false);
    return true;
  };
  var fila = modais.filter(podeAbrir);
  var abrirProximo = function () {
    var m = fila.shift();
    if (!m) return;
    lastFocus = document.activeElement;
    m.hidden = false; body.classList.add("no-scroll"); marcar(m);
    var x = m.querySelector(".modal__x"); if (x) x.focus();
  };
  modais.forEach(function (m) {
    m.querySelectorAll("[data-fechar]").forEach(function (b) { b.addEventListener("click", function () { fechar(m); }); });
    m.addEventListener("keydown", function (e) { if (e.key === "Escape") fechar(m); });
  });
  if (fila.length) setTimeout(abrirProximo, 1200);

  /* ---------------------------------------------------------- filtros (unidades / vagas) */
  var semResultado = document.querySelector(".empty-filter");
  var aplicarFiltro = function () {
    var q = (document.querySelector("[data-filter-input]") || {}).value || "";
    var ufBtn = document.querySelector("[data-filter-uf].on");
    var uf = ufBtn ? ufBtn.getAttribute("data-filter-uf") : "";
    q = q.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().trim();
    var vis = 0;
    document.querySelectorAll(".ucard[data-uf]").forEach(function (c) {
      var nome = c.textContent.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
      var ok = (!q || nome.indexOf(q) > -1) && (!uf || c.getAttribute("data-uf") === uf);
      c.classList.toggle("is-filtered", !ok);
      if (ok) vis++;
    });
    if (semResultado) semResultado.hidden = vis > 0;
  };
  var inp = document.querySelector("[data-filter-input]");
  if (inp) inp.addEventListener("input", aplicarFiltro);
  document.querySelectorAll("[data-filter-uf]").forEach(function (b) {
    b.addEventListener("click", function () {
      document.querySelectorAll("[data-filter-uf]").forEach(function (o) { o.classList.remove("on"); });
      b.classList.add("on"); aplicarFiltro();
    });
  });
  document.querySelectorAll("[data-filter-local]").forEach(function (b) {
    b.addEventListener("click", function () {
      document.querySelectorAll("[data-filter-local]").forEach(function (o) { o.classList.remove("on"); });
      b.classList.add("on");
      var l = b.getAttribute("data-filter-local");
      document.querySelectorAll(".vgrid .vcard[data-local]").forEach(function (c) {
        c.classList.toggle("is-filtered", !!l && c.getAttribute("data-local") !== l);
      });
    });
  });

  /* ---------------------------------------------------------- upload de currículo */
  document.querySelectorAll("[data-drop]").forEach(function (d) {
    var input = d.querySelector("input[type=file]"), txt = d.querySelector(".drop__txt");
    var orig = txt.innerHTML;
    input.addEventListener("change", function () {
      var f = input.files && input.files[0];
      d.classList.toggle("has-file", !!f);
      txt.innerHTML = f ? "<b>" + f.name.replace(/[<>&]/g, "") + "</b> (" + Math.round(f.size / 1024) + " KB)" : orig;
    });
    ["dragenter", "dragover"].forEach(function (ev) { d.addEventListener(ev, function () { d.classList.add("is-over"); }); });
    ["dragleave", "drop"].forEach(function (ev) { d.addEventListener(ev, function () { d.classList.remove("is-over"); }); });
  });

  /* ---------------------------------------------------------- denúncia anônima */
  var anon = document.querySelector("input[name=anonima]");
  var ident = document.querySelector("[data-identificacao]");
  if (anon && ident) {
    var upd = function () { ident.hidden = anon.checked; };
    anon.addEventListener("change", upd); upd();
  }

  /* ---------------------------------------------------------- envio: evita clique duplo */
  document.querySelectorAll("[data-form]").forEach(function (f) {
    f.addEventListener("submit", function () {
      var b = f.querySelector("button[type=submit]");
      if (b) { b.disabled = true; b.style.opacity = ".7"; b.firstChild.textContent = "Enviando… "; }
    });
  });

  /* ---------------------------------------------------------- galeria (lightbox) */
  document.querySelectorAll("[data-lightbox]").forEach(function (b) {
    b.addEventListener("click", function () {
      var lb = document.createElement("div");
      lb.className = "lightbox"; lb.setAttribute("role", "dialog");
      lb.innerHTML = '<img alt="">';
      lb.firstChild.src = b.getAttribute("data-lightbox");
      lb.addEventListener("click", function () { lb.remove(); body.classList.remove("no-scroll"); });
      body.appendChild(lb); body.classList.add("no-scroll");
    });
  });
})();
