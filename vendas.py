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
                    Forma_Pagamento TEXT, Status TEXT, Observacao TEXT)''')
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
                        Valor_Liquido, Forma_Pagamento, Status, Observacao) 
                        VALUES (?,?,?,?,?,?,?,?,?,?)""", 
                     (venda['Data'], venda['Cliente'], venda['WhatsApp'], venda['Produto'],
                      venda['Valor_Bruto'], venda['Custo'], venda['Valor_Liquido'],
                      venda['Forma_Pagamento'], venda['Status'], venda['Observacao']))
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
    st.title("MAXIMOS PODS")

try: st.image(BANNER_URL, use_container_width=True)
except: pass

st.markdown("---")

if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None

df = carregar_vendas()

aba = st.sidebar.selectbox("Menu", ["Nova Venda", "Dashboard", "Clientes", "Histórico Completo"])

# Filtro
st.sidebar.markdown("### 📅 Filtro")
data_inicio = st.sidebar.date_input("Início", datetime.today() - timedelta(days=30))
data_fim = st.sidebar.date_input("Fim", datetime.today())

if not df.empty:
    mask = (df['Data'].dt.date >= data_inicio) & (df['Data'].dt.date <= data_fim)
    df_filtrado = df[mask].copy()
else:
    df_filtrado = pd.DataFrame()

# ====================== NOVA VENDA / EDIÇÃO ======================
if aba == "Nova Venda":
    edit_id = st.session_state.edit_id
    edit_data = df[df['id'] == edit_id].iloc[0] if edit_id is not None and not df.empty else None

    st.subheader("✏️ Editar Venda" if edit_id else "📌 Nova Venda")

    col1, col2 = st.columns(2)
    with col1:
        data = st.date_input("Data", value=pd.to_datetime(edit_data['Data']) if edit_data is not None else datetime.today())
        cliente = st.text_input("Cliente *", value=edit_data['Cliente'] if edit_data is not None else "")
        whatsapp = st.text_input("WhatsApp", value=edit_data.get('WhatsApp', '') if edit_data is not None else "")
        produto = st.text_input("Produto *", value=edit_data['Produto'] if edit_data is not None else "")
    
    with col2:
        valor = st.number_input("Valor Bruto R$", min_value=0.0, format="%.2f", 
                               value=float(edit_data['Valor_Bruto']) if edit_data is not None else 0.0)
        custo = st.number_input("Custo R$", min_value=0.0, format="%.2f", 
                               value=float(edit_data['Custo']) if edit_data is not None else 0.0)
        forma = st.selectbox("Pagamento", ["Pix", "Cartão", "Boleto", "Dinheiro", "Outro"], 
                            index=0 if edit_data is None else ["Pix","Cartão","Boleto","Dinheiro","Outro"].index(edit_data['Forma_Pagamento']))
        status = st.selectbox("Status", ["Pago", "Pendente", "Reembolsado"], 
                             index=0 if edit_data is None else ["Pago","Pendente","Reembolsado"].index(edit_data['Status']))
    
    obs = st.text_area("Observação", value=edit_data.get('Observacao','') if edit_data is not None else "")

    if st.button("💾 Salvar" if not edit_id else "💾 Atualizar Venda", type="primary", use_container_width=True):
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
            salvar_venda(nova, edit_id)
            st.success("✅ Salvo com sucesso!")
            st.session_state.edit_id = None
            st.rerun()

# ====================== DASHBOARD ======================
elif aba == "Dashboard":
    st.subheader("📊 Dashboard")
    if not df_filtrado.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Vendas", len(df_filtrado))
        col2.metric("Faturamento", f"R$ {df_filtrado['Valor_Bruto'].sum():,.2f}")
        col3.metric("Lucro", f"R$ {df_filtrado['Valor_Liquido'].sum():,.2f}")

# ====================== CLIENTES ======================
elif aba == "Clientes":
    st.subheader("👥 Clientes")
    if not df_filtrado.empty:
        clientes = df_filtrado.groupby('Cliente').agg({'Valor_Liquido':'sum', 'Data':'count'}).reset_index()
        clientes.columns = ['Cliente', 'Total Gasto (R$)', 'Nº Compras']
        st.dataframe(clientes.sort_values('Total Gasto (R$)', ascending=False), use_container_width=True)

# ====================== HISTÓRICO COM EDITAR E EXCLUIR ======================
else:
    st.subheader("📋 Histórico Completo")
    if not df_filtrado.empty:
        for _, row in df_filtrado.iterrows():
            c1, c2, c3, c4 = st.columns([3.5, 2, 1, 1])
            with c1:
                st.write(f"**{row['Cliente']}** — {row['Produto']}")
                st.caption(f"{row['Data'].strftime('%d/%m/%Y')} | {row['Status']}")
            with c2:
                st.metric("Valor", f"R$ {row['Valor_Bruto']:,.2f}")
            with c3:
                if st.button("✏️ Editar", key=f"edit_{row['id']}"):
                    st.session_state.edit_id = row['id']
                    st.rerun()
            with c4:
                if st.button("🗑️ Excluir", key=f"del_{row['id']}"):
                    excluir_venda(row['id'])
                    st.success("Venda excluída!")
                    st.rerun()
            st.divider()
    else:
        st.info("Nenhuma venda encontrada.")

# ====================== RODAPÉ ======================
st.markdown("---")
agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
st.caption(f"🕒 Horário de Brasília: {agora.strftime('%H:%M:%S')} | Maximos Pods")
