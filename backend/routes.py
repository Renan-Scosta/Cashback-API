from datetime import datetime
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, HTTPException, Request

from cashback import calcular_cashback
from database import registrar_consulta, buscar_historico
from schemas import CalcularRequest, CalcularResponse, HistoricoItem

router = APIRouter()


def obter_ip_cliente(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.get("/meu-ip")
async def meu_ip(request: Request):
    return {"ip": obter_ip_cliente(request)}


@router.post("/calcular", response_model=CalcularResponse)
async def calcular(dados: CalcularRequest, request: Request):
    ip_cliente = obter_ip_cliente(request)
    is_vip = dados.tipo_cliente == "VIP"

    try:
        valor_decimal = Decimal(str(dados.valor_compra))
    except InvalidOperation:
        raise HTTPException(status_code=400, detail="Valor de compra inválido.")

    resultado = calcular_cashback(valor_decimal, is_vip)

    registrar_consulta(
        ip_usuario=ip_cliente,
        tipo_cliente=dados.tipo_cliente,
        valor_compra=float(resultado["valor_compra"]),
        valor_cashback=float(resultado["cashback_total"]),
    )

    return CalcularResponse(
        tipo_cliente=dados.tipo_cliente,
        valor_compra=float(resultado["valor_compra"]),
        cashback_base=float(resultado["cashback_base"]),
        bonus_vip=float(resultado["bonus_vip"]),
        subtotal=float(resultado["subtotal"]),
        promocao_aplicada=resultado["promocao_aplicada"],
        cashback_total=float(resultado["cashback_total"]),
    )


@router.get("/historico/{ip}", response_model=list[HistoricoItem])
async def historico(ip: str):
    registros = buscar_historico(ip)
    return [
        HistoricoItem(
            id=r["id"],
            tipo_cliente=r["tipo_cliente"],
            valor_compra=float(r["valor_compra"]),
            valor_cashback=float(r["valor_cashback"]),
            data_hora=r["data_hora"].isoformat() if isinstance(r["data_hora"], datetime) else str(r["data_hora"]),
        )
        for r in registros
    ]
