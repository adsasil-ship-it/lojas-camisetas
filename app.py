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
    
    .header-container {
        display: flex; align-items: center; justify-content: center;
        gap: 15px; padding: 15px 0; width: 100%;
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

    /* GRID 2 COLUNAS MOBILE */
    [data-testid="stHorizontalBlock"] { display: flex; flex-wrap: wrap; gap: 8px; }
    @media (max-width: 640px) {
        [data-testid="stHorizontalBlock"] > div {
            width: calc(50% - 8px) !important;
            flex: 1 1 calc(50% - 8px) !important;
            min-width: calc(50% - 8px) !important;
        }
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
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÕES DE DADOS COM TRATAMENTO DE ERRO
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
        except:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

# Inicialização de pastas
if not os.path.exists("images"): os.makedirs("images")
df = carregar_dados()

# --- CABEÇALHO ---
logo_tag = ""
if os.path.exists("logo.png"):
    with open("logo.png", "rb") as f:
        logo_tag = f'<img src="data:image/png;base64,{base64.b64encode(f.read()).decode()}" class="logo-img">'

st.markdown(f'<div class="header-container">{logo_tag}<div class="text-box"><p class="loja-online-do">LOJA ONLINE DO:</p><h1 class="titulo-principal">ADRIANO <span class="destaque-verde">DESIGNER</span></h1></div></div>', unsafe_allow_html=True)

menu = st.sidebar.radio("Navegar", ["🛍️ Vitrine", "⚙️ Painel Admin"])

# --- VITRINE ---
if menu == "🛍️ Vitrine":
    if df.empty:
        st.info("Aguardando cadastro de produtos...")
    else:
        ids_novos = df.tail(3)["id"].tolist()
        c1, c2 = st.columns(2)
        cat_filtro = c1.selectbox("Categoria", ["Todos"] + sorted(df["categoria"].unique().astype(str).tolist()))
        df_f = df if cat_filtro == "Todos" else df[df["categoria"] == cat_filtro]
        
        cols = st.columns(2)
        for i, (idx, row) in enumerate(df_f.iterrows()):
            df.at[idx, "visualizacoes"] += 1
            with cols[i % 2]:
                st.markdown('<div class="card-produto">', unsafe_allow_html=True)
                if row['id'] in ids_novos: st.markdown('<div class="badge-lancamento">NOVO</div>', unsafe_allow_html=True)
                if row['promocao']: st.markdown('<div class="badge-promocao">15% OFF</div>', unsafe_allow_html=True)
                
                if os.path.exists(f"images/{row['imagens']}"):
                    st.image(f"images/{row['imagens']}", use_container_width=True)
                
                st.markdown(f"**{row['nome']}**")
                
                if row['promocao']:
                    vd = float(row['preco_venda']) * 0.85
                    st.markdown(f'<span class="preco-antigo">R$ {float(row["preco_venda"]):.2f}</span><br><b style="color:#A020F0; font-size:16px">R$ {vd:.2f}</b>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<p class="preco-novo">R$ {float(row["preco_venda"]):.2f}</p>', unsafe_allow_html=True)
                
                with st.expander("Detalhes"): st.write(row['descricao'])
                st.link_button("PEDIR", f"https://wa.me/5585998351874?text=Interesse no {row['nome']}")
                st.markdown('</div>', unsafe_allow_html=True)
        df.to_csv("produtos.csv", index=False)

# --- ADMIN ---
else:
    senha = st.text_input("Senha", type="password")
    if senha == "suasenha123":
        t1, t2, t3, t4 = st.tabs(["➕ Cadastro", "📝 Editar", "🗑️ Remover", "💾 Backup"])
        
        with t1:
            with st.form("cad", clear_on_submit=True):
                n = st.text_input("Nome")
                d = st.text_area("Descrição")
                v_v = st.number_input("Venda", min_value=0.0)
                v_c = st.number_input("Custo", min_value=0.0)
                ct = st.text_input("Categoria")
                sb = st.text_input("Subcategoria")
                im = st.file_uploader("Imagem", type=['jpg','png','jpeg'])
                pr = st.checkbox("Promoção Ativa")
                if st.form_submit_button("CADASTRAR"):
                    if n and im:
                        fname = f"{datetime.now().timestamp()}_{im.name}"
                        with open(f"images/{fname}", "wb") as f: f.write(im.getbuffer())
                        # Criando o DataFrame de forma segura
                        novo_item = {
                            "id": int(datetime.now().timestamp()),
                            "nome": n, "preco_venda": v_v, "preco_custo": v_c,
                            "imagens": fname, "categoria": ct, "subcategoria": sb,
                            "descricao": d, "visualizacoes": 0, "promocao": pr
                        }
                        df = pd.concat([df, pd.DataFrame([novo_item])], ignore_index=True)
                        df.to_csv("produtos.csv", index=False)
                        st.success("Salvo!")
                        st.rerun()

        with t2:
            if not df.empty:
                escolha = st.selectbox("Escolher para editar", df["nome"].tolist())
                idx_e = df[df["nome"] == escolha].index[0]
                with st.form("edit"):
                    en = st.text_input("Nome", value=df.at[idx_e, 'nome'])
                    ev = st.number_input("Venda", value=float(df.at[idx_e, 'preco_venda']))
                    ep = st.checkbox("Promoção", value=bool(df.at[idx_e, 'promocao']))
                    if st.form_submit_button("SALVAR"):
                        df.at[idx_e, 'nome'] = en
                        df.at[idx_e, 'preco_venda'] = ev
                        df.at[idx_e, 'promocao'] = ep
                        df.to_csv("produtos.csv", index=False)
                        st.rerun()

        with t3: # REMOVER
            for i, row in df.iterrows():
                c1, c2 = st.columns([4,1])
                c1.write(row['nome'])
                if c2.button("❌", key=f"d_{row['id']}"):
                    df = df.drop(i)
                    df.to_csv("produtos.csv", index=False)
                    st.rerun()

        with t4: # BACKUP
            st.download_button("BAIXAR CSV", df.to_csv(index=False).encode('utf-8'), "backup.csv")
            rest = st.file_uploader("RESTAURAR CSV", type="csv")
            if rest and st.button("Confirmar"):
                pd.read_csv(rest).to_csv("produtos.csv", index=False)
                st.rerun()
