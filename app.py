import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO E DESIGN
st.set_page_config(page_title="Adriano Designer | Loja Oficial", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;700;800&display=swap');
    
    /* --- AJUSTE DO CABEÇALHO (MOBILE & DESKTOP) --- */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        padding: 10px 0;
        margin-bottom: 20px;
        width: 100%;
    }
    
    .logo-img {
        width: 70px;
        height: auto;
        border-radius: 10px;
    }

    .text-box { 
        display: flex; 
        flex-direction: column; 
        align-items: flex-start; 
        justify-content: center; 
    }

    .loja-online-do { 
        font-family: 'Inter', sans-serif; 
        font-size: 10px; 
        letter-spacing: 2px; 
        color: #888; 
        margin-bottom: -5px; 
        font-weight: 700; 
        text-transform: uppercase; 
    }

    .titulo-principal { 
        font-family: 'Bebas Neue', sans-serif; 
        font-size: clamp(35px, 8vw, 55px); /* Ajusta o tamanho da fonte conforme a tela */
        color: #1a1c23; 
        line-height: 0.9; 
        margin: 0; 
    }

    .destaque-verde { color: #25D366; }

    /* --- LAYOUT DOS PRODUTOS (2 COLUNAS NO CELULAR) --- */
    [data-testid="stHorizontalBlock"] {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }
    
    @media (max-width: 640px) {
        .header-container {
            gap: 10px;
        }
        [data-testid="stHorizontalBlock"] > div {
            width: calc(50% - 10px) !important;
            flex: 1 1 calc(50% - 10px) !important;
            min-width: calc(50% - 10px) !important;
        }
    }

    /* --- CARDS --- */
    .stApp { background-color: #f8f9fa; }
    .card-produto { 
        background-color: #ffffff; 
        border: 1px solid #e9ecef; 
        padding: 8px; 
        border-radius: 12px; 
        text-align: center; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); 
        position: relative; 
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    
    .badge-lancamento { background-color: #25D366; color: white; padding: 2px 6px; border-radius: 4px; font-size: 8px; font-weight: bold; position: absolute; top: 5px; left: 5px; z-index: 10; }
    .badge-promocao { background-color: #A020F0; color: white; padding: 2px 6px; border-radius: 4px; font-size: 8px; font-weight: bold; position: absolute; top: 5px; right: 5px; z-index: 10; }
    
    .preco-antigo { text-decoration: line-through; color: #888; font-size: 10px; }
    .preco-novo { font-size: 15px; font-weight: 800; color: #1a1c23; margin: 2px 0; }
    .views-badge { font-size: 8px; color: #999; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÕES DE DADOS (Mantidas)
def carregar_dados():
    caminho = "produtos.csv"
    cols = ["id", "nome", "preco_venda", "preco_custo", "imagens", "categoria", "subcategoria", "descricao", "visualizacoes", "promocao"]
    if os.path.exists(caminho):
        try:
            df = pd.read_csv(caminho)
            for col in cols:
                if col not in df.columns:
                    df[col] = 0.0 if "preco" in col or "visualizacoes" in col else (False if col == "promocao" else "")
            return df
        except: pass
    return pd.DataFrame(columns=cols)

if not os.path.exists("images"): os.makedirs("images")
df = carregar_dados()

# --- NOVO CABEÇALHO BALANCEADO ---
# Usamos HTML direto para garantir que o Flexbox funcione melhor que as colunas do Streamlit no mobile
logo_html = f'<img src="data:image/png;base64,..." class="logo-img">' # Placeholder lógica imagem
# Para simplificar e garantir funcionamento, usamos o caminho se existir:
if os.path.exists("logo.png"):
    import base64
    with open("logo.png", "rb") as f:
        data = base64.b64encode(f.read()).decode()
    logo_tag = f'<img src="data:image/png;base64,{data}" class="logo-img">'
else:
    logo_tag = ''

st.markdown(f"""
    <div class="header-container">
        {logo_tag}
        <div class="text-box">
            <p class="loja-online-do">LOJA ONLINE DO:</p>
            <h1 class="titulo-principal">ADRIANO <span class="destaque-verde">DESIGNER</span></h1>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
menu_principal = st.sidebar.radio("Navegar", ["🛍️ Vitrine", "⚙️ Painel Admin"])

# --- VITRINE ---
if menu_principal == "🛍️ Vitrine":
    ids_lancamento = df.tail(3)["id"].tolist() if not df.empty else []
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        cat_sel = st.selectbox("CATEGORIA", ["Todos"] + sorted(df["categoria"].unique().astype(str).tolist()))
    with c2:
        df_f = df if cat_sel == "Todos" else df[df["categoria"] == cat_sel]
        sub_sel = st.selectbox("SUBCATEGORIA", ["Todas"] + sorted(df_f["subcategoria"].unique().astype(str).tolist()))
    
    df_vitrine = df_f if sub_sel == "Todas" else df_f[df_f["subcategoria"] == sub_sel]
    
    if df_vitrine.empty:
        st.info("Nenhum produto encontrado.")
    else:
        cols = st.columns(2)
        for i, (idx, row) in enumerate(df_vitrine.iterrows()):
            df.at[idx, "visualizacoes"] += 1
            with cols[i % 2]:
                st.markdown('<div class="card-produto">', unsafe_allow_html=True)
                if row['id'] in ids_lancamento: st.markdown('<div class="badge-lancamento">NOVO</div>', unsafe_allow_html=True)
                if row['promocao']: st.markdown('<div class="badge-promocao">15% OFF</div>', unsafe_allow_html=True)

                if os.path.exists(f"images/{row['imagens']}"):
                    st.image(f"images/{row['imagens']}", use_container_width=True)
                
                st.markdown(f"**{row['nome']}**")
                
                if row['promocao']:
                    v_desc = float(row['preco_venda']) * 0.85
                    st.markdown(f'<span class="preco-antigo">R$ {float(row["preco_venda"]):.2f}</span>', unsafe_allow_html=True)
                    st.markdown(f'<p class="preco-novo">R$ {v_desc:.2f}</p>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<p class="preco-novo">R$ {float(row["preco_venda"]):.2f}</p>', unsafe_allow_html=True)
                
                with st.expander("Detalhes"):
                    st.write(row['descricao'])
                
                st.link_button("PEDIR", f"https://wa.me/5585998351874?text=Tenho interesse em: {row['nome']}")
                st.markdown(f'<span class="views-badge">👁️ {int(row["visualizacoes"])}</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        df.to_csv("produtos.csv", index=False)

# --- ADMIN (Mantido igual para não perder funcionalidades) ---
else:
    senha = st.text_input("Senha Admin", type="password")
    if senha == "suasenha123":
        t1, t2, t3, t4 = st.tabs(["➕ Cadastro", "📝 Editar", "🗑️ Remover", "💾 Backup"])
        # ... (restante do código admin anterior permanece o mesmo)
