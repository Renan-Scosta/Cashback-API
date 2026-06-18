import os

import psycopg
from psycopg.rows import dict_row


def get_connection():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "Variável de ambiente DATABASE_URL não configurada. "
            "Exemplo: postgresql://user:pass@host:5432/dbname"
        )
    return psycopg.connect(database_url, row_factory=dict_row)


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS consultas (
                id SERIAL PRIMARY KEY,
                ip_usuario VARCHAR(45) NOT NULL,
                tipo_cliente VARCHAR(10) NOT NULL CHECK (tipo_cliente IN ('VIP', 'Normal')),
                valor_compra NUMERIC(12, 2) NOT NULL,
                valor_cashback NUMERIC(12, 2) NOT NULL,
                data_hora TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_consultas_ip
            ON consultas (ip_usuario);
        """)
        conn.commit()


def registrar_consulta(
    ip_usuario: str,
    tipo_cliente: str,
    valor_compra: float,
    valor_cashback: float,
) -> dict:
    with get_connection() as conn:
        row = conn.execute(
            """
            INSERT INTO consultas (ip_usuario, tipo_cliente, valor_compra, valor_cashback)
            VALUES (%s, %s, %s, %s)
            RETURNING id, ip_usuario, tipo_cliente, valor_compra, valor_cashback, data_hora;
            """,
            (ip_usuario, tipo_cliente, valor_compra, valor_cashback),
        ).fetchone()
        conn.commit()
        return dict(row)


def buscar_historico(ip_usuario: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, tipo_cliente, valor_compra, valor_cashback, data_hora
            FROM consultas
            WHERE ip_usuario = %s
            ORDER BY data_hora DESC;
            """,
            (ip_usuario,),
        ).fetchall()
        return [dict(row) for row in rows]
