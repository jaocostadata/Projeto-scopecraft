# Como usar a automação (sem instalar nada)

## Método 1 — Console do Browser (mais simples)

1. Faça login em https://estudante.estuda.com
2. Navegue até **Banco de Questões**
3. Pressione **F12** → aba **Console**
4. Cole o conteúdo do arquivo `bookmarklet.js` e pressione **Enter**

O script vai aplicar automaticamente:
- ✅ Banca: **ENEM**
- ✅ Anos: **2009–2026**
- ✅ Área: **Matemática**

---

## Método 2 — Favorito do Browser (bookmarklet)

1. Crie um novo favorito no browser
2. Cole o conteúdo do arquivo `bookmarklet_url.txt` como **URL** do favorito
3. Salve como "Filtrar Questões ENEM"
4. Faça login em https://estudante.estuda.com
5. Navegue até o Banco de Questões
6. Clique no favorito criado

---

## Método 3 — Script Python local (Playwright)

```bash
pip install playwright && playwright install chromium
python selecionar_questoes.py
```
As credenciais já estão no arquivo `.env`.

---

## O que acontece quando o script roda

Um painel aparece no canto superior direito da tela mostrando o progresso em tempo real. Os filtros são aplicados automaticamente. Se algum filtro não for encontrado, o painel indica qual ajuste manual é necessário.
