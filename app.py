import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO E DESIGN
st.set_page_config(page_title="Adriano Designer | Loja Oficial", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;700;800&display=swap');
    
    .stApp { background-color: #f8f9fa; }
    
    /* Container que agrupa Logo e Nome */
    .brand-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px; /* Espaço entre a logo e o texto */
        margin-bottom: 0px;
    }

    .text-box {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }
    
    .loja-online-do {
        font-family: 'Inter', sans-serif;
        font-size: 11px;
        letter-spacing: 2px;
        color: #888;
        margin-bottom: -10px;
        font-weight: 700;
        text-transform: uppercase;
    }
    
    .titulo-principal { 
        font-family: 'Bebas Neue', sans-serif; 
        font-size: 60px; 
        color: #1a1c23; 
        line-height: 1;
        margin: 0;
    }
    
    .destaque-verde { color: #25D366; }
    
    .search-label {
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        font-weight: 800;
        color: #1a1c23;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 10px;
        letter-spacing: 1px;
    }

    .card-produto { 
        background-color: #ffffff; border: 1px solid #e9ecef; padding: 15px; 
        border-radius: 15px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        position: relative; height: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÕES DE DADOS
def carregar_dados():
    caminho = "produtos.csv"
    if os.path.exists(caminho):
        try:
            df = pd.read_csv(caminho)
            cols = ["nome", "preco", "imagens", "categoria", "subcategoria", "descricao", "novidade"]
            for col in cols:
                if col not in df.columns: df[col] = ""
            return df
        except: pass
    return pd.DataFrame(columns=["nome", "preco", "imagens", "categoria", "subcategoria", "descricao", "novidade"])

if not os.path.exists("images"): os.makedirs("images")
df = carregar_dados()

# --- CABEÇALHO COMPACTO (LOGO À ESQUERDA) ---
# Usamos colunas para centralizar o bloco inteiro na tela
_, col_header, _ = st.columns([1, 4, 1])

with col_header:
    col_logo, col_texto = st.columns([1, 4])
    with col_logo:
        if os.path.exists("logo.png"):
            # Logo pequena e alinhada
            st.image("logo.png", width=80) 
    with col_texto:
        st.markdown("""
            <div class="text-box">
                <p class="loja-online-do">LOJA ONLINE DO:</p>
                <h1 class="titulo-principal">ADRIANO <span class="destaque-verde">DESIGNER</span></h1>
            </div>
        """, unsafe_allow_html=True)

# --- MENU DE ACESSIBILIDADE ---
st.markdown('<p class="search-label">PROCURE SEU ESTILO AQUI.</p>', unsafe_allow_html=True)

# Filtros centrais
c1, c2 = st.columns(2)
with c1:
    cats_existentes = ["Todos os Produtos"] + sorted(df["categoria"].unique().astype(str).tolist())
    cat_sel = st.selectbox("CATEGORIA", cats_existentes, label_visibility="collapsed")

with c2:
    df_f = df if cat_sel == "Todos os Produtos" else df[df["categoria"] == cat_sel]
    subs_existentes = ["Todas as Subcategorias"] + sorted(df_f["subcategoria"].unique().astype(str).tolist())
    sub_sel = st.selectbox("SUBCATEGORIA", subs_existentes, label_visibility="collapsed")

if sub_sel != "Todas as Subcategorias": 
    df_f = df_f[df_f["subcategoria"] == sub_sel]

st.divider()

# --- NAVEGAÇÃO LATERAL ---
menu_principal = st.sidebar.radio("Navegar", ["🛍️ Vitrine", "⚙️ Painel Admin"])

# --- VITRINE ---
if menu_principal == "🛍️ Vitrine":
    if df.empty:
        st.info("Nenhum produto disponível.")
    else:
        cols = st.columns(3)
        for i, (idx, row) in enumerate(df_f.iterrows()):
            with cols[i % 3]:
                st.markdown('<div class="card-produto">', unsafe_allow_html=True)
                if os.path.exists(f"images/{row['imagens']}"):
                    st.image(f"images/{row['imagens']}", use_container_width=True)
                st.write(f"**{row['nome']}**")
                st.caption(f"{row['categoria']} | {row['subcategoria']}")
                st.write(f"### R$ {float(row['preco']):.2f}")
                st.link_button("VER NO WHATSAPP", f"https://wa.me/5585998351874?text=Olá Adriano! Vi o produto {row['nome']}")
                st.markdown('</div>', unsafe_allow_html=True)

# --- ADMIN ---
else:
    senha = st.text_input("Senha Admin", type="password")
    if senha == "suasenha123":
        t1, t2, t3 = st.tabs(["➕ Novo", "📝 Editar", "🗑️ Remover"])
        
        sugestoes_cat = sorted(df["categoria"].unique().astype(str).tolist()) if not df.empty else []
        sugestoes_sub = sorted(df["subcategoria"].unique().astype(str).tolist()) if not df.empty else []

        with t1:
            with st.form("form_novo", clear_on_submit=True):
                nome = st.text_input("Nome")
                preco = st.number_input("Preço", min_value=0.0)
                col_a, col_b = st.columns(2)
                with col_a:
                    cat_op = st.selectbox("Categoria", ["+ Nova"] + sugestoes_cat)
                    cat_f = st.text_input("Qual nome da categoria?") if cat_op == "+ Nova" else cat_op
                with col_b:
                    sub_op = st.selectbox("Subcategoria", ["+ Nova"] + sugestoes_sub)
                    sub_f = st.text_input("Qual nome da subcategoria?") if sub_op == "+ Nova" else sub_op
                foto = st.file_uploader("Imagem", type=['jpg', 'png', 'jpeg'])
                if st.form_submit_button("CADASTRAR"):
                    if nome and foto and cat_f:
                        nome_arq = f"{datetime.now().timestamp()}_{foto.name}"
                        with open(f"images/{nome_arq}", "wb") as f: f.write(foto.getbuffer())
                        novo = pd.DataFrame([{"nome": nome, "preco": preco, "imagens": nome_arq, "categoria": cat_f, "subcategoria": sub_f}])
                        df = pd.concat([df, novo], ignore_index=True)
                        df.to_csv("produtos.csv", index=False)
                        st.rerun()

        with t2: # EDITAR
            if not df.empty:
                escolha = st.selectbox("Editar:", df["nome"].tolist())
                idx = df[df["nome"] == escolha].index[0]
                with st.form("f_edit"):
                    df.at[idx, 'nome'] = st.text_input("Nome", value=df.at[idx, 'nome'])
                    df.at[idx, 'preco'] = st.number_input("Preço", value=float(df.at[idx, 'preco']))
                    if st.form_submit_button("SALVAR"):
                        df.to_csv("produtos.csv", index=False)
                        st.rerun()

        with t3: # REMOVER
            for i, row in df.iterrows():
                if st.button(f"Remover {row['nome']}", key=f"del_{i}"):
                    df = df.drop(i)
                    df.to_csv("produtos.csv", index=False)
                    st.rerun()
