from decimal import Decimal, ROUND_HALF_UP

CASHBACK_BASE_RATE = Decimal("0.05")
VIP_BONUS_RATE = Decimal("0.10")
PROMO_THRESHOLD = Decimal("500")
PROMO_MULTIPLIER = Decimal("2")

TWO_PLACES = Decimal("0.01")


def _quantize(value: Decimal) -> Decimal:
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def calcular_cashback(valor_compra: Decimal, is_vip: bool) -> dict:
    """Calcula o cashback detalhado com base no valor da compra e tipo de cliente.

    Ordem de cálculo (conforme regras de negócio):
        1. Cashback base = 5% do valor da compra
        2. Bônus VIP = 10% do cashback base (se aplicável)
        3. Promoção: valor > R$500 → cashback total × 2
    """
    if valor_compra < Decimal("0"):
        raise ValueError("O valor da compra não pode ser negativo.")

    cashback_base = _quantize(valor_compra * CASHBACK_BASE_RATE)

    bonus_vip = Decimal("0.00")
    if is_vip:
        bonus_vip = _quantize(cashback_base * VIP_BONUS_RATE)

    subtotal = cashback_base + bonus_vip

    promocao_aplicada = valor_compra > PROMO_THRESHOLD
    cashback_total = _quantize(subtotal * PROMO_MULTIPLIER) if promocao_aplicada else subtotal

    return {
        "valor_compra": valor_compra,
        "is_vip": is_vip,
        "cashback_base": cashback_base,
        "bonus_vip": bonus_vip,
        "subtotal": subtotal,
        "promocao_aplicada": promocao_aplicada,
        "cashback_total": cashback_total,
    }
