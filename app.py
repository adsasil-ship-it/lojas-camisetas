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
    
    .header-container { text-align: center; margin-bottom: 5px; }
    
    .logo-img {
        margin-bottom: 10px;
    }
    
    .loja-online-do {
        font-family: 'Inter', sans-serif;
        font-size: 12px;
        letter-spacing: 3px;
        color: #888;
        margin-bottom: -15px;
        font-weight: 700;
    }
    
    .titulo-principal { 
        font-family: 'Bebas Neue', sans-serif; 
        font-size: 75px; 
        color: #1a1c23; 
        line-height: 1;
        margin-top: 0;
    }
    
    .destaque-verde { color: #25D366; }
    
    .search-label {
        font-family: 'Inter', sans-serif;
        font-size: 16px;
        font-weight: 800;
        color: #1a1c23;
        text-align: center;
        margin-top: 15px;
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

# --- CABEÇALHO COM LOGO ---
st.markdown('<div class="header-container">', unsafe_allow_html=True)
col_l1, col_l2, col_l3 = st.columns([2, 1, 2])
with col_l2:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
st.markdown("""
        <p class="loja-online-do">LOJA ONLINE DO:</p>
        <h1 class="titulo-principal">ADRIANO <span class="destaque-verde">DESIGNER</span></h1>
    </div>
""", unsafe_allow_html=True)

# --- MENU DE ACESSIBILIDADE ---
st.markdown('<p class="search-label">PROCURE SEU ESTILO AQUI.</p>', unsafe_allow_html=True)

# Filtros centrais para o cliente
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

# --- NAVEGAÇÃO INTERNA ---
menu_principal = st.sidebar.radio("Navegar", ["🛍️ Vitrine", "⚙️ Painel Admin"])

# --- VITRINE ---
if menu_principal == "🛍️ Vitrine":
    if df.empty:
        st.info("Nenhum produto cadastrado.")
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
                st.link_button("VER NO WHATSAPP", f"https://wa.me/5585998351874?text=Olá Adriano! Vi este item: {row['nome']}")
                st.markdown('</div>', unsafe_allow_html=True)

# --- ADMIN ---
else:
    senha = st.text_input("Senha Admin", type="password")
    if senha == "suasenha123":
        t1, t2, t3, t4 = st.tabs(["➕ Novo Produto", "📝 Editar", "🗑️ Remover", "💾 Backup"])
        
        sugestoes_cat = sorted(df["categoria"].unique().astype(str).tolist()) if not df.empty else []
        sugestoes_sub = sorted(df["subcategoria"].unique().astype(str).tolist()) if not df.empty else []

        with t1:
            st.write("### Publicar Novo Item")
            with st.form("form_novo", clear_on_submit=True):
                nome = st.text_input("Nome do Produto")
                preco = st.number_input("Preço (R$)", min_value=0.0)
                
                col1, col2 = st.columns(2)
                with col1:
                    cat_op = st.selectbox("Categoria Existente", ["+ Adicionar Nova"] + sugestoes_cat)
                    cat_final = st.text_input("Digite a Nova Categoria") if cat_op == "+ Adicionar Nova" else cat_op
                
                with col2:
                    sub_op = st.selectbox("Subcategoria Existente", ["+ Adicionar Nova"] + sugestoes_sub)
                    sub_final = st.text_input("Digite a Nova Subcategoria") if sub_op == "+ Adicionar Nova" else sub_op
                
                desc = st.text_area("Descrição")
                foto = st.file_uploader("Imagem", type=['jpg', 'png', 'jpeg'])
                
                if st.form_submit_button("PUBLICAR"):
                    if nome and foto and cat_final:
                        nome_arq = f"{datetime.now().timestamp()}_{foto.name}".replace(" ","_")
                        with open(f"images/{nome_arq}", "wb") as f:
                            f.write(foto.getbuffer())
                        
                        novo = pd.DataFrame([{"nome": nome, "preco": preco, "imagens": nome_arq, 
                                             "categoria": cat_final, "subcategoria": sub_final, 
                                             "descricao": desc, "novidade": True}])
                        df = pd.concat([df, novo], ignore_index=True)
                        df.to_csv("produtos.csv", index=False)
                        st.success(f"'{nome}' cadastrado!")
                        st.rerun()

        with t2: # EDITAR
            if not df.empty:
                escolha = st.selectbox("Produto para editar", df["nome"].tolist())
                idx = df[df["nome"] == escolha].index[0]
                with st.form("form_edit"):
                    enome = st.text_input("Nome", value=df.at[idx, 'nome'])
                    epreco = st.number_input("Preço", value=float(df.at[idx, 'preco']))
                    ecat = st.text_input("Categoria", value=df.at[idx, 'categoria'])
                    esub = st.text_input("Subcategoria", value=df.at[idx, 'subcategoria'])
                    if st.form_submit_button("SALVAR"):
                        df.at[idx, 'nome'], df.at[idx, 'preco'] = enome, epreco
                        df.at[idx, 'categoria'], df.at[idx, 'subcategoria'] = ecat, esub
                        df.to_csv("produtos.csv", index=False)
                        st.rerun()

        with t3: # REMOVER
            for i, row in df.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.write(f"🗑️ **{row['nome']}** | {row['categoria']}")
                if c2.button("Excluir", key=f"del_{i}"):
                    df = df.drop(i)
                    df.to_csv("produtos.csv", index=False)
                    st.rerun()

        with t4: # BACKUP
            st.download_button("📥 BAIXAR PLANILHA", df.to_csv(index=False), "produtos.csv")
