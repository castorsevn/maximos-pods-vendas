import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import os

st.set_page_config(page_title="Maximos Pods - Sistema de Vendas", layout="wide")

# ====================== CABEÇALHO ======================
st.markdown("""
    <h1 style='text-align: center; color: #FF4B4B;'>
        Maximos Pods
    </h1>
    <h3 style='text-align: center;'>Sistema de Controle de Vendas</h3>
    <hr>
""", unsafe_allow_html=True)

ARQUIVO = "vendas_maximos_pods.csv"

# Carregar ou criar arquivo
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

# ====================== FILTRO DE DATA (Calendário) ======================
st.sidebar.markdown("### 📅 Filtro por Período")

# Data padrão: últimos 30 dias
data_inicio = st.sidebar.date_input("Data Inicial", df['Data'].min() if not df.empty else datetime.today() - timedelta(days=30))
data_fim = st.sidebar.date_input("Data Final", datetime.today())

# Aplicar filtro
if not df.empty:
    mask = (df['Data'].dt.date >= data_inicio) & (df['Data'].dt.date <= data_fim)
    df_filtrado = df[mask].copy()
else:
    df_filtrado = df

# Menu lateral
aba = st.sidebar.selectbox("Escolha uma opção", 
    ["Nova Venda", "Dashboard", "Clientes", "Histórico Completo"])

st.sidebar.markdown("---")
st.sidebar.success("✅ Dados salvos automaticamente")

# ===================== NOVA VENDA =====================
if aba == "Nova Venda":
    st.subheader("📌 Registrar Nova Venda")
    
    col1, col2 = st.columns(2)
    with col1:
        data = st.date_input("Data da venda", datetime.today())
        cliente = st.text_input("Nome do Cliente *")
        whatsapp = st.text_input("WhatsApp")
        produto = st.text_input("Produto / Serviço *")
    
    with col2:
        valor_bruto = st.number_input("Valor Bruto (R$)", min_value=0.0, format="%.2f")
        custo = st.number_input("Custo (R$)", min_value=0.0, format="%.2f")
        forma = st.selectbox("Forma de Pagamento", ["Pix", "Cartão", "Boleto", "Dinheiro", "Outro"])
        status = st.selectbox("Status do Pagamento", ["Pago", "Pendente", "Reembolsado"])
    
    obs = st.text_area("Observação")
    
    if st.button("💾 Salvar Venda", type="primary", use_container_width=True):
        if cliente and produto and valor_bruto > 0:
            nova_linha = {
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
            df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
            salvar_dados(df)
            st.success("✅ Venda salva com sucesso!")
            st.rerun()
        else:
            st.error("Preencha os campos obrigatórios (Cliente, Produto e Valor)")

# ===================== DASHBOARD =====================
elif aba == "Dashboard":
    st.subheader(f"📊 Dashboard - Período: {data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}")
    
    if not df_filtrado.empty:
        faturamento = df_filtrado['Valor_Bruto'].sum()
        lucro = df_filtrado['Valor_Liquido'].sum()
        qtd_vendas = len(df_filtrado)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Faturamento Total", f"R$ {faturamento:,.2f}")
        col2.metric("Lucro Total", f"R$ {lucro:,.2f}")
        col3.metric("Total de Vendas", qtd_vendas)
        
        st.dataframe(df_filtrado.sort_values('Data', ascending=False), use_container_width=True)
    else:
        st.info("Nenhuma venda encontrada no período selecionado.")

# ===================== CLIENTES =====================
elif aba == "Clientes":
    st.subheader(f"👥 Clientes - Período: {data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}")
    
    if not df_filtrado.empty:
        clientes = df_filtrado.groupby('Cliente').agg({
            'Valor_Liquido': 'sum',
            'Data': 'count'
        }).reset_index()
        clientes.columns = ['Cliente', 'Total Gasto (R$)', 'Nº de Compras']
        st.dataframe(clientes.sort_values('Total Gasto (R$)', ascending=False), use_container_width=True)
    else:
        st.info("Nenhuma venda no período selecionado.")

# ===================== HISTÓRICO =====================
else:
    st.subheader(f"📋 Histórico Completo - Período: {data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}")
    if not df_filtrado.empty:
        st.dataframe(df_filtrado.sort_values('Data', ascending=False), use_container_width=True)
    else:
        st.info("Nenhuma venda encontrada no período.")

st.sidebar.caption("Maximos Pods © 2026")