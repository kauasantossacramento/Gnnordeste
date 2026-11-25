/* Empreender Soluções — interações (sem dependências) */
(function () {
  "use strict";
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var body = document.body;
  var calmo = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var guarda = {
    ler: function (k, sessao) { try { return (sessao ? sessionStorage : localStorage).getItem(k); } catch (e) { return null; } },
    gravar: function (k, v, sessao) { try { (sessao ? sessionStorage : localStorage).setItem(k, v); } catch (e) {} }
  };

  /* ---------------------------------------------- cabeçalho e menu */
  var topo = $(".topo");
  var aoRolar = function () { if (topo) topo.classList.toggle("rolou", window.scrollY > 20); };
  window.addEventListener("scroll", aoRolar, { passive: true }); aoRolar();

  var burger = $(".topo__burger"), gaveta = $("#gaveta");
  if (burger && gaveta) {
    var abrirMenu = function (abrir) {
      if (abrir) gaveta.hidden = false;
      requestAnimationFrame(function () {
        body.classList.toggle("menu-aberto", abrir);
        body.classList.toggle("trava", abrir);
      });
      burger.setAttribute("aria-expanded", abrir);
      burger.setAttribute("aria-label", abrir ? "Fechar menu" : "Abrir menu");
      if (!abrir) setTimeout(function () { if (!body.classList.contains("menu-aberto")) gaveta.hidden = true; }, 700);
    };
    burger.addEventListener("click", function () { abrirMenu(!body.classList.contains("menu-aberto")); });
    $$("a", gaveta).forEach(function (a) { a.addEventListener("click", function () { abrirMenu(false); }); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && body.classList.contains("menu-aberto")) abrirMenu(false); });
  }

  /* ---------------------------------------------- revelar ao rolar + contadores */
  var revelar = $$("[data-revela]");
  if ("IntersectionObserver" in window && !calmo) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("visto"); io.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    revelar.forEach(function (el) { io.observe(el); });
  } else revelar.forEach(function (el) { el.classList.add("visto"); });

  var contar = function (el) {
    var fim = parseInt(el.getAttribute("data-conta"), 10) || 0;
    if (calmo) { el.textContent = fim; return; }
    var t0 = null;
    var passo = function (t) {
      if (!t0) t0 = t;
      var p = Math.min((t - t0) / 1600, 1);
      el.textContent = Math.round(fim * (1 - Math.pow(1 - p, 3)));
      if (p < 1) requestAnimationFrame(passo);
    };
    requestAnimationFrame(passo);
  };
  if ("IntersectionObserver" in window) {
    var co = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { contar(e.target); co.unobserve(e.target); } });
    }, { threshold: 0.6 });
    $$("[data-conta]").forEach(function (el) { co.observe(el); });
  }

  /* ---------------------------------------------- letreiro de serviços no palco do hero */
  $$(".ticker ul").forEach(function (ul) {
    var itens = ul.children.length;
    if (itens < 2 || calmo) return;
    var i = 0;
    setInterval(function () {
      i++;
      ul.classList.remove("sem-anim");
      ul.style.transform = "translateY(" + (-1.4 * i) + "em)";
      if (i === itens - 1) setTimeout(function () { ul.classList.add("sem-anim"); ul.style.transform = "translateY(0)"; i = 0; }, 750);
    }, 2400);
  });

  /* ---------------------------------------------- range com preenchimento + saída */
  var pintaRange = function (r) {
    var p = ((r.value - r.min) / (r.max - r.min)) * 100;
    r.style.setProperty("--p", p + "%");
  };
  $$("[data-mini-sim]").forEach(function (f) {
    var r = $("[data-faixa-range]", f), out = $("[data-saida]", f);
    if (!r) return;
    var upd = function () { pintaRange(r); if (out) out.textContent = r.value; };
    r.addEventListener("input", upd); upd();
  });

  /* ---------------------------------------------- explorador de serviços (abas acessíveis) */
  $$("[data-explorador]").forEach(function (ex) {
    var abas = $$("[role=tab]", ex);
    var ativar = function (aba, foco) {
      abas.forEach(function (a) {
        var on = a === aba;
        a.setAttribute("aria-selected", on); a.tabIndex = on ? 0 : -1;
        document.getElementById(a.getAttribute("aria-controls")).hidden = !on;
      });
      if (foco) aba.focus();
    };
    abas.forEach(function (a, i) {
      a.addEventListener("click", function () { ativar(a); });
      a.addEventListener("keydown", function (e) {
        var n = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[e.key];
        if (n) { e.preventDefault(); ativar(abas[(i + n + abas.length) % abas.length], true); }
      });
    });
  });

  /* ---------------------------------------------- linha do processo acompanha a rolagem */
  $$("[data-processo]").forEach(function (lista) {
    var trilho = $(".processo__trilho", lista), etapas = $$(".etapa", lista);
    var atualiza = function () {
      var r = lista.getBoundingClientRect(), vh = window.innerHeight;
      var p = Math.max(0, Math.min(1, (vh * 0.75 - r.top) / (r.height + vh * 0.2)));
      trilho.style.setProperty("--progresso", (p * 100) + "%");
      etapas.forEach(function (e, i) { e.classList.toggle("ativa", p >= (i + 0.3) / etapas.length); });
    };
    window.addEventListener("scroll", atualiza, { passive: true }); atualiza();
  });

  /* ---------------------------------------------- filtros de vagas */
  var filtros = $("[data-filtros]");
  if (filtros) {
    var busca = $("[data-filtro-busca]"), cidade = $("[data-filtro-cidade]"), area = $("[data-filtro-area]");
    var total = $("[data-filtro-total]"), vazio = $("[data-filtro-vazio]");
    var norm = function (t) { return (t || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); };
    var filtrar = function () {
      var q = norm(busca && busca.value), c = cidade ? cidade.value : "", a = area ? area.value : "", n = 0;
      $$("[data-lista-vagas] .vaga-linha").forEach(function (v) {
        var ok = (!q || norm(v.getAttribute("data-busca")).indexOf(q) > -1) &&
                 (!c || v.getAttribute("data-cidade") === c) && (!a || v.getAttribute("data-area") === a);
        v.classList.toggle("filtrada", !ok); if (ok) n++;
      });
      if (total) total.textContent = n;
      if (vazio) vazio.hidden = n > 0;
    };
    [busca, cidade, area].forEach(function (el) { if (el) el.addEventListener("input", filtrar); });
  }

  /* ---------------------------------------------- upload de currículo */
  $$("[data-upload]").forEach(function (u) {
    var inp = $("input", u), txt = $("[data-upload-txt]", u), orig = txt.innerHTML;
    inp.addEventListener("change", function () {
      var f = inp.files && inp.files[0];
      u.classList.toggle("ok", !!f);
      txt.textContent = "";
      if (f) { var b = document.createElement("b"); b.textContent = f.name; txt.appendChild(b); txt.appendChild(document.createTextNode(" · " + Math.max(1, Math.round(f.size / 1024)) + " KB")); }
      else txt.innerHTML = orig;
    });
    ["dragenter", "dragover"].forEach(function (ev) { u.addEventListener(ev, function () { u.classList.add("sobre"); }); });
    ["dragleave", "drop"].forEach(function (ev) { u.addEventListener(ev, function () { u.classList.remove("sobre"); }); });
  });

  /* ---------------------------------------------- máscara de telefone */
  $$("[data-mask=tel]").forEach(function (i) {
    i.addEventListener("input", function () {
      var d = i.value.replace(/\D/g, "").slice(0, 11);
      if (d.length > 10) i.value = "(" + d.slice(0, 2) + ") " + d.slice(2, 7) + "-" + d.slice(7);
      else if (d.length > 6) i.value = "(" + d.slice(0, 2) + ") " + d.slice(2, 6) + "-" + d.slice(6);
      else if (d.length > 2) i.value = "(" + d.slice(0, 2) + ") " + d.slice(2);
      else if (d.length) i.value = "(" + d;
    });
  });

  /* ---------------------------------------------- copiar protocolo */
  $$("[data-copiar]").forEach(function (el) {
    el.title = "Clique para copiar";
    el.addEventListener("click", function () {
      if (navigator.clipboard) navigator.clipboard.writeText(el.textContent.trim()).then(function () {
        el.classList.add("copiado"); setTimeout(function () { el.classList.remove("copiado"); }, 2000);
      });
    });
  });

  /* ---------------------------------------------- evitar duplo envio */
  $$("form[data-form], form[data-sim]").forEach(function (f) {
    f.addEventListener("submit", function () {
      $$("button[type=submit]", f).forEach(function (b) { b.disabled = true; b.style.opacity = ".7"; });
    });
  });

  /* ---------------------------------------------- toasts */
  $$(".toast").forEach(function (t, i) {
    setTimeout(function () { t.classList.add("sai"); setTimeout(function () { t.remove(); }, 450); }, 6000 + i * 400);
  });

  /* ---------------------------------------------- faixa de aviso */
  $$("[data-faixa]").forEach(function (f) {
    var k = "faixa:" + f.getAttribute("data-faixa");
    if (guarda.ler(k, true)) { f.classList.add("fechada"); return; }
    $(".faixa__x", f).addEventListener("click", function () { f.classList.add("fechada"); guarda.gravar(k, "1", true); });
  });

  /* ---------------------------------------------- avisos modal e flutuante */
  var podeMostrar = function (el) {
    var k = "aviso:" + el.getAttribute("data-aviso"), f = el.getAttribute("data-freq");
    if (f === "sessao") return !guarda.ler(k, true);
    if (f === "uma-vez") return !guarda.ler(k, false);
    return true;
  };
  var marcar = function (el) {
    var k = "aviso:" + el.getAttribute("data-aviso"), f = el.getAttribute("data-freq");
    if (f === "sessao") guarda.gravar(k, "1", true);
    if (f === "uma-vez") guarda.gravar(k, "1", false);
  };
  var fila = $$(".modal[data-aviso]").filter(podeMostrar), focoAnterior = null;
  var proximoModal = function () {
    var m = fila.shift(); if (!m) return;
    focoAnterior = document.activeElement;
    m.hidden = false; body.classList.add("trava"); marcar(m);
    var x = $(".modal__x", m); if (x) x.focus();
  };
  $$(".modal[data-aviso]").forEach(function (m) {
    var fechar = function () {
      m.classList.add("fechando");
      setTimeout(function () {
        m.hidden = true; m.classList.remove("fechando"); body.classList.remove("trava");
        if (focoAnterior) focoAnterior.focus();
        proximoModal();
      }, 280);
    };
    $$("[data-fechar]", m).forEach(function (b) { b.addEventListener("click", fechar); });
    m.addEventListener("keydown", function (e) {
      if (e.key === "Escape") fechar();
      if (e.key === "Tab") { /* mantém o foco dentro do modal */
        var f = $$("a[href], button:not([disabled])", m).filter(function (x) { return x.offsetParent; });
        if (!f.length) return;
        if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
        else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
      }
    });
  });
  if (fila.length) setTimeout(proximoModal, 1400);

  $$(".flutuante[data-aviso]").forEach(function (fl) {
    if (!podeMostrar(fl)) return;
    setTimeout(function () { fl.hidden = false; marcar(fl); }, fila.length ? 6000 : 2500);
    $$("[data-fechar]", fl).forEach(function (b) {
      b.addEventListener("click", function () { fl.classList.add("sai"); setTimeout(function () { fl.hidden = true; }, 350); });
    });
  });

  /* ---------------------------------------------- cookies (LGPD) */
  var cookies = $("[data-cookies]");
  var carregaGA = function () {
    if (!window.GA_ID || window.gtag) return;
    var s = document.createElement("script"); s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(window.GA_ID);
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("js", new Date()); window.gtag("config", window.GA_ID, { anonymize_ip: true });
  };
  if (cookies) {
    var resp = guarda.ler("cookies");
    if (resp === "todos") carregaGA();
    if (!resp) setTimeout(function () { cookies.hidden = false; }, 1800);
    $$("[data-cookies-resp]", cookies).forEach(function (b) {
      b.addEventListener("click", function () {
        var v = b.getAttribute("data-cookies-resp");
        guarda.gravar("cookies", v); cookies.hidden = true;
        if (v === "todos") carregaGA();
      });
    });
    $$("[data-cookies-abrir]").forEach(function (b) { b.addEventListener("click", function () { cookies.hidden = false; }); });
  }

  /* ---------------------------------------------- simulador "Monte sua equipe" */
  var sim = $("[data-sim]");
  if (sim) {
    var etapas = $$("[data-etapa]", sim), passos = $$(".sim__passos li", sim), atual = 1;
    var bVoltar = $("[data-voltar]", sim), bAvancar = $("[data-avancar]", sim), bEnviar = $("[data-enviar]", sim);
    var barra = $("[data-sim-progresso]", sim);
    var qtd = $("[data-qtd]", sim), qtdR = $("[data-qtd-range]", sim), rQtd = $("[data-r-qtd]", sim);
    var perfisBox = $("[data-perfis-box]", sim), perfisLista = $("[data-perfis-lista]", sim), perfisHidden = $("input[name=perfis]", sim);
    var escolhidos = (perfisHidden.value || "").split(",").map(function (s) { return s.trim(); }).filter(Boolean);

    var texto = function (sel) {
      var el = $(sel + ":checked", sim);
      return el ? el.parentNode.textContent.trim() : "—";
    };
    var resumo = function () {
      var servs = $$("input[name=servicos]:checked", sim).map(function (c) { return c.getAttribute("data-nome"); });
      $("[data-r-servicos]", sim).textContent = servs.length ? servs.join(", ") : "—";
      $("[data-r-contrato]", sim).textContent = texto("input[name=contrato]");
      $("[data-r-inicio]", sim).textContent = texto("input[name=inicio]");
      var c = $("[name=cidade]", sim).value.trim(), u = $("[name=uf]", sim).value;
      $("[data-r-local]", sim).textContent = c ? c + (u ? "/" + u : "") : "—";
      if (rQtd.textContent !== String(qtd.value)) {
        rQtd.textContent = qtd.value || "—";
        rQtd.classList.remove("bate"); void rQtd.offsetWidth; rQtd.classList.add("bate");
      }
    };
    var montaPerfis = function () {
      var todos = [];
      $$("input[name=servicos]:checked", sim).forEach(function (c) {
        (c.getAttribute("data-perfis") || "").split("|").forEach(function (p) { if (p && todos.indexOf(p) < 0) todos.push(p); });
      });
      perfisLista.innerHTML = "";
      todos.forEach(function (p) {
        var l = document.createElement("label"), i = document.createElement("input"), s = document.createElement("span");
        i.type = "checkbox"; i.value = p; i.checked = escolhidos.indexOf(p) > -1; s.textContent = p;
        i.addEventListener("change", function () {
          escolhidos = $$("input", perfisLista).filter(function (x) { return x.checked; }).map(function (x) { return x.value; });
          perfisHidden.value = escolhidos.join(", ");
        });
        l.appendChild(i); l.appendChild(s); perfisLista.appendChild(l);
      });
      perfisBox.hidden = !todos.length;
    };
    var valida = function (n) {
      var et = $("[data-etapa='" + n + "']", sim), ok = true;
      $$(".campo__erro.js", et).forEach(function (e) { e.remove(); });
      $$(".campo--erro", et).forEach(function (e) { e.classList.remove("campo--erro"); });
      var erro = function (alvo, msg) {
        ok = false; alvo.classList.add("campo--erro");
        var s = document.createElement("small"); s.className = "campo__erro js"; s.textContent = msg; alvo.appendChild(s);
      };
      if (n === 1 && !$$("input[name=servicos]:checked", sim).length) erro($(".sim__servicos", sim).parentNode, "Escolha pelo menos um serviço.");
      if (n === 2 && !(parseInt(qtd.value, 10) > 0)) erro(qtd.closest(".campo"), "Informe a quantidade.");
      if (n === 3) {
        if (!$("[name=cidade]", sim).value.trim()) erro($("[name=cidade]", sim).closest(".campo"), "Informe a cidade.");
        if (!$("[name=uf]", sim).value) erro($("[name=uf]", sim).closest(".campo"), "Escolha a UF.");
      }
      if (n === 4) {
        ["empresa", "nome", "email", "telefone"].forEach(function (nm) {
          var i = $("[name=" + nm + "]", sim);
          if (!i.value.trim() || (nm === "email" && !/^\S+@\S+\.\S+$/.test(i.value))) erro(i.closest(".campo"), nm === "email" ? "Informe um e-mail válido." : "Campo obrigatório.");
        });
        var ac = $("[name=aceite]", sim);
        if (!ac.checked) erro(ac.closest(".campo"), "É preciso concordar para enviar.");
      }
      if (!ok) { var p = $(".campo--erro input, .campo--erro select", et) || $(".campo--erro", et); if (p && p.focus) p.focus(); }
      return ok;
    };
    var ir = function (n) {
      atual = n;
      etapas.forEach(function (e) { e.hidden = +e.getAttribute("data-etapa") !== n; });
      passos.forEach(function (p, i) { p.classList.toggle("on", i + 1 === n); p.classList.toggle("feito", i + 1 < n); });
      barra.style.width = (n / etapas.length * 100) + "%";
      bVoltar.hidden = n === 1; bAvancar.hidden = n === etapas.length; bEnviar.hidden = n !== etapas.length;
      var topoSim = sim.getBoundingClientRect().top + window.scrollY - 110;
      if (window.scrollY > topoSim) window.scrollTo({ top: topoSim, behavior: calmo ? "auto" : "smooth" });
    };
    bAvancar.addEventListener("click", function () { if (valida(atual)) ir(atual + 1); });
    bVoltar.addEventListener("click", function () { ir(atual - 1); });
    passos.forEach(function (p, i) {
      p.addEventListener("click", function () {
        var alvo = i + 1;
        if (alvo < atual) return ir(alvo);
        for (var k = atual; k < alvo; k++) if (!valida(k)) return ir(k);
        ir(alvo);
      });
    });
    sim.addEventListener("submit", function (e) {
      for (var k = 1; k <= etapas.length; k++) if (!valida(k)) { e.preventDefault(); ir(k); valida(k); return; }
    });
    var sincroniza = function (de, para) { para.value = de.value; pintaRange(qtdR); resumo(); };
    qtd.addEventListener("input", function () { qtdR.value = Math.min(qtd.value, 300); sincroniza(qtd, qtd); });
    qtdR.addEventListener("input", function () { sincroniza(qtdR, qtd); });
    $$("[data-passo]", sim).forEach(function (b) {
      b.addEventListener("click", function () {
        qtd.value = Math.max(1, Math.min(5000, (parseInt(qtd.value, 10) || 0) + +b.getAttribute("data-passo")));
        qtdR.value = Math.min(qtd.value, 300); pintaRange(qtdR); resumo();
      });
    });
    sim.addEventListener("change", function (e) { if (e.target.name === "servicos") montaPerfis(); resumo(); });
    sim.addEventListener("input", resumo);
    pintaRange(qtdR); montaPerfis(); resumo();
    /* se o servidor devolveu erro, abre a primeira etapa com problema */
    var comErro = $(".campo--erro, .sim__servicos.campo--erro", sim);
    ir(comErro ? +comErro.closest("[data-etapa]").getAttribute("data-etapa") : 1);
  }
})();
