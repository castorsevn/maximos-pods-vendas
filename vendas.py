import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import os
import time

st.set_page_config(page_title="Maximos Pods", layout="wide", initial_sidebar_state="expanded")

# ====================== CSS - Visual Digital ======================
st.markdown("""
    <style>
    .main {background-color: #0E1117;}
    .big-number {font-size: 2.8rem; font-weight: bold; color: #00FF88; text-align: center; margin: 0;}
    .clock {font-size: 1.4rem; color: #00FF88; font-family: 'Courier New', monospace; text-align: center;}
    hr {border-color: #333;}
    </style>
""", unsafe_allow_html=True)

# ====================== LOGO + BANNER ======================
col1, col2 = st.columns([1, 5])
with col1:
    st.markdown("**MAXIMOS PODS**")
with col2:
    st.markdown("""
        <h1 style='margin: 0; color: #FF4B4B;'>MAXIMOS PODS</h1>
        <p style='color: #AAAAAA; margin: 0;'>Sistema Profissional de Vendas</p>
    """, unsafe_allow_html=True)

st.markdown("---")

ARQUIVO = "vendas_maximos_pods.csv"

def carregar_dados():
    if os.path.exists(ARQUIVO):
        df = pd.read_csv(ARQUIVO)
        df['Data'] = pd.to_datetime(df['Data'])
        return df
    else:
        df = pd.DataFrame(columns=['Data', 'Cliente', 'WhatsApp', 'Produto', 'Valor_Bruto', 
                                 'Custo', 'Valor_Liquido', 'Forma_Pagamento', 'Status', 'Observacao'])
        df.to_csv(ARQUIVO, index=False)
        return df

def salvar_dados(df):
    df_copy = df.copy()
    df_copy['Data'] = df_copy['Data'].dt.strftime('%Y-%m-%d')
    df_copy.to_csv(ARQUIVO, index=False)

df = carregar_dados()

# ====================== FILTRO ======================
st.sidebar.markdown("### 📅 Filtro por Período")
data_inicio = st.sidebar.date_input("Data Inicial", datetime.today() - timedelta(days=30))
data_fim = st.sidebar.date_input("Data Final", datetime.today())

if not df.empty:
    mask = (df['Data'].dt.date >= data_inicio) & (df['Data'].dt.date <= data_fim)
    df_filtrado = df[mask].copy()
else:
    df_filtrado = df

aba = st.sidebar.selectbox("Menu", ["Nova Venda", "Dashboard", "Clientes", "Histórico Completo"])

# ===================== NOVA VENDA =====================
if aba == "Nova Venda":
    st.subheader("📌 Nova Venda")
    col1, col2 = st.columns(2)
    with col1:
        data = st.date_input("Data", datetime.today())
        cliente = st.text_input("Nome do Cliente *")
        whatsapp = st.text_input("WhatsApp")
        produto = st.text_input("Produto / Serviço *")
    
    with col2:
        valor_bruto = st.number_input("Valor Bruto (R$)", min_value=0.0, format="%.2f")
        custo = st.number_input("Custo (R$)", min_value=0.0, format="%.2f")
        forma = st.selectbox("Forma de Pagamento", ["Pix", "Cartão", "Boleto", "Dinheiro", "Outro"])
        status = st.selectbox("Status", ["Pago", "Pendente", "Reembolsado"])
    
    obs = st.text_area("Observação")
    
    if st.button("💾 Salvar Venda", type="primary", use_container_width=True):
        if cliente and produto and valor_bruto > 0:
            nova = {
                'Data': data.strftime('%Y-%m-%d'),
                'Cliente': cliente,
                'WhatsApp': whatsapp,
                'Produto': produto,
                'Valor_Bruto': valor_bruto,
                'Custo': custo,
                'Valor_Liquido': round(valor_bruto - custo, 2),
                'Forma_Pagamento': forma,
                'Status': status,
                'Observacao': obs
            }
            df = pd.concat([df, pd.DataFrame([nova])], ignore_index=True)
            salvar_dados(df)
            st.success("✅ Venda salva com sucesso!")
            st.rerun()
        else:
            st.error("Preencha os campos obrigatórios")

# ===================== DASHBOARD =====================
elif aba == "Dashboard":
    st.subheader("📊 Dashboard")
    if not df_filtrado.empty:
        fat = df_filtrado['Valor_Bruto'].sum()
        lucro = df_filtrado['Valor_Liquido'].sum()
        qtd = len(df_filtrado)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Vendas", f"{qtd} un")
        col2.metric("Faturamento", f"R$ {fat:,.2f}")
        col3.metric("Lucro", f"R$ {lucro:,.2f}")
        
        st.bar_chart(df_filtrado.groupby(df_filtrado['Data'].dt.date)['Valor_Liquido'].sum())
    else:
        st.info("Nenhuma venda no período selecionado.")

# ===================== CLIENTES =====================
elif aba == "Clientes":
    st.subheader("👥 Clientes")
    if not df_filtrado.empty:
        clientes = df_filtrado.groupby('Cliente').agg({'Valor_Liquido':'sum', 'Data':'count'}).reset_index()
        clientes.columns = ['Cliente', 'Total Gasto', 'Compras']
        st.dataframe(clientes.sort_values('Total Gasto', ascending=False), use_container_width=True)

# ===================== HISTÓRICO =====================
else:
    st.subheader("📋 Histórico Completo")
    if not df_filtrado.empty:
        st.dataframe(df_filtrado.sort_values('Data', ascending=False), use_container_width=True)

# ===================== CONTADOR DE HORAS + STATUS =====================
st.markdown("---")
col_a, col_b, col_c = st.columns([3, 2, 3])

with col_b:
    st.markdown(f"""
        <div style='text-align: center;'>
            <p style='margin:0; color:#666;'>🕒 Hora atual</p>
            <p class='clock' id='clock'>{datetime.now().strftime('%H:%M:%S')}</p>
        </div>
    """, unsafe_allow_html=True)

st.caption("✅ Dados salvos automaticamente em tempo real | Maximos Pods © 2026")

# Atualização automática do relógio (JavaScript)
st.markdown("""
    <script>
        function updateClock() {
            const now = new Date();
            const timeString = now.getHours().toString().padStart(2, '0') + ':' + 
                              now.getMinutes().toString().padStart(2, '0') + ':' + 
                              now.getSeconds().toString().padStart(2, '0');
            document.getElementById('clock').innerText = timeString;
        }
        setInterval(updateClock, 1000);
    </script>
""", unsafe_allow_html=True)