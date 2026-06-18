from decimal import Decimal

from pydantic import BaseModel, field_validator


class CalcularRequest(BaseModel):
    tipo_cliente: str
    valor_compra: float

    @field_validator("tipo_cliente")
    @classmethod
    def validar_tipo_cliente(cls, v: str) -> str:
        valor = v.strip()
        normalizado = valor.upper() if valor.upper() == "VIP" else valor.capitalize()
        if normalizado not in ("VIP", "Normal"):
            raise ValueError("tipo_cliente deve ser 'VIP' ou 'Normal'.")
        return normalizado

    @field_validator("valor_compra")
    @classmethod
    def validar_valor_compra(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("valor_compra deve ser maior que zero.")
        return v


class CalcularResponse(BaseModel):
    tipo_cliente: str
    valor_compra: float
    cashback_base: float
    bonus_vip: float
    subtotal: float
    promocao_aplicada: bool
    cashback_total: float


class HistoricoItem(BaseModel):
    id: int
    tipo_cliente: str
    valor_compra: float
    valor_cashback: float
    data_hora: str
