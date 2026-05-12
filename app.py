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
    .text-box { display: flex; flex-direction: column; align-items: flex-start; justify-content: center; }
    .loja-online-do { font-family: 'Inter', sans-serif; font-size: 11px; letter-spacing: 2px; color: #888; margin-bottom: -10px; font-weight: 700; text-transform: uppercase; }
    .titulo-principal { font-family: 'Bebas Neue', sans-serif; font-size: 60px; color: #1a1c23; line-height: 1; margin: 0; }
    .destaque-verde { color: #25D366; }
    .search-label { font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 800; color: #1a1c23; text-align: center; margin: 15px 0; letter-spacing: 1px; }
    .card-produto { background-color: #ffffff; border: 1px solid #e9ecef; padding: 15px; border-radius: 15px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.05); position: relative; height: 100%; }
    .views-badge { font-size: 10px; color: #666; background: #eee; padding: 2px 8px; border-radius: 10px; margin-top: 10px; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÕES DE DADOS
def carregar_dados():
    caminho = "produtos.csv"
    cols_necessarias = ["nome", "preco_venda", "preco_custo", "imagens", "categoria", "subcategoria", "descricao", "visualizacoes"]
    if os.path.exists(caminho):
        try:
            df = pd.read_csv(caminho)
            for col in cols_necessarias:
                if col not in df.columns:
                    df[col] = 0 if "preco" in col or "visualizacoes" in col else ""
            return df
        except: pass
    return pd.DataFrame(columns=cols_necessarias)

if not os.path.exists("images"): os.makedirs("images")
df = carregar_dados()

# --- CABEÇALHO (LOGO À ESQUERDA) ---
_, col_header, _ = st.columns([1, 4, 1])
with col_header:
    col_logo, col_texto = st.columns([1, 5])
    with col_logo:
        if os.path.exists("logo.png"): st.image("logo.png", width=85) 
    with col_texto:
        st.markdown(f"""<div class="text-box"><p class="loja-online-do">LOJA ONLINE DO:</p><h1 class="titulo-principal">ADRIANO <span class="destaque-verde">DESIGNER</span></h1></div>""", unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
menu_principal = st.sidebar.radio("Navegar", ["🛍️ Vitrine", "⚙️ Painel Admin"])

# --- VITRINE ---
if menu_principal == "🛍️ Vitrine":
    st.markdown('<p class="search-label">PROCURE SEU ESTILO AQUI.</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        cats = ["Todos"] + sorted(df["categoria"].unique().astype(str).tolist())
        cat_sel = st.selectbox("CATEGORIA", cats, label_visibility="collapsed")
    with c2:
        df_f = df if cat_sel == "Todos" else df[df["categoria"] == cat_sel]
        subs = ["Todas"] + sorted(df_f["subcategoria"].unique().astype(str).tolist())
        sub_sel = st.selectbox("SUBCATEGORIA", subs, label_visibility="collapsed")
    
    df_vitrine = df_f if sub_sel == "Todas" else df_f[df_f["subcategoria"] == sub_sel]
    
    st.divider()
    
    if df_vitrine.empty:
        st.info("Nenhum produto encontrado.")
    else:
        cols = st.columns(3)
        for i, (idx, row) in enumerate(df_vitrine.iterrows()):
            # CONTADOR DE VISUALIZAÇÕES: Aumenta ao carregar a vitrine
            df.at[idx, "visualizacoes"] += 1
            
            with cols[i % 3]:
                st.markdown('<div class="card-produto">', unsafe_allow_html=True)
                if os.path.exists(f"images/{row['imagens']}"):
                    st.image(f"images/{row['imagens']}", use_container_width=True)
                st.write(f"**{row['nome']}**")
                st.caption(f"{row['descricao'][:50]}...")
                st.write(f"### R$ {float(row['preco_venda']):.2f}")
                st.link_button("WHATSAPP", f"https://wa.me/5585998351874?text=Olá Adriano! Vi o produto {row['nome']}")
                st.markdown(f'<span class="views-badge">👁️ {int(row["visualizacoes"])} visualizações</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        # Salva as visualizações discretamente
        df.to_csv("produtos.csv", index=False)

# --- ADMIN ---
else:
    senha = st.text_input("Senha Admin", type="password")
    if senha == "suasenha123":
        t1, t2, t3, t4 = st.tabs(["➕ Novo Produto", "📝 Editar", "🗑️ Remover", "💾 Backup"])
        
        sugestoes_cat = sorted(df["categoria"].unique().astype(str).tolist()) if not df.empty else []
        sugestoes_sub = sorted(df["subcategoria"].unique().astype(str).tolist()) if not df.empty else []

        with t1:
            with st.form("form_novo", clear_on_submit=True):
                nome = st.text_input("Nome do Produto")
                desc = st.text_area("Descrição do Produto")
                cv1, cv2 = st.columns(2)
                preco_v = cv1.number_input("Valor de Venda (R$)", min_value=0.0)
                preco_c = cv2.number_input("Valor de Custo (R$)", min_value=0.0)
                
                ca, cb = st.columns(2)
                with ca:
                    cat_op = st.selectbox("Categoria", ["+ Nova"] + sugestoes_cat)
                    cat_f = st.text_input("Nome da nova categoria") if cat_op == "+ Nova" else cat_op
                with cb:
                    sub_op = st.selectbox("Subcategoria", ["+ Nova"] + sugestoes_sub)
                    sub_f = st.text_input("Nome da nova subcategoria") if sub_op == "+ Nova" else sub_op
                
                foto = st.file_uploader("Imagem do Produto", type=['jpg', 'png', 'jpeg'])
                
                if st.form_submit_button("CADASTRAR PRODUTO"):
                    if nome and foto and cat_f:
                        nome_arq = f"{datetime.now().timestamp()}_{foto.name}"
                        with open(f"images/{nome_arq}", "wb") as f: f.write(foto.getbuffer())
                        novo = pd.DataFrame([{"nome": nome, "preco_venda": preco_v, "preco_custo": preco_c, 
                                             "imagens": nome_arq, "categoria": cat_f, "subcategoria": sub_f, 
                                             "descricao": desc, "visualizacoes": 0}])
                        df = pd.concat([df, novo], ignore_index=True)
                        df.to_csv("produtos.csv", index=False)
                        st.success("Produto cadastrado com sucesso!")
                        st.rerun()

        with t2: # EDITAR
            if not df.empty:
                escolha = st.selectbox("Produto:", df["nome"].tolist())
                idx = df[df["nome"] == escolha].index[0]
                with st.form("f_edit"):
                    df.at[idx, 'nome'] = st.text_input("Nome", value=df.at[idx, 'nome'])
                    df.at[idx, 'preco_venda'] = st.number_input("Venda", value=float(df.at[idx, 'preco_venda']))
                    df.at[idx, 'preco_custo'] = st.number_input("Custo", value=float(df.at[idx, 'preco_custo']))
                    if st.form_submit_button("SALVAR"):
                        df.to_csv("produtos.csv", index=False)
                        st.rerun()

        with t4: # BACKUP E RESTAURAÇÃO
            st.subheader("📥 Exportar Backup")
            st.download_button("BAIXAR CSV", df.to_csv(index=False).encode('utf-8'), "backup_loja.csv", "text/csv")
            st.divider()
            st.subheader("📤 Restaurar Backup")
            arq = st.file_uploader("Subir arquivo de backup", type=["csv"])
            if arq and st.button("RESTAURAR AGORA"):
                pd.read_csv(arq).to_csv("produtos.csv", index=False)
                st.rerun()
