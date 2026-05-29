# Duct Viewer

Web app para instaladores buscarem dutos por ID nos drawings.

## Estrutura

```
ductviewer/
├── main.py              # Backend (FastAPI)
├── requirements.txt     # Dependências Python
├── render.yaml          # Config de deploy (Render.com)
├── static/
│   └── index.html       # Viewer para instaladores
└── data/
    └── drawings.json    # Drawings processados (gerado automaticamente)
```

## Deploy no Render.com (gratuito)

### 1. Sobe para o GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/duct-viewer.git
git push -u origin main
```

### 2. Cria conta no Render.com

1. Acessa https://render.com
2. Cria conta com o GitHub
3. Clica em **New → Web Service**
4. Conecta o repositório `duct-viewer`
5. Render detecta o `render.yaml` automaticamente
6. Clica **Deploy**

### 3. Configura a senha do admin

No painel do Render → Environment → adiciona:
```
ADMIN_PASSWORD = sua_senha_aqui
```

### 4. Acessa o app

Render gera uma URL tipo: `https://duct-viewer.onrender.com`

- **Instaladores:** `https://duct-viewer.onrender.com`
- **Admin (você):** `https://duct-viewer.onrender.com/admin`

---

## Como usar

### Admin (você)
1. Acessa `/admin` com usuário e senha
2. Faz upload dos PDFs — o sistema extrai os IDs automaticamente
3. Cada PDF processado aparece na lista

### Instaladores
1. Abre o link no celular (Android ou iOS)
2. Digita o ID do duto (ex: `02-0044`)
3. O drawing abre com o duto destacado em amarelo

---

## Variáveis de ambiente

| Variável | Descrição | Default |
|----------|-----------|---------|
| `ADMIN_PASSWORD` | Senha do painel admin | `sublime2024` |

**Importante:** mude a senha antes de deployar!
