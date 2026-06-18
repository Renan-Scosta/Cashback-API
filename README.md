# Calculadora de Cashback

API para cálculo de cashback com **FastAPI**, **PostgreSQL** e frontend estático.

🔗 **Demo:** [cashback-api-vodb.onrender.com](https://cashback-api-vodb.onrender.com)

## Regras de Negócio

1. Cashback base: **5%** do valor da compra
2. Bônus VIP: **+10%** sobre o cashback base
3. Promoção: compras acima de **R$ 500** → cashback é dobrado
4. Ordem: cashback base → bônus VIP → promoção

## Como Executar

**Pré-requisitos:** Python 3.10+ e PostgreSQL

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
cp .env.example .env         # Editar com sua DATABASE_URL
uvicorn main:app --reload --port 8000
```

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

### Frontend

```bash
cd frontend
python -m http.server 3000
```

- Acesse: http://localhost:3000

### Testes

```bash
pytest tests/ -v
```

## Endpoints

| Método | Rota              | Descrição                        |
| ------ | ----------------- | -------------------------------- |
| POST   | `/calcular`       | Calcula cashback e registra      |
| GET    | `/historico/{ip}` | Histórico de consultas por IP    |
| GET    | `/meu-ip`        | IP detectado do cliente          |

## Tecnologias

- **Backend:** FastAPI, psycopg3, Pydantic, Decimal
- **Frontend:** HTML, CSS, JavaScript
- **Banco:** PostgreSQL (Supabase)
- **Deploy:** Render
