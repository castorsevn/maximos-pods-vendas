import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px

st.set_page_config(page_title="Maximos Pods - Sistema", layout="wide")
st.title("🚀 Sistema de Vendas - Maximos Pods")

# ==================== Banco de Dados ====================
if 'df_vendas' not in st.session_state:
    st.session_state.df_vendas = pd.DataFrame(columns=[
        'Data', 'Cliente', 'WhatsApp', 'Produto', 'Valor_Bruto', 
        'Custo', 'Valor_Liquido', 'Forma_Pagamento', 'Status', 'Observacao'
    ])

if 'df_caixa' not in st.session_state:
    st.session_state.df_caixa = pd.DataFrame(columns=[
        'Data', 'Saldo_Inicial', 'Entradas_Vendas', 'Entradas_Extras',
        'Saidas', 'Saldo_Final', 'Observacao_Fechamento'
    ])

aba = st.sidebar.selectbox("Escolha a seção", 
    ["Dashboard", "Nova Venda", "Gestão de Caixa", "Clientes", "Histórico"])

# ====================== NOVA VENDA ======================
if aba == "Nova Venda":
    st.subheader("📌 Nova Venda")
    
    col1, col2 = st.columns(2)
    with col1:
        data = st.date_input("Data", datetime.today())
        cliente = st.text_input("Nome do Cliente *")
        whatsapp = st.text_input("WhatsApp")
        produto = st.text_input("Produto / Serviço *")
    
    with col2:
        valor = st.number_input("Valor Bruto (R$)", min_value=0.0, format="%.2f")
        custo = st.number_input("Custo (R$)", min_value=0.0, format="%.2f")
        pagamento = st.selectbox("Forma de Pagamento", ["Pix", "Cartão Crédito", "Cartão Débito", "Dinheiro"])
        status = st.selectbox("Status", ["Pago", "Pendente", "Reembolsado"])
    
    obs = st.text_area("Observação")
    
    if st.button("💾 Salvar Venda", type="primary"):
        if cliente and produto and valor > 0:
            novo = {
                'Data': data.strftime('%Y-%m-%d'),
                'Cliente': cliente,
                'WhatsApp': whatsapp,
                'Produto': produto,
                'Valor_Bruto': valor,
                'Custo': custo,
                'Valor_Liquido': valor - custo,
                'Forma_Pagamento': pagamento,
                'Status': status,
                'Observacao': obs
            }
            st.session_state.df_vendas = pd.concat([st.session_state.df_vendas, pd.DataFrame([novo])], ignore_index=True)
            st.success("✅ Venda salva com sucesso!")
        else:
            st.error("Preencha os campos obrigatórios (*)")

# ====================== GESTÃO DE CAIXA ======================
elif aba == "Gestão de Caixa":
    st.subheader("💰 Gestão de Caixa - Loja")

    data_caixa = st.date_input("Data do Caixa", datetime.today())
    data_str = data_caixa.strftime('%Y-%m-%d')

    # Vendas do dia
    vendas_dia = st.session_state.df_vendas[st.session_state.df_vendas['Data'] == data_str]
    entradas_vendas = vendas_dia['Valor_Bruto'].sum() if not vendas_dia.empty else 0.0

    col1, col2 = st.columns(2)
    with col1:
        saldo_inicial = st.number_input("💵 Saldo Inicial do Dia (R$)", min_value=0.0, value=0.0, format="%.2f")
    with col2:
        entradas_extras = st.number_input("➕ Entradas Extras (R$)", min_value=0.0, value=0.0, format="%.2f")

    saidas = st.number_input("➖ Saídas / Despesas (R$)", min_value=0.0, value=0.0, format="%.2f")
    obs_fechamento = st.text_area("Observação do Fechamento")

    if st.button("🔒 Fechar Caixa do Dia", type="primary"):
        saldo_final = saldo_inicial + entradas_vendas + entradas_extras - saidas
        
        novo_caixa = {
            'Data': data_str,
            'Saldo_Inicial': saldo_inicial,
            'Entradas_Vendas': entradas_vendas,
            'Entradas_Extras': entradas_extras,
            'Saidas': saidas,
            'Saldo_Final': saldo_final,
            'Observacao_Fechamento': obs_fechamento
        }
        
        st.session_state.df_caixa = pd.concat([st.session_state.df_caixa, pd.DataFrame([novo_caixa])], ignore_index=True)
        st.success(f"✅ Caixa fechado com sucesso! Saldo Final: R$ {saldo_final:,.2f}")

    # Resumo do dia
    st.subheader("📊 Resumo do Dia")
    st.info(f"""
    **Data:** {data_str}  
    **Vendas do Dia:** R$ {entradas_vendas:,.2f}  
    **Saldo Inicial:** R$ {saldo_inicial:,.2f}  
    **Entradas Extras:** R$ {entradas_extras:,.2f}  
    **Saídas:** R$ {saidas:,.2f}  
    **Saldo Final Estimado:** R$ {saldo_inicial + entradas_vendas + entradas_extras - saidas:,.2f}
    """)

    # Histórico de Caixas
    st.subheader("📋 Histórico de Fechamentos")
    if not st.session_state.df_caixa.empty:
        st.dataframe(st.session_state.df_caixa.sort_values('Data', ascending=False), use_container_width=True)
    else:
        st.info("Nenhum caixa fechado ainda.")

# ====================== DASHBOARD ======================
elif aba == "Dashboard":
    st.subheader("📊 Dashboard Geral")
    df = st.session_state.df_vendas
    
    if not df.empty:
        faturamento = df['Valor_Bruto'].sum()
        lucro = df['Valor_Liquido'].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Faturamento Total", f"R$ {faturamento:,.2f}")
        col2.metric("Lucro Total", f"R$ {lucro:,.2f}")
        col3.metric("Total de Vendas", len(df))
        
        st.dataframe(df.sort_values('Data', ascending=False), use_container_width=True)
    else:
        st.info("Nenhuma venda cadastrada ainda.")

# ====================== CLIENTES ======================
elif aba == "Clientes":
    st.subheader("👥 Clientes")
    df = st.session_state.df_vendas
    if not df.empty:
        clientes = df.groupby('Cliente').agg({
            'Valor_Liquido': 'sum',
            'Data': 'count'
        }).reset_index()
        clientes.columns = ['Cliente', 'Total Gasto (R$)', 'Quantidade de Compras']
        st.dataframe(clientes.sort_values('Total Gasto (R$)', ascending=False), use_container_width=True)
    else:
        st.info("Cadastre vendas para aparecer aqui.")

# ====================== HISTÓRICO ======================
else:
    st.subheader("📋 Histórico Completo de Vendas")
    if not st.session_state.df_vendas.empty:
        st.dataframe(st.session_state.df_vendas.sort_values('Data', ascending=False), use_container_width=True)
    else:
        st.info("Nenhuma venda ainda.")

st.sidebar.caption("Sistema de Vendas Maximos Pods\nDesenvolvido com Grok")