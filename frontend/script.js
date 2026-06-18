const API_BASE_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://localhost:8000"
    : window.location.origin; // Em produção, API e frontend são servidos pelo mesmo servidor

let userIp = null;


// Utilidades

function formatarBRL(valor) {
    return valor.toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL",
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
}

function formatarData(isoString) {
    return new Date(isoString).toLocaleDateString("pt-BR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}

function mostrarToast(mensagem, tipo = "error") {
    const existente = document.querySelector(".toast");
    if (existente) existente.remove();

    const toast = document.createElement("div");
    toast.className = `toast ${tipo}`;
    toast.textContent = mensagem;
    document.body.appendChild(toast);

    requestAnimationFrame(() => toast.classList.add("show"));

    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}


// Detecção de IP — tenta backend primeiro, fallback para ipify

async function detectarIp() {
    const ipElement = document.getElementById("user-ip");

    try {
        const res = await fetch(`${API_BASE_URL}/meu-ip`);
        if (res.ok) {
            const data = await res.json();
            if (data.ip && data.ip !== "unknown") {
                userIp = data.ip;
                ipElement.textContent = userIp;
                return;
            }
        }
    } catch (_) { /* fallback */ }

    try {
        const res = await fetch("https://api.ipify.org?format=json");
        if (res.ok) {
            const data = await res.json();
            userIp = data.ip;
            ipElement.textContent = userIp;
            return;
        }
    } catch (_) { /* fallback */ }

    userIp = "127.0.0.1";
    ipElement.textContent = "não detectado";
}


// API

async function calcularCashback(tipoCliente, valorCompra) {
    const response = await fetch(`${API_BASE_URL}/calcular`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tipo_cliente: tipoCliente, valor_compra: valorCompra }),
    });

    if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || `Erro ${response.status}`);
    }

    return response.json();
}


// UI — Resultado

function exibirResultado(resultado) {
    const container = document.getElementById("resultado");
    const isVip = resultado.tipo_cliente === "VIP";
    const hasPromo = resultado.promocao_aplicada;

    const badge = document.getElementById("resultado-badge");
    if (hasPromo) {
        badge.textContent = "🎉 Promoção ×2";
        badge.className = "resultado-badge promo";
    } else if (isVip) {
        badge.textContent = "⭐ VIP";
        badge.className = "resultado-badge vip";
    } else {
        badge.textContent = "Normal";
        badge.className = "resultado-badge normal";
    }

    document.getElementById("resultado-valor").textContent = formatarBRL(resultado.cashback_total);
    document.getElementById("detalhe-valor-compra").textContent = formatarBRL(resultado.valor_compra);
    document.getElementById("detalhe-cashback-base").textContent = formatarBRL(resultado.cashback_base);

    const rowVip = document.getElementById("row-bonus-vip");
    rowVip.hidden = !isVip;
    if (isVip) {
        document.getElementById("detalhe-bonus-vip").textContent = `+${formatarBRL(resultado.bonus_vip)}`;
    }

    document.getElementById("row-promocao").hidden = !hasPromo;
    document.getElementById("detalhe-total").textContent = formatarBRL(resultado.cashback_total);

    container.hidden = false;
}


// UI — Histórico

async function carregarHistorico() {
    if (!userIp) return;

    const loading = document.getElementById("historico-loading");
    const vazio = document.getElementById("historico-vazio");
    const lista = document.getElementById("historico-lista");

    loading.hidden = false;
    vazio.hidden = true;
    lista.hidden = true;

    try {
        const response = await fetch(`${API_BASE_URL}/historico/${encodeURIComponent(userIp)}`);
        if (!response.ok) throw new Error(`Erro ${response.status}`);

        const registros = await response.json();
        loading.hidden = true;

        if (registros.length === 0) {
            vazio.hidden = false;
            return;
        }

        lista.innerHTML = registros.map((r) => `
            <div class="historico-item">
                <span class="historico-tipo ${r.tipo_cliente === "VIP" ? "vip" : "normal"}">
                    ${r.tipo_cliente === "VIP" ? "⭐ VIP" : "Normal"}
                </span>
                <div class="historico-info">
                    <span class="historico-valor-compra">Compra: ${formatarBRL(r.valor_compra)}</span>
                    <span class="historico-data">${formatarData(r.data_hora)}</span>
                </div>
                <span class="historico-cashback">${formatarBRL(r.valor_cashback)}</span>
            </div>
        `).join("");

        lista.hidden = false;
    } catch (err) {
        loading.hidden = true;
        vazio.hidden = false;
        console.error("Erro ao carregar histórico:", err);
    }
}


// Init

document.addEventListener("DOMContentLoaded", async () => {
    await detectarIp();
    await carregarHistorico();

    const form = document.getElementById("cashback-form");
    const btnText = form.querySelector(".btn-text");
    const btnLoading = form.querySelector(".btn-loading");
    const btnCalc = document.getElementById("btn-calcular");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const tipoCliente = document.getElementById("tipo-cliente").value;
        const valorCompra = parseFloat(document.getElementById("valor-compra").value);

        if (!valorCompra || valorCompra <= 0) {
            mostrarToast("Informe um valor de compra válido.");
            return;
        }

        btnCalc.disabled = true;
        btnText.hidden = true;
        btnLoading.hidden = false;

        try {
            const resultado = await calcularCashback(tipoCliente, valorCompra);
            exibirResultado(resultado);
            mostrarToast("Cashback calculado com sucesso!", "success");
            await carregarHistorico();
        } catch (err) {
            mostrarToast(err.message || "Erro ao calcular cashback.");
        } finally {
            btnCalc.disabled = false;
            btnText.hidden = false;
            btnLoading.hidden = true;
        }
    });

    document.getElementById("btn-refresh").addEventListener("click", async () => {
        const btn = document.getElementById("btn-refresh");
        btn.style.transform = "rotate(360deg)";
        btn.style.transition = "transform 0.5s ease";
        await carregarHistorico();
        setTimeout(() => { btn.style.transform = ""; }, 500);
    });
});
