import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO DE DESIGN
st.set_page_config(page_title="Adriano Designer | Studio", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;800&display=swap');
    
    /* FUNDO DA PÁGINA */
    .stApp { background-color: #f4f4f6; }

    /* CABEÇALHO MODERNO */
    .header-container {
        text-align: left;
        margin-bottom: 30px;
    }
    .subtitulo-loja {
        font-family: 'Inter', sans-serif;
        font-weight: 300;
        font-size: 14px;
        letter-spacing: 4px;
        color: #7a7a7a;
        text-transform: uppercase;
        margin-bottom: -10px;
        display: block;
    }
    .titulo-principal {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 42px;
        color: #1a1c23;
        line-height: 1;
    }
    .destaque-verde {
        color: #25D366;
    }

    /* CARD DO PRODUTO */
    div[data-testid="column"] {
        background-color: #ffffff;
        border: 1px solid #eef0f2;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.03);
        transition: 0.3s;
    }

    /* NOMES DO PRODUTO (CINZA ESCURO) */
    .nome-produto {
        color: #1a1c23 !important; 
        font-size: 20px !important;
        font-weight: 700 !important;
        margin-top: 15px !important;
        display: block;
    }

    .categoria-texto {
        color: #888 !important;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .badge-destaque {
        background: #25D366;
        color: white !important;
        padding: 5px 15px;
        border-radius: 50px;
        font-weight: bold;
        font-size: 10px;
        margin-bottom: 15px;
        display: inline-block;
    }
    
    /* Estilo do Preço */
    .preco-estilo {
        color: #1a1c23 !important;
        font-weight: 800;
        font-size: 26px;
        margin: 10px 0;
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

# --- CABEÇALHO MODERNO ---
col_logo, col_vazio, col_texto = st.columns([1, 0.1, 5])
with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=110)

with col_texto:
    st.markdown(f"""
        <div class="header-container">
            <span class="subtitulo-loja">Loja Virtual</span>
            <h1 class="titulo-principal">ADRIANO <span class="destaque-verde">DESIGNER</span></h1>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border: 0.5px solid #e0e0e0;'>", unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
pagina = st.sidebar.radio("Navegação", ["🛍️ Vitrine", "⚙️ Painel Admin"])

if pagina == "🛍️ Vitrine":
    df = carregar_dados()
    if not df.empty:
        # Menu de categorias visível e moderno
        categorias = ["Todos"] + sorted(df["categoria"].unique().astype(str).tolist())
        escolha_cat = st.segmented_control("Explorar Categorias", categorias, default="Todos")
        
        df_view = df if escolha_cat == "Todos" else df[df["categoria"] == escolha_cat]
        df_view = df_view.iloc[::-1] # Recentes primeiro

        st.write("") # Espaçamento

        cols = st.columns(3)
        for i, (idx, row) in enumerate(df_view.iterrows()):
            with cols[i % 3]:
                # Etiqueta de Lançamento (Destaque)
                if idx in df.index[-3:]:
                    st.markdown('<div class="badge-destaque">NOVIDADE</div>', unsafe_allow_html=True)
                
                # Imagem
                fotos = str(row['imagens']).split(",")
                if os.path.exists(f"images/{fotos[0]}"):
                    st.image(f"images/{fotos[0]}", use_container_width=True)
                
                # Textos
                st.markdown(f'<span class="nome-produto">{row["nome"]}</span>', unsafe_allow_html=True)
                st.markdown(f'<span class="categoria-texto">{row["categoria"]} | {row["subcategoria"]}</span>', unsafe_allow_html=True)
                
                preco_formatado = f"R$ {row['preco']:.2f}" if row['preco'] > 0 else "Sob Consulta"
                st.markdown(f'<p class="preco-estilo">{preco_formatado}</p>', unsafe_allow_html=True)
                
                link_zap = f"https://wa.me/5585998351874?text=Olá Adriano! Gostaria de detalhes do produto: {row['nome']}"
                st.link_button("ADQUIRIR AGORA", link_zap)
    else:
        st.info("Nenhum produto cadastrado.")

# --- PAINEL ADMIN (Mantido para funcionamento) ---
elif pagina == "⚙️ Painel Admin":
    senha = st.sidebar.text_input("Senha", type="password")
    if senha == "suasenha123":
        tab1, tab2, tab3 = st.tabs(["➕ Adicionar", "📝 Editar", "🗑️ Excluir"])
        df = carregar_dados()
        # ... (Restante do código de administração igual ao anterior)
