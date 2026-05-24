"""
Automação de seleção de questões - estudante.estuda.com
Critérios: Banca ENEM | Anos 2009-2026 | Área Matemática
"""

import asyncio
import os
import json
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# ── Configuração ──────────────────────────────────────────────────────────────
BASE_URL = "https://estudante.estuda.com"
EMAIL    = os.getenv("ESTUDA_EMAIL", "")
SENHA    = os.getenv("ESTUDA_SENHA", "")

FILTROS = {
    "banca": "ENEM",
    "anos":  list(range(2009, 2027)),   # 2009 até 2026 inclusive
    "area":  "Matemática",
}

SCREENSHOTS_DIR = Path("screenshots")
RESULTADOS_FILE = Path("questoes_selecionadas.json")
# ─────────────────────────────────────────────────────────────────────────────


async def fazer_login(page):
    print("🔐 Fazendo login...")
    await page.goto(f"{BASE_URL}/login", wait_until="networkidle")
    await page.screenshot(path=SCREENSHOTS_DIR / "01_login_page.png")

    # Detecta campos de login (tenta seletores comuns)
    for email_sel in ["input[type='email']", "input[name='email']", "#email", "input[placeholder*='mail']"]:
        if await page.locator(email_sel).count() > 0:
            await page.fill(email_sel, EMAIL)
            break

    for senha_sel in ["input[type='password']", "input[name='password']", "#password", "input[name='senha']"]:
        if await page.locator(senha_sel).count() > 0:
            await page.fill(senha_sel, SENHA)
            break

    # Submete o formulário
    for submit_sel in ["button[type='submit']", "input[type='submit']", "button:has-text('Entrar')",
                       "button:has-text('Login')", "button:has-text('Acessar')"]:
        if await page.locator(submit_sel).count() > 0:
            await page.click(submit_sel)
            break

    await page.wait_for_load_state("networkidle")
    await page.screenshot(path=SCREENSHOTS_DIR / "02_pos_login.png")
    print(f"   URL atual: {page.url}")


async def navegar_banco_questoes(page):
    print("📚 Navegando para o banco de questões...")

    # Tenta rotas conhecidas da plataforma
    rotas_candidatas = [
        "/questoes",
        "/banco-de-questoes",
        "/questoes_categorias",
        "/simulado",
        "/exercicios",
    ]

    for rota in rotas_candidatas:
        try:
            resp = await page.goto(f"{BASE_URL}{rota}", wait_until="networkidle", timeout=10_000)
            if resp and resp.status < 400:
                print(f"   Rota encontrada: {rota}")
                await page.screenshot(path=SCREENSHOTS_DIR / "03_banco_questoes.png")
                return True
        except PlaywrightTimeout:
            continue

    # Se não encontrou rota direta, tenta via menu de navegação
    print("   Buscando link de questões no menu...")
    for link_text in ["Questões", "Banco de Questões", "Exercícios", "Simulado"]:
        loc = page.get_by_role("link", name=link_text, exact=False)
        if await loc.count() > 0:
            await loc.first.click()
            await page.wait_for_load_state("networkidle")
            await page.screenshot(path=SCREENSHOTS_DIR / "03_banco_questoes.png")
            print(f"   Clicado em: {link_text}")
            return True

    print("   ⚠️  Não encontrou rota automática. Capturando estado atual...")
    await page.screenshot(path=SCREENSHOTS_DIR / "03_pagina_atual.png")
    return False


async def aplicar_filtro_banca(page, banca: str):
    print(f"🏷️  Aplicando filtro Banca: {banca}")

    seletores = [
        f"[data-banca='{banca}']",
        f"option[value*='ENEM']",
        f"label:has-text('{banca}')",
        f"button:has-text('{banca}')",
        f"li:has-text('{banca}')",
        f"input[value*='ENEM']",
    ]

    # Tenta selecionar via <select>
    selects = await page.locator("select").all()
    for sel in selects:
        options = await sel.locator("option").all_text_contents()
        if any("ENEM" in opt for opt in options):
            await sel.select_option(label="ENEM")
            print("   Selecionado via <select>")
            return True

    # Tenta seletores diretos
    for sel in seletores:
        loc = page.locator(sel)
        if await loc.count() > 0:
            await loc.first.click()
            print(f"   Clicado: {sel}")
            return True

    print("   ⚠️  Filtro de banca não encontrado automaticamente")
    return False


async def aplicar_filtro_anos(page, anos: list):
    print(f"📅 Aplicando filtro Anos: {anos[0]}-{anos[-1]}")

    # Tenta selecionar anos via <select multiple>
    selects = await page.locator("select").all()
    for sel in selects:
        options = await sel.locator("option").all_text_contents()
        if any(str(ano) in opt for ano in anos for opt in options):
            valores = [str(ano) for ano in anos]
            try:
                await sel.select_option(value=valores)
                print(f"   Selecionados {len(valores)} anos via <select>")
                return True
            except Exception:
                pass

    # Tenta clicar em checkboxes/botões de ano
    selecionados = 0
    for ano in anos:
        for sel in [f"label:has-text('{ano}')", f"input[value='{ano}']",
                    f"button:has-text('{ano}')", f"[data-ano='{ano}']"]:
            loc = page.locator(sel)
            if await loc.count() > 0:
                await loc.first.click()
                selecionados += 1
                break

    if selecionados > 0:
        print(f"   Selecionados {selecionados} anos via clique")
        return True

    print("   ⚠️  Filtro de anos não encontrado automaticamente")
    return False


