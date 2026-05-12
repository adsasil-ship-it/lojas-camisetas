import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

# 1. CONFIGURAÇÃO E DESIGN
st.set_page_config(page_title="Adriano Designer | Loja", layout="wide")

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

    .card-produto { 
        background: white; border: 1px solid #eee; padding: 10px; border-radius: 12px; 
        text-align: center; height: 100%; position: relative; display: flex; flex-direction: column;
    }

    /* SELOS */
    .badge-promo { background: #A020F0; color: white; font-size: 9px; padding: 3px 7px; border-radius: 4px; position: absolute; top: 8px; right: 8px; z-index: 10; font-weight: bold; }
    .badge-lancamento { background: #25D366; color: white; font-size: 9px; padding: 3px 7px; border-radius: 4px; position: absolute; top: 8px; left: 8px; z-index: 10; font-weight: bold; }
    .badge-novidade { background: #007BFF; color: white; font-size: 9px; padding: 3px 7px; border-radius: 4px; position: absolute; top: 35px; left: 8px; z-index: 10; font-weight: bold; }
    
    .views-counter { font-size: 9px; color: #999; margin-top: 8px; display: block; }
    .preco-antigo { text-decoration: line-through; color: #888; font-size: 11px; }
    .preco-venda { color: #1a1c23; font-weight: 800; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÕES DE DADOS
def carregar_dados():
    caminho = "produtos.csv"
    if os.path.exists(caminho):
        try:
            df = pd.read_csv(caminho)
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
        st.info("Cadastre produtos no Painel Admin.")
    else:
        # Identificação para os selos
        lista_lancamentos = df.tail(6)["id"].tolist() 
        lista_novidades = df.head(3)["id"].tolist()   

        # REGRA DE OURO: Ordenar para que os lançamentos fiquem no topo
        # Criamos uma coluna auxiliar 'ordem_topo' onde Lançamentos = 0 e outros = 1
        df['ordem_topo'] = df['id'].apply(lambda x: 0 if x in lista_lancamentos else 1)
        df_ordenado = df.sort_values(by=['ordem_topo', 'id'], ascending=[True, False])

        cat_sel = st.selectbox("Filtrar Categoria", ["Todos"] + sorted(df["categoria"].unique().astype(str).tolist()))
        df_v = df_ordenado if cat_sel == "Todos" else df_ordenado[df_ordenado["categoria"] == cat_sel]
        
        st.divider()
        cols = st.columns(2)
        for i, (idx, row) in enumerate(df_v.iterrows()):
            # Atualiza visualizações no DF original usando o index
            df.at[idx, "visualizacoes"] = int(row.get("visualizacoes", 0)) + 1
            
            with cols[i % 2]:
                st.markdown('<div class="card-produto">', unsafe_allow_html=True)
                
                if row['id'] in lista_lancamentos:
                    st.markdown('<div class="badge-lancamento">LANÇAMENTO</div>', unsafe_allow_html=True)
                if row['id'] in lista_novidades:
                    st.markdown('<div class="badge-novidade">NOVIDADE</div>', unsafe_allow_html=True)
                if row.get('promocao'): 
                    st.markdown('<div class="badge-promo">15% OFF</div>', unsafe_allow_html=True)
                
                if os.path.exists(f"images/{row['images']}"): # Corrigido para 'images' conforme o CSV
                    st.image(f"images/{row['images']}", use_container_width=True)
                elif os.path.exists(f"images/{row.get('imagens')}"):
                    st.image(f"images/{row['imagens']}", use_container_width=True)
                
                st.markdown(f"**{row['nome']}**")
                
                if row.get('promocao'):
                    v_desc = float(row['preco_venda']) * 0.85
                    st.markdown(f'<span class="preco-antigo">R$ {float(row["preco_venda"]):.2f}</span>', unsafe_allow_html=True)
                    st.markdown(f'<span class="preco-venda">R$ {v_desc:.2f}</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="preco-venda">R$ {float(row["preco_venda"]):.2f}</span>', unsafe_allow_html=True)
                
                with st.expander("Ver Detalhes"): st.write(row['descricao'])
                
                st.link_button("PEDIR", f"https://wa.me/5585998351874?text=Interesse: {row['nome']}")
                st.markdown(f'<span class="views-counter">👁️ {int(df.at[idx, "visualizacoes"])}</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Remove a coluna temporária antes de salvar
        df_save = df.drop(columns=['ordem_topo'])
        df_save.to_csv("produtos.csv", index=False)

# --- ADMIN (Mantido igual) ---
else:
    senha = st.sidebar.text_input("Senha", type="password")
    if senha == "suasenha123":
        t1, t2, t3, t4 = st.tabs(["➕ Cadastro", "📝 Editar", "🗑️ Remover", "💾 Backup"])
        
        with t1:
            with st.form("add", clear_on_submit=True):
                n = st.text_input("Nome")
                d = st.text_area("Descrição")
                col1, col2 = st.columns(2)
                pv = col1.number_input("Venda", min_value=0.0)
                pc = col2.number_input("Custo", min_value=0.0)
                ct = st.text_input("Categoria")
                im = st.file_uploader("Imagem")
                pr = st.checkbox("Promoção")
                if st.form_submit_button("SALVAR"):
                    if n and im:
                        fn = f"{int(datetime.now().timestamp())}_{im.name}"
                        with open(f"images/{fn}", "wb") as f: f.write(im.getbuffer())
                        novo = pd.DataFrame([{"id": int(datetime.now().timestamp()), "nome": n, "preco_venda": pv, "preco_custo": pc, "imagens": fn, "categoria": ct, "descricao": d, "visualizacoes": 0, "promocao": pr}])
                        df = pd.concat([df, novo], ignore_index=True)
                        df.to_csv("produtos.csv", index=False)
                        st.rerun()

        with t2:
            if not df.empty:
                sel = st.selectbox("Editar:", df["nome"].tolist())
                idx_e = df[df["nome"] == sel].index[0]
                with st.form("edit"):
                    en = st.text_input("Nome", value=df.at[idx_e, 'nome'])
                    ev = st.number_input("Preço", value=float(df.at[idx_e, 'preco_venda']))
                    ep = st.checkbox("Promoção", value=bool(df.at[idx_e, 'promocao']))
                    if st.form_submit_button("ATUALIZAR"):
                        df.at[idx_e, 'nome'], df.at[idx_e, 'preco_venda'], df.at[idx_e, 'promocao'] = en, ev, ep
                        df.to_csv("produtos.csv", index=False)
                        st.rerun()

        with t3:
            for i, row in df.iterrows():
                c1, c2 = st.columns([4,1])
                c1.write(row['nome'])
                if c2.button("Apagar", key=f"d_{row['id']}"):
                    df = df.drop(i)
                    df.to_csv("produtos.csv", index=False)
                    st.rerun()

        with t4:
            st.download_button("Download CSV", df.to_csv(index=False).encode('utf-8'), "loja.csv")
            up = st.file_uploader("Restaurar", type="csv")
            if up and st.button("Confirmar"):
                pd.read_csv(up).to_csv("produtos.csv", index=False)
                st.rerun()
