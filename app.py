import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

# 1. CONFIGURAÇÃO E DESIGN
st.set_page_config(page_title="Adriano Designer | Loja Oficial", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;700;800&display=swap');
    
    /* CABEÇALHO FLEXBOX PARA MOBILE */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        padding: 15px 0;
        width: 100%;
        text-align: left;
    }
    
    .logo-img { width: 65px; height: auto; border-radius: 8px; }

    .text-box { display: flex; flex-direction: column; }

    .loja-online-do { 
        font-family: 'Inter', sans-serif; font-size: 10px; letter-spacing: 2px; 
        color: #888; margin-bottom: -5px; font-weight: 700; text-transform: uppercase; 
    }

    .titulo-principal { 
        font-family: 'Bebas Neue', sans-serif; font-size: clamp(30px, 8vw, 50px); 
        color: #1a1c23; line-height: 0.9; margin: 0; 
    }

    .destaque-verde { color: #25D366; }

    /* GRID 2 COLUNAS NO CELULAR */
    [data-testid="stHorizontalBlock"] { display: flex; flex-wrap: wrap; gap: 8px; }
    
    @media (max-width: 640px) {
        [data-testid="stHorizontalBlock"] > div {
            width: calc(50% - 8px) !important;
            flex: 1 1 calc(50% - 8px) !important;
            min-width: calc(50% - 8px) !important;
        }
        .header-container { gap: 10px; }
    }

    .stApp { background-color: #f8f9fa; }
    .card-produto { 
        background-color: #ffffff; border: 1px solid #e9ecef; padding: 8px; 
        border-radius: 12px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05); 
        position: relative; height: 100%; display: flex; flex-direction: column;
    }
    
    .badge-lancamento { background-color: #25D366; color: white; padding: 2px 6px; border-radius: 4px; font-size: 8px; font-weight: bold; position: absolute; top: 5px; left: 5px; z-index: 10; }
    .badge-promocao { background-color: #A020F0; color: white; padding: 2px 6px; border-radius: 4px; font-size: 8px; font-weight: bold; position: absolute; top: 5px; right: 5px; z-index: 10; }
    
    .preco-antigo { text-decoration: line-through; color: #888; font-size: 10px; }
    .preco-novo { font-size: 15px; font-weight: 800; color: #1a1c23; margin: 2px 0; }
    .views-badge { font-size: 8px; color: #999; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÕES DE DADOS
def carregar_dados():
    caminho = "produtos.csv"
    cols = ["id", "nome", "preco_venda", "preco_custo", "imagens", "categoria", "subcategoria", "descricao", "visualizacoes", "promocao"]
    if os.path.exists(caminho):
        df = pd.read_csv(caminho)
        for col in cols:
            if col not in df.columns:
                df[col] = 0.0 if "preco" in col or "visualizacoes" in col else (False if col == "promocao" else "")
        return df
    return pd.DataFrame(columns=cols)

if not os.path.exists("images"): os.makedirs("images")
df = carregar_dados()

# --- CABEÇALHO DINÂMICO ---
logo_tag = ""
if os.path.exists("logo.png"):
    with open("logo.png", "rb") as f:
        data = base64.b64encode(f.read()).decode()
    logo_tag = f'<img src="data:image/png;base64,{data}" class="logo-img">'

st.markdown(f"""
    <div class="header-container">
        {logo_tag}
        <div class="text-box">
            <p class="loja-online-do">LOJA ONLINE DO:</p>
            <h1 class="titulo-principal">ADRIANO <span class="destaque-verde">DESIGNER</span></h1>
        </div>
    </div>
    """, unsafe_allow_html=True)

menu = st.sidebar.radio("Menu", ["🛍️ Vitrine", "⚙️ Painel Admin"])

# --- VITRINE ---
if menu == "🛍️ Vitrine":
    ids_lancamento = df.tail(3)["id"].tolist() if not df.empty else []
    
    c1, c2 = st.columns(2)
    cat_sel = c1.selectbox("Filtrar Categoria", ["Todos"] + sorted(df["categoria"].unique().astype(str).tolist()))
    df_f = df if cat_sel == "Todos" else df[df["categoria"] == cat_sel]
    sub_sel = c2.selectbox("Subcategoria", ["Todas"] + sorted(df_f["subcategoria"].unique().astype(str).tolist()))
    
    df_vitrine = df_f if sub_sel == "Todas" else df_f[df_f["subcategoria"] == sub_sel]
    
    st.divider()
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
                    st.markdown(f'<span class="preco-antigo">R$ {float(row["preco_venda"]):.2f}</span> <b style="color:#A020F0">R$ {v_desc:.2f}</b>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<p class="preco-novo">R$ {float(row["preco_venda"]):.2f}</p>', unsafe_allow_html=True)
                
                with st.expander("Detalhes"):
                    st.write(row['descricao'])
                
                st.link_button("PEDIR", f"https://wa.me/5585998351874?text=Interesse: {row['nome']}")
                st.markdown(f'<span class="views-badge">👁️ {int(row["visualizacoes"])}</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        df.to_csv("produtos.csv", index=False)

# --- PAINEL ADMIN (RESTAURADO) ---
else:
    senha = st.text_input("Senha Admin", type="password")
    if senha == "suasenha123":
        tab1, tab2, tab3, tab4 = st.tabs(["➕ Cadastro", "📝 Editar", "🗑️ Remover", "💾 Backup"])
        
        with tab1:
            with st.form("form_cad", clear_on_submit=True):
                n = st.text_input("Nome do Produto")
                d = st.text_area("Descrição Completa")
                col_a, col_b = st.columns(2)
                pv = col_a.number_input("Preço de Venda")
                pc = col_b.number_input("Preço de Custo")
                cat = st.text_input("Categoria")
                sub = st.text_input("Subcategoria")
                img = st.file_uploader("Foto do Produto")
                promo = st.checkbox("Ativar Promoção (15% desconto automático)")
                if st.form_submit_button("FINALIZAR CADASTRO"):
                    if n and img:
                        n_img = f"{datetime.now().timestamp()}_{img.name}"
                        with open(f"images/{n_img}", "wb") as f: f.write(img.getbuffer())
                        novo = pd.DataFrame([{"id": int(datetime.now().timestamp()), "nome": n, "preco_venda": pv, "preco_custo": pc, "imagens": n_img, "categoria": cat, "subcategoria": sub, "descricao": d, "visualizacoes": 0, "promocao": promo}])
                        df = pd.concat([df, novo], ignore_index=True)
                        df.to_csv("produtos.csv", index=False)
                        st.success("Produto salvo!")
                        st.rerun()

        with tab2:
            if not df.empty:
                sel = st.selectbox("Escolha o produto para editar:", df["nome"].tolist())
                idx_e = df[df["nome"] == sel].index[0]
                with st.form("form_edit"):
                    en = st.text_input("Nome", value=df.at[idx_e, 'nome'])
                    ed = st.text_area("Descrição", value=df.at[idx_e, 'descricao'])
                    ev = st.number_input("Preço Venda", value=float(df.at[idx_e, 'preco_venda']))
                    ec = st.number_input("Preço Custo", value=float(df.at[idx_e, 'preco_custo']))
                    ep = st.checkbox("Promoção", value=bool(df.at[idx_e, 'promocao']))
                    if st.form_submit_button("SALVAR ALTERAÇÕES"):
                        df.loc[idx_e, ['nome', 'descricao', 'preco_venda', 'preco_custo', 'promocao']] = [en, ed, ev, ec, ep]
                        df.to_csv("produtos.csv", index=False)
                        st.success("Alterado!")
                        st.rerun()

        with tab3:
            for i, row in df.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{row['nome']}** ({row['categoria']})")
                if c2.button("❌", key=f"del_{row['id']}"):
                    df = df.drop(i)
                    df.to_csv("produtos.csv", index=False)
                    st.rerun()

        with tab4:
            st.download_button("BAIXAR PLANILHA (BACKUP)", df.to_csv(index=False).encode('utf-8'), "produtos.csv")
            arq = st.file_uploader("RESTAURAR PLANILHA", type="csv")
            if arq and st.button("Confirmar Restauração"):
                pd.read_csv(arq).to_csv("produtos.csv", index=False)
                st.rerun()
