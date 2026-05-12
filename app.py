import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Adriano Designer | Loja", layout="wide")

# CSS (Cabeçalho e Grid Mobile)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;700;800&display=swap');
    .header-container { display: flex; align-items: center; justify-content: center; gap: 15px; padding: 15px 0; }
    .logo-img { width: 65px; height: auto; border-radius: 8px; }
    .titulo-principal { font-family: 'Bebas Neue', sans-serif; font-size: clamp(30px, 8vw, 50px); color: #1a1c23; line-height: 0.9; margin: 0; }
    .destaque-verde { color: #25D366; }
    .loja-online-do { font-family: 'Inter', sans-serif; font-size: 10px; letter-spacing: 2px; color: #888; margin-bottom: -5px; font-weight: 700; }
    
    [data-testid="stHorizontalBlock"] { display: flex; flex-wrap: wrap; gap: 8px; }
    @media (max-width: 640px) {
        [data-testid="stHorizontalBlock"] > div { width: calc(50% - 8px) !important; flex: 1 1 calc(50% - 8px) !important; min-width: calc(50% - 8px) !important; }
    }
    .card-produto { background: white; border: 1px solid #eee; padding: 10px; border-radius: 12px; text-align: center; height: 100%; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARREGAMENTO DE DADOS
def carregar_dados():
    caminho = "produtos.csv"
    if os.path.exists(caminho):
        try:
            df = pd.read_csv(caminho)
            # Garante que colunas essenciais existam
            for col in ["id", "nome", "preco_venda", "promocao", "imagens"]:
                if col not in df.columns: df[col] = ""
            return df
        except: return pd.DataFrame()
    return pd.DataFrame()

if not os.path.exists("images"): os.makedirs("images")
df = carregar_dados()

# --- CABEÇALHO ---
logo_tag = ""
if os.path.exists("logo.png"):
    with open("logo.png", "rb") as f:
        logo_tag = f'<img src="data:image/png;base64,{base64.b64encode(f.read()).decode()}" class="logo-img">'

st.markdown(f'<div class="header-container">{logo_tag}<div><p class="loja-online-do">LOJA ONLINE DO:</p><h1 class="titulo-principal">ADRIANO <span class="destaque-verde">DESIGNER</span></h1></div></div>', unsafe_allow_html=True)

menu = st.sidebar.radio("Navegar", ["🛍️ Vitrine", "⚙️ Painel Admin"])

# --- VITRINE ---
if menu == "🛍️ Vitrine":
    if df.empty:
        st.info("Nenhum produto cadastrado.")
    else:
        cols = st.columns(2)
        for i, (idx, row) in enumerate(df.iterrows()):
            with cols[i % 2]:
                st.markdown('<div class="card-produto">', unsafe_allow_html=True)
                if os.path.exists(f"images/{row['imagens']}"):
                    st.image(f"images/{row['imagens']}", use_container_width=True)
                st.write(f"**{row['nome']}**")
                st.write(f"R$ {float(row['preco_venda']):.2f}")
                st.link_button("PEDIR", f"https://wa.me/5585998351874?text=Interesse: {row['nome']}")
                st.markdown('</div>', unsafe_allow_html=True)

# --- ADMIN (CORRIGIDO) ---
else:
    senha = st.sidebar.text_input("Senha", type="password")
    if senha == "suasenha123":
        # Recarrega o DF aqui dentro para garantir que Editar/Remover vejam os dados novos
        df = carregar_dados()
        
        tab1, tab2, tab3 = st.tabs(["➕ Cadastrar", "📝 Editar", "🗑️ Remover"])
        
        with tab1:
            with st.form("form_add", clear_on_submit=True):
                n = st.text_input("Nome")
                p = st.number_input("Preço", min_value=0.0)
                img = st.file_uploader("Foto", type=['jpg','png','jpeg'])
                cat = st.text_input("Categoria")
                if st.form_submit_button("SALVAR PRODUTO"):
                    if n and img:
                        fname = f"{int(datetime.now().timestamp())}_{img.name}"
                        with open(f"images/{fname}", "wb") as f: f.write(img.getbuffer())
                        novo = pd.DataFrame([{"id": int(datetime.now().timestamp()), "nome": n, "preco_venda": p, "imagens": fname, "categoria": cat}])
                        df = pd.concat([df, novo], ignore_index=True)
                        df.to_csv("produtos.csv", index=False)
                        st.success("Cadastrado!")
                        st.rerun()

        with tab2:
            if not df.empty:
                st.subheader("Selecione para editar")
                # Mostra lista de nomes para escolher
                prod_escolhido = st.selectbox("Produto", df["nome"].tolist())
                idx_original = df[df["nome"] == prod_escolhido].index[0]
                
                with st.form("form_edit"):
                    novo_nome = st.text_input("Nome", value=df.at[idx_original, 'nome'])
                    novo_preco = st.number_input("Preço", value=float(df.at[idx_original, 'preco_venda']))
                    if st.form_submit_button("ATUALIZAR"):
                        df.at[idx_original, 'nome'] = novo_nome
                        df.at[idx_original, 'preco_venda'] = novo_preco
                        df.to_csv("produtos.csv", index=False)
                        st.success("Atualizado!")
                        st.rerun()
            else:
                st.warning("Não há produtos para editar.")

        with tab3:
            if not df.empty:
                st.subheader("Excluir produtos")
                for i, row in df.iterrows():
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"🗑️ {row['nome']}")
                    if c2.button("Apagar", key=f"del_{row['id']}"):
                        df = df.drop(i)
                        df.to_csv("produtos.csv", index=False)
                        st.rerun()
            else:
                st.warning("Não há produtos para remover.")
    else:
        st.info("Insira a senha no menu lateral para acessar.")
