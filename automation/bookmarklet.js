/**
 * Bookmarklet - Seleção automática de questões
 * estudante.estuda.com | ENEM | 2009-2026 | Matemática
 *
 * Como usar:
 *   1. Faça login em estudante.estuda.com
 *   2. Navegue até o banco de questões
 *   3. Abra o Console do browser (F12 > Console)
 *   4. Cole este código inteiro e pressione Enter
 *
 * OU como bookmarklet:
 *   Crie um novo favorito no browser e cole o conteúdo
 *   do arquivo bookmarklet_minified.js como URL
 */

(function () {
  "use strict";

  // ── Configuração ──────────────────────────────────────────────────────────
  const CONFIG = {
    banca: "ENEM",
    anoMin: 2009,
    anoMax: 2026,
    area: "Matemática",
    areaVariants: ["Matemática", "Matematica", "MATEMÁTICA", "matematica",
                   "Matemática e suas Tecnologias", "Mat"],
  };

  // ── Overlay de status ─────────────────────────────────────────────────────
  const overlay = document.createElement("div");
  overlay.id = "__estuda_automacao__";
  Object.assign(overlay.style, {
    position: "fixed", top: "20px", right: "20px", zIndex: "999999",
    background: "#1a1a2e", color: "#eee", padding: "16px 20px",
    borderRadius: "12px", fontFamily: "monospace", fontSize: "13px",
    maxWidth: "360px", boxShadow: "0 4px 24px rgba(0,0,0,.5)",
    lineHeight: "1.6", border: "1px solid #444",
  });
  overlay.innerHTML = `<b style="color:#7df9c8">🤖 Automação Estuda.com</b><br><div id="__estuda_log__"></div>`;
  document.body.appendChild(overlay);

  const log = (msg, color = "#ccc") => {
    const el = document.getElementById("__estuda_log__");
    if (el) el.innerHTML += `<div style="color:${color}">› ${msg}</div>`;
    console.log("[Estuda Bot]", msg);
  };

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  // ── Utilitários de DOM ────────────────────────────────────────────────────

  /** Encontra elemento por texto (case-insensitive, parcial) */
  function findByText(tag, text) {
    const lc = text.toLowerCase();
    return [...document.querySelectorAll(tag)].find(
      (el) => el.textContent.trim().toLowerCase().includes(lc)
    );
  }

  /** Dispara eventos React/Vue/Angular após mudança de valor */
  function triggerChange(el) {
    ["input", "change", "blur"].forEach((evt) =>
      el.dispatchEvent(new Event(evt, { bubbles: true }))
    );
    // React synthetic event
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
      window.HTMLInputElement.prototype, "value"
    );
    if (nativeInputValueSetter) nativeInputValueSetter.set.call(el, el.value);
  }

  /** Aguarda elemento aparecer no DOM */
  async function waitFor(selector, timeout = 5000) {
    const start = Date.now();
    while (Date.now() - start < timeout) {
      const el = document.querySelector(selector);
      if (el) return el;
      await sleep(200);
    }
    return null;
  }

  // ── Estratégias de seleção ────────────────────────────────────────────────

  async function aplicarFiltroSelect(labelTexts, valorTexts) {
    /** Tenta via elementos <select> */
    const selects = document.querySelectorAll("select");
    for (const sel of selects) {
      const opts = [...sel.options].map((o) => o.text.trim());
      for (const v of valorTexts) {
        const match = opts.find((o) => o.toLowerCase().includes(v.toLowerCase()));
        if (match) {
          sel.value = [...sel.options].find((o) =>
            o.text.trim().toLowerCase().includes(v.toLowerCase())
          )?.value;
          triggerChange(sel);
          return `<select> → ${match}`;
        }
      }
    }
    return null;
  }

  async function aplicarFiltroCheckbox(valorTexts) {
    /** Tenta via checkboxes ou radio buttons */
    for (const v of valorTexts) {
      const lbl = findByText("label", v);
      if (lbl) {
        lbl.click();
        const cb = lbl.querySelector("input") ||
          document.getElementById(lbl.htmlFor);
        if (cb && !cb.checked) cb.click();
        return `label → ${v}`;
      }
    }
    return null;
  }

  async function aplicarFiltroButton(valorTexts) {
    /** Tenta via botões, chips, pills, tags */
    for (const v of valorTexts) {
      for (const tag of ["button", "a", "span", "div", "li"]) {
        const el = findByText(tag, v);
        if (el && el.offsetParent !== null) {
          el.click();
          return `${tag} → ${v}`;
        }
      }
    }
    return null;
  }

  async function aplicarFiltroInput(placeholder, valor) {
    /** Tenta via inputs de texto (busca/autocomplete) */
    const inputs = document.querySelectorAll(
      `input[placeholder*="${placeholder}" i], input[aria-label*="${placeholder}" i]`
    );
    for (const inp of inputs) {
      inp.focus();
      inp.value = valor;
      triggerChange(inp);
      await sleep(600);
      // Seleciona primeira opção no dropdown de autocomplete
      const opt = await waitFor("[role='option'], .autocomplete-item, .dropdown-item", 1500);
      if (opt) {
        opt.click();
        return `input[${placeholder}] → ${valor}`;
      }
    }
    return null;
  }

  /** Estratégia combinada: tenta todas as abordagens */
  async function aplicarFiltro(nome, valorTexts, placeholderHint = "") {
    log(`Aplicando filtro: <b>${nome}</b>...`);

    let resultado =
      await aplicarFiltroSelect([nome], valorTexts) ||
      await aplicarFiltroCheckbox(valorTexts) ||
      await aplicarFiltroButton(valorTexts) ||
      (placeholderHint
        ? await aplicarFiltroInput(placeholderHint, valorTexts[0])
        : null);

    if (resultado) {
      log(`✓ ${nome}: ${resultado}`, "#7df9c8");
      await sleep(800);
      return true;
    }

    log(`⚠ ${nome}: não encontrado automaticamente`, "#ffbb33");
    return false;
  }

  // ── Seleção de anos ───────────────────────────────────────────────────────

  async function aplicarFiltroAnos(anoMin, anoMax) {
    log(`Aplicando filtro Anos: ${anoMin}–${anoMax}...`);

    // Estratégia 1: range slider (min/max)
    const sliders = document.querySelectorAll("input[type='range']");
    if (sliders.length >= 2) {
      sliders[0].value = anoMin;
      triggerChange(sliders[0]);
      sliders[1].value = anoMax;
      triggerChange(sliders[1]);
      log(`✓ Anos: sliders → ${anoMin}–${anoMax}`, "#7df9c8");
      return true;
    }

    // Estratégia 2: <select> com anos
    const selects = document.querySelectorAll("select");
    let selecionados = 0;
    for (const sel of selects) {
      const opts = [...sel.options].map((o) => parseInt(o.value || o.text));
      const temAnos = opts.some((a) => a >= 2009 && a <= 2026);
      if (temAnos) {
        // Seleciona todos os anos no range (múltipla seleção)
        for (const opt of sel.options) {
          const ano = parseInt(opt.value || opt.text);
          if (ano >= anoMin && ano <= anoMax) {
            opt.selected = true;
            selecionados++;
          }
        }
        triggerChange(sel);
        log(`✓ Anos: <select> → ${selecionados} anos`, "#7df9c8");
        return true;
      }
    }

    // Estratégia 3: checkboxes/botões por ano
    let clicados = 0;
    for (let ano = anoMin; ano <= anoMax; ano++) {
      const resultado = await aplicarFiltroButton([String(ano)]);
      if (resultado) clicados++;
    }
    if (clicados > 0) {
      log(`✓ Anos: ${clicados} botões clicados`, "#7df9c8");
      return true;
    }

    // Estratégia 4: input de texto "de/até"
    const inputAnos = document.querySelectorAll(
      "input[placeholder*='ano' i], input[name*='ano' i], input[id*='ano' i]"
    );
    if (inputAnos.length >= 2) {
      inputAnos[0].value = anoMin;
      triggerChange(inputAnos[0]);
      inputAnos[1].value = anoMax;
      triggerChange(inputAnos[1]);
      log(`✓ Anos: inputs → ${anoMin}–${anoMax}`, "#7df9c8");
      return true;
    }

    log(`⚠ Anos: não encontrado automaticamente`, "#ffbb33");
    return false;
  }

  // ── Confirmação/Submit ────────────────────────────────────────────────────

  async function confirmarSelecao() {
    log("Confirmando seleção...");
    const textos = ["Buscar", "Filtrar", "Aplicar", "Pesquisar",
                    "Ver questões", "Listar", "Gerar"];
    for (const txt of textos) {
      const btn =
        findByText("button", txt) ||
        findByText("a", txt) ||
        document.querySelector("button[type='submit']");
      if (btn && btn.offsetParent !== null) {
        btn.click();
        log(`✓ Confirmado: ${btn.textContent.trim()}`, "#7df9c8");
        await sleep(2000);
        return true;
      }
    }
    // Tenta submeter o formulário diretamente
    const form = document.querySelector("form");
    if (form) {
      form.submit();
      log("✓ Formulário submetido", "#7df9c8");
      return true;
    }
    log("⚠ Botão de confirmação não encontrado", "#ffbb33");
    return false;
  }

  // ── Fluxo principal ───────────────────────────────────────────────────────

  async function run() {
    log("Iniciando automação...", "#aef");
    await sleep(500);

    const bancaOk   = await aplicarFiltro("Banca", ["ENEM"], "banca");
    const areaOk    = await aplicarFiltro("Área", CONFIG.areaVariants, "área");
    const anosOk    = await aplicarFiltroAnos(CONFIG.anoMin, CONFIG.anoMax);
    const submitOk  = await confirmarSelecao();

    await sleep(1000);

    const total = document.querySelectorAll(
      ".questao, .question, [data-questao], .card-questao, .exercicio"
    ).length;

    log("─────────────────────────", "#555");
    if (bancaOk && areaOk && anosOk) {
      log(`✅ Filtros aplicados! Questões na página: ${total || "?"}`, "#7df9c8");
    } else {
      log("⚠ Alguns filtros precisam de ajuste manual.", "#ffbb33");
      log("Abra o DevTools (F12) e inspecione os filtros.", "#ffbb33");
    }
    log("URL: " + location.href);

    setTimeout(() => overlay.remove(), 15000);
  }

  run().catch((e) => {
    log("Erro: " + e.message, "#ff6b6b");
    console.error(e);
  });
})();
