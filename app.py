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

    .card-produto { 
        background: white; border: 1px solid #eee; padding: 10px; border-radius: 12px; 
        text-align: center; height: 100%; position: relative; display: flex; flex-direction: column;
    }

    /* Selo de Promoção CORRIGIDO (na frente de tudo) */
    .badge-promo { 
        background: #A020F0; color: white; font-size: 10px; padding: 4px 10px; 
        border-radius: 6px; position: absolute; top: 10px; right: 10px; 
        z-index: 999 !important; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    .views-counter { font-size: 10px; color: #999; margin-top: 8px; display: block; }
    .preco-antigo { text-decoration: line-through; color: #888; font-size: 12px; }
    .preco-venda { color: #1a1c23; font-weight: 800; font-size: 18px; }
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
                    df[col] = 0 if "visualizacoes" in col else (0.0 if "preco" in col else (False if col == "promocao" else ""))
            return df
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

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
        st.info("Nenhum produto cadastrado.")
    else:
        cat_sel = st.selectbox("Filtrar Categoria", ["Todos"] + sorted(df["categoria"].unique().astype(str).tolist()))
        df_v = df if cat_sel == "Todos" else df[df["categoria"] == cat_sel]
        
        st.divider()
        cols = st.columns(2)
        for i, (idx, row) in enumerate(df_v.iterrows()):
            # Incrementa visualização
            df.at[idx, "visualizacoes"] = int(df.at[idx, "visualizacoes"]) + 1
            
            with cols[i % 2]:
                st.markdown('<div class="card-produto">', unsafe_allow_html=True)
                
                # Selo Promoção na frente
                if row['promocao']: 
                    st.markdown('<div class="badge-promo">15% OFF</div>', unsafe_allow_html=True)
                
                if os.path.exists(f"images/{row['imagens']}"):
                    st.image(f"images/{row['imagens']}", use_container_width=True)
                
                st.markdown(f"**{row['nome']}**")
                
                if row['promocao']:
                    valor_desc = float(row['preco_venda']) * 0.85
                    st.markdown(f'<span class="preco-antigo">R$ {float(row["preco_venda"]):.2f}</span>', unsafe_allow_html=True)
                    st.markdown(f'<span class="preco-venda">R$ {valor_desc:.2f}</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="preco-venda">R$ {float(row["preco_venda"]):.2f}</span>', unsafe_allow_html=True)
                
                with st.expander("Ver Descrição"): st.write(row['descricao'])
                
                st.link_button("PEDIR", f"https://wa.me/5585998351874?text=Interesse: {row['nome']}")
                
                # Contador de visualizações adicionado novamente
                st.markdown(f'<span class="views-counter">👁️ {int(row["visualizacoes"])} visualizações</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Salva as visualizações no CSV
        df.to_csv("produtos.csv", index=False)

# --- ADMIN ---
else:
    senha = st.sidebar.text_input("Senha", type="password")
    if senha == "suasenha123":
        t1, t2, t3, t4 = st.tabs(["➕ Cadastro", "📝 Editar", "🗑️ Remover", "💾 Backup"])
        
        with t1: # Cadastro
            with st.form("form_add", clear_on_submit=True):
                n = st.text_input("Nome")
                desc = st.text_area("Descrição")
                col1, col2 = st.columns(2)
                pv = col1.number_input("Preço Venda", min_value=0.0)
                pc = col2.number_input("Preço Custo", min_value=0.0)
                ct = st.text_input("Categoria")
                sb = st.text_input("Subcategoria")
                img = st.file_uploader("Imagem", type=['jpg','png','jpeg'])
                promo = st.checkbox("Ativar Promoção")
                if st.form_submit_button("CADASTRAR"):
                    if n and img:
                        fname = f"{int(datetime.now().timestamp())}_{img.name}"
                        with open(f"images/{fname}", "wb") as f: f.write(img.getbuffer())
                        novo = pd.DataFrame([{"id": int(datetime.now().timestamp()), "nome": n, "preco_venda": pv, "preco_custo": pc, "imagens": fname, "categoria": ct, "subcategoria": sb, "descricao": desc, "visualizacoes": 0, "promocao": promo}])
                        df = pd.concat([df, novo], ignore_index=True)
                        df.to_csv("produtos.csv", index=False)
                        st.success("Salvo!")
                        st.rerun()

        with t2: # Editar
            if not df.empty:
                escolha = st.selectbox("Escolha o produto", df["nome"].tolist())
                idx_e = df[df["nome"] == escolha].index[0]
                with st.form("form_edit"):
                    en = st.text_input("Nome", value=df.at[idx_e, 'nome'])
                    ev = st.number_input("Preço Venda", value=float(df.at[idx_e, 'preco_venda']))
                    ep = st.checkbox("Promoção Ativa", value=bool(df.at[idx_e, 'promocao']))
                    if st.form_submit_button("ATUALIZAR"):
                        df.at[idx_e, 'nome'] = en
                        df.at[idx_e, 'preco_venda'] = ev
                        df.at[idx_e, 'promocao'] = ep
                        df.to_csv("produtos.csv", index=False)
                        st.rerun()

        with t3: # Remover
            for i, row in df.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.write(f"🗑️ {row['nome']}")
                if c2.button("Apagar", key=f"del_{row['id']}"):
                    df = df.drop(i)
                    df.to_csv("produtos.csv", index=False)
                    st.rerun()

        with t4: # Backup
            st.download_button("BAIXAR CSV", df.to_csv(index=False).encode('utf-8'), "backup.csv")
            restaurar = st.file_uploader("Restaurar", type="csv")
            if restaurar and st.button("Confirmar"):
                pd.read_csv(restaurar).to_csv("produtos.csv", index=False)
                st.rerun()
