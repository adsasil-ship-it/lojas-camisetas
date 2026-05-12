import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO E DESIGN
st.set_page_config(page_title="Adriano Designer | Loja Oficial", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;700;800&display=swap');
    
    /* Layout Responsivo para Celular */
    [data-testid="stHorizontalBlock"] {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }
    
    /* Força 2 colunas em telas pequenas (mobile) */
    @media (max-width: 640px) {
        [data-testid="stHorizontalBlock"] > div {
            width: calc(50% - 10px) !important;
            flex: 1 1 calc(50% - 10px) !important;
            min-width: calc(50% - 10px) !important;
        }
    }

    .stApp { background-color: #f8f9fa; }
    .text-box { display: flex; flex-direction: column; align-items: flex-start; justify-content: center; }
    .loja-online-do { font-family: 'Inter', sans-serif; font-size: 11px; letter-spacing: 2px; color: #888; margin-bottom: -10px; font-weight: 700; text-transform: uppercase; }
    .titulo-principal { font-family: 'Bebas Neue', sans-serif; font-size: 45px; color: #1a1c23; line-height: 1; margin: 0; }
    .destaque-verde { color: #25D366; }
    
    .card-produto { 
        background-color: #ffffff; 
        border: 1px solid #e9ecef; 
        padding: 10px; 
        border-radius: 12px; 
        text-align: center; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); 
        position: relative; 
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .badge-lancamento { background-color: #25D366; color: white; padding: 2px 6px; border-radius: 4px; font-size: 9px; font-weight: bold; position: absolute; top: 5px; left: 5px; z-index: 10; }
    .badge-promocao { background-color: #A020F0; color: white; padding: 2px 6px; border-radius: 4px; font-size: 9px; font-weight: bold; position: absolute; top: 5px; right: 5px; z-index: 10; }
    
    .preco-antigo { text-decoration: line-through; color: #888; font-size: 12px; }
    .preco-novo { font-size: 18px; font-weight: 800; color: #1a1c23; margin: 5px 0; }
    .views-badge { font-size: 9px; color: #999; margin-top: 5px; }
    
    /* Ajuste de fonte para botões no mobile */
    .stButton button { width: 100%; font-size: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÕES DE DADOS
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

# --- CABEÇALHO ---
col_logo, col_texto = st.columns([1, 3])
with col_logo:
    if os.path.exists("logo.png"): st.image("logo.png", width=70) 
with col_texto:
    st.markdown('<div class="text-box"><p class="loja-online-do">LOJA ONLINE DO:</p><h1 class="titulo-principal">ADRIANO <span class="destaque-verde">DESIGNER</span></h1></div>', unsafe_allow_html=True)

menu_principal = st.sidebar.radio("Navegar", ["🛍️ Vitrine", "⚙️ Painel Admin"])

# --- VITRINE ---
if menu_principal == "🛍️ Vitrine":
    ids_lancamento = df.tail(3)["id"].tolist() if not df.empty else []
    
    st.divider()
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
        # Grid de produtos
        cols = st.columns(2 if len(df_vitrine) > 1 else 1)
        for i, (idx, row) in enumerate(df_vitrine.iterrows()):
            df.at[idx, "visualizacoes"] += 1
            with cols[i % 2]:
                st.markdown('<div class="card-produto">', unsafe_allow_html=True)
                
                # Selos
                if row['id'] in ids_lancamento:
                    st.markdown('<div class="badge-lancamento">NOVO</div>', unsafe_allow_html=True)
                if row['promocao']:
                    st.markdown('<div class="badge-promocao">15% OFF</div>', unsafe_allow_html=True)

                if os.path.exists(f"images/{row['imagens']}"):
                    st.image(f"images/{row['imagens']}", use_container_width=True)
                
                st.markdown(f"**{row['nome']}**")
                
                # Preços
                if row['promocao']:
                    valor_desc = float(row['preco_venda']) * 0.85
                    st.markdown(f'<span class="preco-antigo">R$ {float(row["preco_venda"]):.2f}</span>', unsafe_allow_html=True)
                    st.markdown(f'<p class="preco-novo">R$ {valor_desc:.2f}</p>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<p class="preco-novo">R$ {float(row["preco_venda"]):.2f}</p>', unsafe_allow_html=True)
                
                # DESCRIÇÃO EXPANSÍVEL
                with st.expander("Ver detalhes"):
                    st.write(row['descricao'])
                
                st.link_button("PEDIR", f"https://wa.me/5585998351874?text=Quero saber mais sobre: {row['nome']}")
                st.markdown(f'<span class="views-badge">👁️ {int(row["visualizacoes"])}</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        df.to_csv("produtos.csv", index=False)

# --- ADMIN --- (Código anterior mantido com as correções de remoção e edição)
else:
    senha = st.text_input("Senha Admin", type="password")
    if senha == "suasenha123":
        t1, t2, t3 = st.tabs(["➕ Cadastro", "📝 Editar", "🗑️ Remover"])
        
        with t1: # Cadastro igual ao anterior com campo 'promocao'
            with st.form("f_novo", clear_on_submit=True):
                n = st.text_input("Nome")
                d = st.text_area("Descrição")
                pv = st.number_input("Venda")
                pc = st.number_input("Custo")
                c = st.text_input("Categoria")
                s = st.text_input("Subcategoria")
                img = st.file_uploader("Imagem")
                promo = st.checkbox("Ativar Promoção")
                if st.form_submit_button("Cadastrar"):
                    if n and img:
                        nome_img = f"{datetime.now().timestamp()}_{img.name}"
                        with open(f"images/{nome_img}", "wb") as f: f.write(img.getbuffer())
                        novo = pd.DataFrame([{"id": int(datetime.now().timestamp()), "nome": n, "preco_venda": pv, "preco_custo": pc, "imagens": nome_img, "categoria": c, "subcategoria": s, "descricao": d, "visualizacoes": 0, "promocao": promo}])
                        df = pd.concat([df, novo], ignore_index=True)
                        df.to_csv("produtos.csv", index=False)
                        st.rerun()

        with t2: # Editar completo
            if not df.empty:
                sel = st.selectbox("Editar:", df["nome"].tolist())
                idx = df[df["nome"] == sel].index[0]
                with st.form("f_edit"):
                    en = st.text_input("Nome", value=df.at[idx, 'nome'])
                    ed = st.text_area("Descrição", value=df.at[idx, 'descricao'])
                    ev = st.number_input("Preço", value=float(df.at[idx, 'preco_venda']))
                    ep = st.checkbox("Promoção", value=bool(df.at[idx, 'promocao']))
                    if st.form_submit_button("Atualizar"):
                        df.at[idx, 'nome'], df.at[idx, 'descricao'], df.at[idx, 'preco_venda'], df.at[idx, 'promocao'] = en, ed, ev, ep
                        df.to_csv("produtos.csv", index=False)
                        st.rerun()

        with t3: # Remover
            for i, row in df.iterrows():
                c1, c2 = st.columns([3, 1])
                c1.write(row['nome'])
                if c2.button("❌", key=f"del_{row['id']}"):
                    df = df.drop(i)
                    df.to_csv("produtos.csv", index=False)
                    st.rerun()
