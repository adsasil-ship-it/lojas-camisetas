import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Adriano Designer | Studio", layout="wide")

# CSS AJUSTADO
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    /* Fundo Geral */
    .stApp {
        background-color: #0e1117;
    }

    /* Card do Produto */
    div[data-testid="column"] {
        background-color: #1a1c23;
        border: 1px solid #333;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        text-align: center;
    }

    /* COR DO NOME DO PRODUTO - CINZA ESCURO / GRAFITE CLARO */
    /* Usei um cinza visível no fundo escuro (#a0a0a0) */
    .nome-produto {
        color: #a0a0a0 !important; 
        font-size: 22px !important;
        font-weight: 700 !important;
        margin-top: 15px !important;
        margin-bottom: 5px !important;
        display: block;
    }

    .categoria-texto {
        color: #666666 !important;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .badge-destaque {
        background: linear-gradient(90deg, #25D366, #128C7E);
        color: white !important;
        padding: 4px 12px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 11px;
        margin-bottom: 10px;
        display: inline-block;
    }
    
    /* Botão WhatsApp */
    .stButton>button {
        background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
        color: white;
        border: none;
    }
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
    st.markdown("<h1 style='color:white; margin-bottom:0;'>ADRIANO <span style='color:#25D366;'>DESIGNER</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#666;'>Estúdio de Criação & Personalizados Premium</p>", unsafe_allow_html=True)

st.markdown("---")

# --- VITRINE ---
df = carregar_dados()

if not df.empty:
    # Menu de categorias horizontal
    categorias = ["Todos"] + sorted(df["categoria"].unique().astype(str).tolist())
    escolha_cat = st.radio("Filtrar por:", categorias, horizontal=True)
    
    df_view = df if escolha_cat == "Todos" else df[df["categoria"] == escolha_cat]
    df_view = df_view.iloc[::-1] # Recentes primeiro

    cols = st.columns(3)
    for i, (idx, row) in enumerate(df_view.iterrows()):
        with cols[i % 3]:
            # Selo de Destaque
            if idx in df.index[-3:]:
                st.markdown('<div class="badge-destaque">✨ NOVIDADE</div>', unsafe_allow_html=True)
            
            # Imagem
            fotos = str(row['imagens']).split(",")
            if os.path.exists(f"images/{fotos[0]}"):
                st.image(f"images/{fotos[0]}", use_container_width=True)
            
            # NOMES DO PRODUTO (Usando a classe CSS nova para garantir visibilidade)
            st.markdown(f'<span class="nome-produto">{row["nome"]}</span>', unsafe_allow_html=True)
            st.markdown(f'<span class="categoria-texto">{row["categoria"]} | {row["subcategoria"]}</span>', unsafe_allow_html=True)
            
            preco = f"R$ {row['preco']:.2f}" if row['preco'] > 0 else "CONSULTAR"
            st.markdown(f"<h2 style='color: #25D366;'>{preco}</h2>", unsafe_allow_html=True)
            
            st.link_button("SOLICITAR NO WHATSAPP", f"https://wa.me/5585998351874?text=Tenho interesse no {row['nome']}")
else:
    st.info("Cadastre produtos no Painel Admin para eles aparecerem aqui.")
