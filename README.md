# 💰 Cashback Calculator API

API para cálculo de cashback desenvolvida com **FastAPI** (Python) e **PostgreSQL**, com frontend estático em HTML/CSS/JS.

## 📐 Regras de Negócio

1. **Cashback base**: 5% do valor da compra
2. **Bônus VIP**: Clientes VIP recebem 10% adicional sobre o cashback base
3. **Promoção**: Compras acima de R$500 → cashback total é dobrado
4. **Ordem**: Primeiro calcula cashback base → aplica bônus VIP → aplica promoção

## 🏗️ Estrutura do Projeto

```
Cashback-API/
├── backend/
│   ├── main.py              # Inicialização do app FastAPI
│   ├── routes.py             # Endpoints da API
│   ├── schemas.py            # Modelos Pydantic (request/response)
│   ├── cashback.py           # Lógica de cálculo (Decimal)
│   ├── database.py           # PostgreSQL (psycopg3)
│   ├── requirements.txt      # Dependências Python
│   └── .env.example          # Template de variáveis de ambiente
├── frontend/
│   ├── index.html            # Interface do usuário
│   ├── style.css             # Design (dark mode + glassmorphism)
│   └── script.js             # Lógica do frontend
├── tests/
│   ├── conftest.py           # Configuração de path para testes
│   └── test_cashback.py      # Testes unitários (pytest)
└── README.md
```

## 🚀 Como Executar

### Pré-requisitos

- Python 3.10+
- PostgreSQL ([Supabase](https://supabase.com), [Neon](https://neon.tech) ou local)

### Backend

```bash
cd backend

# Criar e ativar ambiente virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com a URL do seu PostgreSQL

# Iniciar servidor
python -m uvicorn main:app --reload --port 8000
```

A API estará disponível em `http://localhost:8000`.
Documentação Swagger: `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
python -m http.server 3000
```

Acesse `http://localhost:3000`.

### Testes

```bash
pytest tests/ -v
```

## 📡 Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/calcular` | Calcula cashback e registra no banco |
| `GET` | `/historico/{ip}` | Retorna histórico de consultas por IP |
| `GET` | `/meu-ip` | Retorna o IP detectado do cliente |
| `GET` | `/docs` | Documentação Swagger (automática) |

### Exemplo — POST /calcular

**Request:**
```json
{
    "tipo_cliente": "VIP",
    "valor_compra": 510.00
}
```

**Response:**
```json
{
    "tipo_cliente": "VIP",
    "valor_compra": 510.0,
    "cashback_base": 25.5,
    "bonus_vip": 2.55,
    "subtotal": 28.05,
    "promocao_aplicada": true,
    "cashback_total": 56.1
}
```

## 🛠️ Tecnologias

- **Backend**: Python 3.10+, FastAPI, Uvicorn, psycopg (psycopg3)
- **Frontend**: HTML5, CSS3 (dark mode, glassmorphism), JavaScript (ES6+)
- **Banco**: PostgreSQL (Supabase)
- **Precisão**: `decimal.Decimal` com `ROUND_HALF_UP` para cálculos financeiros

## 🔒 Segurança

- **Variáveis de ambiente**: Credenciais são carregadas via `.env` (não versionado). Use o `.env.example` como template.
- **`.gitignore`**: Configurado para ignorar `.env`, caches, bytecodes e configs locais de IDE.
- **Sem secrets no código**: Nenhuma credencial hardcoded — tudo via `os.environ`.

## 📝 Decisões Técnicas

- **Decimal vs Float**: Uso de `Decimal` para evitar erros de arredondamento em cálculos financeiros (cf. Questão 4).
- **IP Detection**: Backend detecta IP via `X-Forwarded-For` (deploy) com fallback para `request.client.host` (local) e `ipify` (frontend).
- **CORS**: Habilitado para permitir chamadas cross-origin do frontend estático.
- **Validação**: Pydantic models com validators para `tipo_cliente` e `valor_compra`.