async def aplicar_filtro_area(page, area: str):
    print(f"📐 Aplicando filtro Área: {area}")

    seletores = [
        f"label:has-text('{area}')",
        f"button:has-text('{area}')",
        f"option:has-text('{area}')",
        f"[data-area*='Matem']",
        f"li:has-text('{area}')",
        "label:has-text('Matemática')",
        "button:has-text('Matemática')",
    ]

    # Tenta via <select>
    selects = await page.locator("select").all()
    for sel in selects:
        options = await sel.locator("option").all_text_contents()
        if any("Matem" in opt for opt in options):
            matching = [opt for opt in options if "Matem" in opt]
            await sel.select_option(label=matching[0])
            print(f"   Selecionado via <select>: {matching[0]}")
            return True

    # Tenta seletores diretos
    for sel in seletores:
        loc = page.locator(sel)
        if await loc.count() > 0:
            await loc.first.click()
            print(f"   Clicado: {sel}")
            return True

    print("   ⚠️  Filtro de área não encontrado automaticamente")
    return False


async def confirmar_selecao(page):
    print("✅ Confirmando seleção...")

    botoes_confirmar = [
        "button:has-text('Buscar')",
        "button:has-text('Filtrar')",
        "button:has-text('Aplicar')",
        "button:has-text('Pesquisar')",
        "button[type='submit']",
        "input[type='submit']",
    ]

    for sel in botoes_confirmar:
        loc = page.locator(sel)
        if await loc.count() > 0:
            await loc.first.click()
            await page.wait_for_load_state("networkidle")
            print(f"   Clicado: {sel}")
            await page.screenshot(path=SCREENSHOTS_DIR / "04_resultado.png")
            return True

    await page.screenshot(path=SCREENSHOTS_DIR / "04_resultado.png")
    return False


async def capturar_questoes(page) -> list:
    print("📋 Capturando questões encontradas...")

    # Espera elementos de questão carregarem
    await page.wait_for_timeout(2000)

    # Tenta extrair dados das questões via JavaScript
    questoes = await page.evaluate("""() => {
        const itens = [];

        // Seletores comuns para cards de questão
        const sels = [
            '.questao', '.question', '.card-questao',
            '[data-questao]', '[data-question-id]',
            '.exercicio', '.item-questao',
        ];

        for (const sel of sels) {
            const els = document.querySelectorAll(sel);
            if (els.length > 0) {
                els.forEach((el, i) => {
                    itens.push({
                        index: i + 1,
                        id: el.dataset.questaoId || el.dataset.questionId || el.id || null,
                        texto: el.querySelector('p, .enunciado, .question-text')?.innerText?.slice(0, 200) || null,
                        seletor: sel,
                    });
                });
                break;
            }
        }

        return itens;
    }""")

    total = await page.locator(".questao, .question, .card-questao, [data-questao]").count()
    print(f"   Questões encontradas na página: {max(len(questoes), total)}")
    return questoes


async def salvar_resultados(questoes: list, url_final: str):
    resultado = {
        "filtros_aplicados": {
            "banca": FILTROS["banca"],
            "anos": f"{FILTROS['anos'][0]}-{FILTROS['anos'][-1]}",
            "area": FILTROS["area"],
        },
        "url_resultado": url_final,
        "total_questoes": len(questoes),
        "questoes": questoes,
    }

    with open(RESULTADOS_FILE, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"💾 Resultados salvos em: {RESULTADOS_FILE}")


async def main():
    if not EMAIL or not SENHA:
        print("❌ Configure as variáveis de ambiente:")
        print("   export ESTUDA_EMAIL='seu@email.com'")
        print("   export ESTUDA_SENHA='sua_senha'")
        return

    SCREENSHOTS_DIR.mkdir(exist_ok=True)

    print("=" * 60)
    print("  Automação estudante.estuda.com")
    print(f"  Banca: {FILTROS['banca']}")
    print(f"  Anos:  {FILTROS['anos'][0]}-{FILTROS['anos'][-1]}")
    print(f"  Área:  {FILTROS['area']}")
    print("=" * 60)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)  # headless=True para rodar sem janela
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        # Intercepta chamadas de API para debug
        api_calls = []
        async def capturar_api(route):
            if "questao" in route.request.url or "filtro" in route.request.url:
                api_calls.append({"url": route.request.url, "method": route.request.method})
            await route.continue_()

        await page.route("**/*", capturar_api)

        try:
            await fazer_login(page)

            if "login" in page.url.lower() or "entrar" in page.url.lower():
                print("❌ Login falhou. Verifique as credenciais.")
                await browser.close()
                return

            encontrou = await navegar_banco_questoes(page)

            if encontrou:
                await aplicar_filtro_banca(page, FILTROS["banca"])
                await page.screenshot(path=SCREENSHOTS_DIR / "03b_banca.png")

                await aplicar_filtro_area(page, FILTROS["area"])
                await page.screenshot(path=SCREENSHOTS_DIR / "03c_area.png")

                await aplicar_filtro_anos(page, FILTROS["anos"])
                await page.screenshot(path=SCREENSHOTS_DIR / "03d_anos.png")

                await confirmar_selecao(page)

                questoes = await capturar_questoes(page)
                await salvar_resultados(questoes, page.url)

                if api_calls:
                    print("\n📡 Chamadas de API detectadas:")
                    for call in api_calls[:10]:
                        print(f"   {call['method']} {call['url']}")
            else:
                print("\n⚠️  Não foi possível navegar automaticamente.")
                print("   Screenshots salvas em ./screenshots/")
                print("   Verifique a URL do banco de questões manualmente.")

        except Exception as e:
            print(f"❌ Erro: {e}")
            await page.screenshot(path=SCREENSHOTS_DIR / "erro.png")
            raise
        finally:
            input("\n⏸️  Pressione ENTER para fechar o browser...")
            await browser.close()

    print("\n✅ Concluído!")


if __name__ == "__main__":
    asyncio.run(main())
