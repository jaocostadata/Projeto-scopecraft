# Automação de Seleção de Questões - estudante.estuda.com

Seleciona automaticamente questões com os critérios:
- **Banca:** ENEM
- **Anos:** 2009–2026
- **Área:** Matemática

## Instalação

```bash
cd automation
pip install -r requirements.txt
playwright install chromium
```

## Configuração de credenciais

```bash
# Linux / Mac
export ESTUDA_EMAIL="seu@email.com"
export ESTUDA_SENHA="sua_senha"

# Windows (PowerShell)
$env:ESTUDA_EMAIL="seu@email.com"
$env:ESTUDA_SENHA="sua_senha"
```

Ou crie um arquivo `.env` (copie `.env.example`) e carregue com:
```bash
export $(cat .env | xargs)
```

## Execução

```bash
python selecionar_questoes.py
```

O script abre o browser (visível), faz login, navega até o banco de questões,
aplica os filtros e salva os resultados em `questoes_selecionadas.json`.

### Modo headless (sem janela)

Edite `selecionar_questoes.py` e troque:
```python
browser = await pw.chromium.launch(headless=False)
# para:
browser = await pw.chromium.launch(headless=True)
```

## Saídas geradas

| Arquivo | Descrição |
|---|---|
| `screenshots/01_login_page.png` | Página de login |
| `screenshots/02_pos_login.png` | Após o login |
| `screenshots/03_banco_questoes.png` | Banco de questões |
| `screenshots/03b_banca.png` | Após filtro banca |
| `screenshots/03c_area.png` | Após filtro área |
| `screenshots/03d_anos.png` | Após filtro anos |
| `screenshots/04_resultado.png` | Resultado final |
| `questoes_selecionadas.json` | Dados das questões extraídas |

## Ajuste manual se necessário

Se o script não encontrar os filtros automaticamente, os screenshots
mostrarão o estado da página. Inspecione com F12 no browser e atualize
os seletores CSS nas funções `aplicar_filtro_*` do script.
