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
    
    /* Grid 2 colunas no Mobile */
    [data-testid="stHorizontalBlock"] { display: flex; flex-wrap: wrap; gap: 8px; }
    @media (max-width: 640px) {
        [data-testid="stHorizontalBlock"] > div { width: calc(50% - 8px) !important; flex: 1 1 calc(50% - 8px) !important; min-width: calc(50% - 8px) !important; }
    }
    .card-produto { background: white; border: 1px solid #eee; padding: 10px; border-radius: 12px; text-align: center; height: 100%; position: relative; }
    .badge-promo { background: #A020F0; color: white; font-size: 10px; padding: 2px 8px; border-radius: 5px; position: absolute; top: 5px; right: 5px; }
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
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

if not os.path.exists("images"): os.makedirs("images")
df = carregar_dados()

# --- CABEÇALHO ---
logo_tag = ""
if os.path.exists("logo.png"):
    with open("logo.png", "rb") as f:
        data = base64.b64encode(f.read()).decode()
    logo_tag = f'<img src="data:image/png;base64,{data}" class="logo-img">'

st.markdown(f'<div class="header-container">{logo_tag}<div><p class="loja-online-do">LOJA ONLINE DO:</p><h1 class="titulo-principal">ADRIANO <span class="destaque-verde">DESIGNER</span></h1></div></div>', unsafe_allow_html=True)

menu = st.sidebar.radio("Navegar", ["🛍️ Vitrine", "⚙️ Painel Admin"])

# --- VITRINE ---
if menu == "🛍️ Vitrine":
    if df.empty:
        st.info("Nenhum produto cadastrado.")
    else:
        # Filtros básicos
        cat_list = ["Todos"] + sorted(df["categoria"].unique().astype(str).tolist())
        cat_sel = st.selectbox("Filtrar Categoria", cat_list)
        df_v = df if cat_sel == "Todos" else df[df["categoria"] == cat_sel]
        
        st.divider()
        cols = st.columns(2)
        for i, (idx, row) in enumerate(df_v.iterrows()):
            with cols[i % 2]:
                st.markdown('<div class="card-produto">', unsafe_allow_html=True)
                if row['promocao']: st.markdown('<div class="badge-promo">PROMO</div>', unsafe_allow_html=True)
                
                if os.path.exists(f"images/{row['imagens']}"):
                    st.image(f"images/{row['imagens']}", use_container_width=True)
                
                st.write(f"**{row['nome']}**")
                
                if row['promocao']:
                    valor_desc = float(row['preco_venda']) * 0.85
                    st.write(f"~~R$ {float(row['preco_venda']):.2f}~~")
                    st.write(f"**R$ {valor_desc:.2f}**")
                else:
                    st.write(f"**R$ {float(row['preco_venda']):.2f}**")
                
                with st.expander("Ver Descrição"): st.write(row['descricao'])
                st.link_button("PEDIR", f"https://wa.me/5585998351874?text=Olá Adriano! Tenho interesse no {row['nome']}")
                st.markdown('</div>', unsafe_allow_html=True)

# --- ADMIN (RESTAURADO COMPLETO) ---
else:
    senha = st.sidebar.text_input("Senha", type="password")
    if senha == "suasenha123":
        # Abas completas
        t1, t2, t3, t4 = st.tabs(["➕ Cadastro", "📝 Editar", "🗑️ Remover", "💾 Backup"])
        
        with t1: # Cadastro
            with st.form("form_add", clear_on_submit=True):
                n = st.text_input("Nome do Produto")
                desc = st.text_area("Descrição")
                col_p1, col_p2 = st.columns(2)
                pv = col_p1.number_input("Preço Venda", min_value=0.0)
                pc = col_p2.number_input("Preço Custo", min_value=0.0)
                ct = st.text_input("Categoria")
                sb = st.text_input("Subcategoria")
                img = st.file_uploader("Imagem", type=['jpg','png','jpeg'])
                promo = st.checkbox("Ativar Promoção (15% OFF)")
                
                if st.form_submit_button("CADASTRAR PRODUTO"):
                    if n and img:
                        fname = f"{int(datetime.now().timestamp())}_{img.name}"
                        with open(f"images/{fname}", "wb") as f: f.write(img.getbuffer())
                        novo = pd.DataFrame([{"id": int(datetime.now().timestamp()), "nome": n, "preco_venda": pv, "preco_custo": pc, "imagens": fname, "categoria": ct, "subcategoria": sb, "descricao": desc, "visualizacoes": 0, "promocao": promo}])
                        df = pd.concat([df, novo], ignore_index=True)
                        df.to_csv("produtos.csv", index=False)
                        st.success("Produto salvo com sucesso!")
                        st.rerun()

        with t2: # Editar
            if not df.empty:
                escolha = st.selectbox("Produto para editar", df["nome"].tolist())
                idx_e = df[df["nome"] == escolha].index[0]
                with st.form("form_edit"):
                    en = st.text_input("Nome", value=df.at[idx_e, 'nome'])
                    ed = st.text_area("Descrição", value=df.at[idx_e, 'descricao'])
                    ev = st.number_input("Venda", value=float(df.at[idx_e, 'preco_venda']))
                    ec = st.number_input("Custo", value=float(df.at[idx_e, 'preco_custo']))
                    ep = st.checkbox("Promoção Ativa", value=bool(df.at[idx_e, 'promocao']))
                    if st.form_submit_button("ATUALIZAR"):
                        df.loc[idx_e, ['nome', 'descricao', 'preco_venda', 'preco_custo', 'promocao']] = [en, ed, ev, ec, ep]
                        df.to_csv("produtos.csv", index=False)
                        st.success("Alterações salvas!")
                        st.rerun()

        with t3: # Remover
            for i, row in df.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.write(f"🗑️ **{row['nome']}** | {row['categoria']}")
                if c2.button("Excluir", key=f"del_{row['id']}"):
                    df = df.drop(i)
                    df.to_csv("produtos.csv", index=False)
                    st.rerun()

        with t4: # Backup e Restauração
            st.subheader("Gerenciar Banco de Dados")
            st.download_button("BAIXAR PLANILHA (CSV)", df.to_csv(index=False).encode('utf-8'), "backup_produtos.csv")
            st.divider()
            restaurar = st.file_uploader("Subir arquivo para restaurar", type="csv")
            if restaurar and st.button("Confirmar Restauração"):
                pd.read_csv(restaurar).to_csv("produtos.csv", index=False)
                st.success("Dados restaurados!")
                st.rerun()
    else:
        st.info("Digite a senha para acessar o painel.")
