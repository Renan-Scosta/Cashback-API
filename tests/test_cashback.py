from decimal import Decimal

import pytest

from cashback import calcular_cashback


class TestCashbackBase:

    def test_cliente_normal_sem_promocao(self):
        resultado = calcular_cashback(Decimal("100"), is_vip=False)
        assert resultado["cashback_base"] == Decimal("5.00")
        assert resultado["bonus_vip"] == Decimal("0.00")
        assert resultado["promocao_aplicada"] is False
        assert resultado["cashback_total"] == Decimal("5.00")


class TestCashbackVIP:

    def test_cliente_vip_sem_promocao(self):
        resultado = calcular_cashback(Decimal("200"), is_vip=True)
        assert resultado["cashback_base"] == Decimal("10.00")
        assert resultado["bonus_vip"] == Decimal("1.00")
        assert resultado["cashback_total"] == Decimal("11.00")


class TestPromocao:

    @pytest.mark.parametrize(
        "valor, esperado_promo",
        [
            (Decimal("499.99"), False),
            (Decimal("500.00"), False),
            (Decimal("500.01"), True),
            (Decimal("501.00"), True),
        ],
        ids=["abaixo_limiar", "exato_500", "centavo_acima", "acima_limiar"],
    )
    def test_limiar_promocao(self, valor, esperado_promo):
        resultado = calcular_cashback(valor, is_vip=False)
        assert resultado["promocao_aplicada"] is esperado_promo

    def test_promocao_cliente_normal(self):
        resultado = calcular_cashback(Decimal("600"), is_vip=False)
        assert resultado["cashback_base"] == Decimal("30.00")
        assert resultado["promocao_aplicada"] is True
        assert resultado["cashback_total"] == Decimal("60.00")

    def test_promocao_cliente_vip(self):
        resultado = calcular_cashback(Decimal("600"), is_vip=True)
        assert resultado["cashback_base"] == Decimal("30.00")
        assert resultado["bonus_vip"] == Decimal("3.00")
        assert resultado["subtotal"] == Decimal("33.00")
        assert resultado["promocao_aplicada"] is True
        assert resultado["cashback_total"] == Decimal("66.00")


class TestCenariosProcessoSeletivo:

    def test_questao_2_vip_600_desconto_20(self):
        valor_final = Decimal("600") * (1 - Decimal("0.20"))
        resultado = calcular_cashback(valor_final, is_vip=True)

        assert resultado["valor_compra"] == Decimal("480")
        assert resultado["cashback_base"] == Decimal("24.00")
        assert resultado["bonus_vip"] == Decimal("2.40")
        assert resultado["promocao_aplicada"] is False
        assert resultado["cashback_total"] == Decimal("26.40")

    def test_questao_3_normal_600_desconto_10(self):
        valor_final = Decimal("600") * (1 - Decimal("0.10"))
        resultado = calcular_cashback(valor_final, is_vip=False)

        assert resultado["valor_compra"] == Decimal("540.00")
        assert resultado["cashback_base"] == Decimal("27.00")
        assert resultado["promocao_aplicada"] is True
        assert resultado["cashback_total"] == Decimal("54.00")

    def test_questao_4_vip_600_desconto_15(self):
        valor_final = Decimal("600") * (1 - Decimal("0.15"))
        resultado = calcular_cashback(valor_final, is_vip=True)

        assert resultado["valor_compra"] == Decimal("510.00")
        assert resultado["cashback_base"] == Decimal("25.50")
        assert resultado["bonus_vip"] == Decimal("2.55")
        assert resultado["subtotal"] == Decimal("28.05")
        assert resultado["promocao_aplicada"] is True
        assert resultado["cashback_total"] == Decimal("56.10")


class TestCasosDeBorda:

    def test_valor_zero(self):
        resultado = calcular_cashback(Decimal("0"), is_vip=False)
        assert resultado["cashback_total"] == Decimal("0.00")

    def test_valor_negativo_raises(self):
        with pytest.raises(ValueError, match="negativo"):
            calcular_cashback(Decimal("-10"), is_vip=False)

    def test_valor_muito_pequeno(self):
        resultado = calcular_cashback(Decimal("0.01"), is_vip=False)
        assert resultado["cashback_total"] == Decimal("0.00")

    def test_valor_grande(self):
        resultado = calcular_cashback(Decimal("10000"), is_vip=True)
        assert resultado["cashback_base"] == Decimal("500.00")
        assert resultado["bonus_vip"] == Decimal("50.00")
        assert resultado["promocao_aplicada"] is True
        assert resultado["cashback_total"] == Decimal("1100.00")
