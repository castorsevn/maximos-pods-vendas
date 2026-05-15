import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import sqlite3
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Maximos Pods", layout="wide")

# ====================== CONFIG ======================
GITHUB_USER = "castorsevn"
REPO_NAME = "maximos-pods-vendas"

LOGO_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/logo.jfif"
BANNER_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/banner.jfif"

DB_FILE = "vendas_maximos_pods.db"

# ====================== BANCO ======================
def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS vendas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Data TEXT, Cliente TEXT, WhatsApp TEXT, Produto TEXT,
                    Valor_Bruto REAL, Custo REAL, Valor_Liquido REAL,
                    Forma_Pagamento TEXT, Status TEXT, Observacao TEXT,
                    Data_Criacao TEXT)''')
    conn.commit()
    conn.close()

init_db()

def salvar_venda(venda, venda_id=None):
    conn = get_connection()
    if venda_id:
        conn.execute("""UPDATE vendas SET Data=?, Cliente=?, WhatsApp=?, Produto=?, 
                        Valor_Bruto=?, Custo=?, Valor_Liquido=?, Forma_Pagamento=?, 
                        Status=?, Observacao=? WHERE id=?""", 
                     (venda['Data'], venda['Cliente'], venda['WhatsApp'], venda['Produto'],
                      venda['Valor_Bruto'], venda['Custo'], venda['Valor_Liquido'],
                      venda['Forma_Pagamento'], venda['Status'], venda['Observacao'], venda_id))
    else:
        conn.execute("""INSERT INTO vendas (Data, Cliente, WhatsApp, Produto, Valor_Bruto, Custo, 
                        Valor_Liquido, Forma_Pagamento, Status, Observacao, Data_Criacao)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?)""", 
                     (venda['Data'], venda['Cliente'], venda['WhatsApp'], venda['Produto'],
                      venda['Valor_Bruto'], venda['Custo'], venda['Valor_Liquido'],
                      venda['Forma_Pagamento'], venda['Status'], venda['Observacao'],
                      datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

def carregar_vendas():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM vendas ORDER BY id DESC", conn)
    if not df.empty:
        df['Data'] = pd.to_datetime(df['Data'])
    conn.close()
    return df

def excluir_venda(venda_id):
    conn = get_connection()
    conn.execute("DELETE FROM vendas WHERE id=?", (venda_id,))
    conn.commit()
    conn.close()

# ====================== CABEÇALHO ======================
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    try: st.image(LOGO_URL, width=120)
    except: pass
with col_titulo:
    st.markdown("<h1 style='color:#FF4B4B; margin:0;'>MAXIMOS PODS</h1>", unsafe_allow_html=True)

try:
    st.image(BANNER_URL, use_container_width=True)
except:
    st.markdown("---")

# ====================== FORÇA ATUALIZAÇÃO ======================
if st.button("🔄 Atualizar Tudo", type="secondary"):
    st.rerun()

df = carregar_vendas()

st.sidebar.markdown("### 📅 Filtro")
data_inicio = st.sidebar.date_input("Início", datetime.today() - timedelta(days=30))
data_fim = st.sidebar.date_input("Fim", datetime.today())

if not df.empty:
    mask = (df['Data'].dt.date >= data_inicio) & (df['Data'].dt.date <= data_fim)
    df_filtrado = df[mask].copy()
else:
    df_filtrado = df

aba = st.sidebar.selectbox("Menu", ["Nova Venda", "Dashboard", "Clientes", "Histórico"])

# ====================== NOVA VENDA ======================
if aba == "Nova Venda":
    st.subheader("📌 Nova Venda")
    col1, col2 = st.columns(2)
    with col1:
        data = st.date_input("Data", datetime.today())
        cliente = st.text_input("Cliente *")
        whatsapp = st.text_input("WhatsApp")
        produto = st.text_input("Produto *")
    with col2:
        valor = st.number_input("Valor Bruto R$", min_value=0.0, format="%.2f")
        custo = st.number_input("Custo R$", min_value=0.0, format="%.2f")
        forma = st.selectbox("Pagamento", ["Pix", "Cartão", "Boleto", "Dinheiro"])
        status = st.selectbox("Status", ["Pago", "Pendente", "Reembolsado"])
    
    obs = st.text_area("Observação")

    if st.button("💾 Salvar Venda", type="primary", use_container_width=True):
        if cliente and produto and valor > 0:
            nova = {
                'Data': data.strftime('%Y-%m-%d'),
                'Cliente': cliente,
                'WhatsApp': whatsapp,
                'Produto': produto,
                'Valor_Bruto': valor,
                'Custo': custo,
                'Valor_Liquido': round(valor - custo, 2),
                'Forma_Pagamento': forma,
                'Status': status,
                'Observacao': obs
            }
            salvar_venda(nova)
            st.success("✅ Venda salva!")
            st.rerun()
        else:
            st.error("Preencha os campos obrigatórios")

# ====================== HISTÓRICO (com atualização forte) ======================
elif aba == "Histórico":
    st.subheader("📋 Histórico Completo")
    if not df_filtrado.empty:
        for _, row in df_filtrado.iterrows():
            c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
            with c1:
                st.write(f"**{row['Cliente']}** - {row['Produto']}")
                st.caption(f"{row['Data'].strftime('%d/%m/%Y')} | {row['Status']}")
            with c2:
                st.metric("Valor", f"R$ {row['Valor_Bruto']:,.2f}")
            with c3:
                if st.button("✏️", key=f"ed{row['id']}"):
                    st.session_state.edit_id = row['id']
                    st.switch_page("vendas.py")
            with c4:
                if st.button("🗑️", key=f"del{row['id']}"):
                    excluir_venda(row['id'])
                    st.rerun()
            st.divider()
    else:
        st.info("Nenhuma venda encontrada")

# Outras abas (Dashboard e Clientes) simplificadas
else:
    st.info("Use o botão 🔄 Atualizar Tudo no topo se não atualizar")

# ====================== RODAPÉ ======================
st.markdown("---")
agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
st.markdown(f"**🕒 Brasília:** {agora.strftime('%H:%M:%S')} | Atualize com o botão acima")

st.caption("Maximos Pods © 2026")