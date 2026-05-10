import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO DE DESIGN
st.set_page_config(page_title="Adriano Designer | Studio", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    /* 1. FUNDO DA PÁGINA (CINZA BEM CLARO) */
    .stApp {
        background-color: #f4f4f6;
    }

    /* 2. CARD DO PRODUTO (BRANCO OU CINZA QUASE BRANCO) */
    div[data-testid="column"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    /* 3. NOME DO PRODUTO (CINZA ESCURO / GRAFITE) */
    .nome-produto {
        color: #2c2c2c !important; 
        font-size: 22px !important;
        font-weight: 700 !important;
        margin-top: 15px !important;
        margin-bottom: 5px !important;
        display: block;
    }

    /* Categoria e Subcategoria */
    .categoria-texto {
        color: #7a7a7a !important;
        font-size: 13px;
        text-transform: uppercase;
        font-weight: 500;
    }

    /* Badge de Destaque */
    .badge-destaque {
        background-color: #25D366;
        color: white !important;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 11px;
        margin-bottom: 10px;
        display: inline-block;
    }

    /* Preço e Botão */
    h2.preco { color: #128C7E !important; font-weight: 800; }
    
    h1, h2, h3, p { color: #333333 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÃO DE DADOS
def carregar_dados():
    colunas_obrigatorias = ["nome", "preco", "imagens", "categoria", "subcategoria", "descricao"]
    if os.path.exists("produtos.csv"):
        df = pd.read_csv("produtos.csv")
        for col in colunas_obrigatorias:
            if col not in df.columns: df[col] = ""
        return df
    return pd.DataFrame(columns=colunas_obrigatorias)

# --- CABEÇALHO ---
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)

with col_titulo:
    st.markdown("<h1 style='margin-bottom:0;'>ADRIANO <span style='color: #25D366;'>DESIGNER</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:18px; color:#555;'>Estúdio de Criação & Personalizados Premium</p>", unsafe_allow_html=True)

st.markdown("---")

# --- VITRINE ---
df = carregar_dados()

if not df.empty:
    # Menu de categorias visível
    categorias = ["Todos"] + sorted(df["categoria"].unique().astype(str).tolist())
    escolha_cat = st.radio("Navegue pelas Coleções:", categorias, horizontal=True)
    
    df_view = df if escolha_cat == "Todos" else df[df["categoria"] == escolha_cat]
    df_view = df_view.iloc[::-1] # Mais recentes primeiro

    cols = st.columns(3)
    for i, (idx, row) in enumerate(df_view.iterrows()):
        with cols[i % 3]:
            # Destaque automático para os últimos 3
            if idx in df.index[-3:]:
                st.markdown('<div class="badge-destaque">NOVIDADE</div>', unsafe_allow_html=True)
            
            # Imagem do Produto
            fotos = str(row['imagens']).split(",")
            if os.path.exists(f"images/{fotos[0]}"):
                st.image(f"images/{fotos[0]}", use_container_width=True)
            
            # Exibição dos Textos com as cores novas
            st.markdown(f'<span class="nome-produto">{row["nome"]}</span>', unsafe_allow_html=True)
            st.markdown(f'<span class="categoria-texto">{row["categoria"]} | {row["subcategoria"]}</span>', unsafe_allow_html=True)
            
            with st.expander("Detalhes do Produto"):
                st.write(row['descricao'])
            
            preco_val = f"R$ {row['preco']:.2f}" if row['preco'] > 0 else "CONSULTAR"
            st.markdown(f"<h2 class='preco'>{preco_val}</h2>", unsafe_allow_html=True)
            
            link_zap = f"https://wa.me/5585998351874?text=Olá Adriano! Gostaria de mais informações sobre: {row['nome']}"
            st.link_button("PEDIR PELO WHATSAPP", link_zap)
else:
    st.info("A vitrine está sendo preparada. Volte em breve!")
