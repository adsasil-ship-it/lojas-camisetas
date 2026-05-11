import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO E DESIGN
st.set_page_config(page_title="Adriano Designer | Catálogo", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;800&display=swap');
    .stApp { background-color: #f8f9fa; }
    .header-container { text-align: left; margin-bottom: 20px; }
    .subtitulo { font-family: 'Inter', sans-serif; font-weight: 300; font-size: 12px; letter-spacing: 3px; color: #6c757d; text-transform: uppercase; }
    .titulo-principal { font-family: 'Inter', sans-serif; font-weight: 800; font-size: 40px; color: #1a1c23; margin-top: -10px; }
    .destaque-verde { color: #25D366; }
    .card-produto { background-color: #ffffff; border: 1px solid #e9ecef; padding: 15px; border-radius: 15px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    .nome-prod { font-weight: 700; font-size: 18px; color: #343a40; margin-top: 10px; }
    .sub-texto { font-size: 12px; color: #888; text-transform: uppercase; }
    .preco-prod { font-weight: 800; font-size: 22px; color: #212529; margin: 5px 0; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÕES DE DADOS
def carregar_dados():
    caminho = "produtos.csv"
    colunas = ["nome", "preco", "imagens", "categoria", "subcategoria", "descricao"]
    if os.path.exists(caminho):
        try:
            df = pd.read_csv(caminho)
            for col in colunas:
                if col not in df.columns: df[col] = ""
            return df
        except: pass
    return pd.DataFrame(columns=colunas)

if not os.path.exists("images"): os.makedirs("images")
df = carregar_dados()

# --- CABEÇALHO ---
st.markdown('<div class="header-container"><span class="subtitulo">Premium Collection</span>'
            '<h1 class="titulo-principal">ADRIANO <span class="destaque-verde">DESIGNER</span></h1></div>', unsafe_allow_html=True)

menu = st.sidebar.radio("Navegar", ["🛍️ Vitrine", "⚙️ Painel Admin"])

# --- VITRINE ---
if menu == "🛍️ Vitrine":
    if df.empty:
        st.info("Catálogo vazio. Vá ao Admin para cadastrar ou restaurar backup.")
    else:
        st.sidebar.subheader("Filtros")
        # Filtro de Categoria
        lista_cats = ["Todas"] + sorted(df["categoria"].unique().astype(str).tolist())
        cat_sel = st.sidebar.selectbox("Categoria", lista_cats)
        
        df_filtrado = df if cat_sel == "Todas" else df[df["categoria"] == cat_sel]
        
        # Filtro de Subcategoria (dinâmico)
        lista_subs = ["Todas"] + sorted(df_filtrado["subcategoria"].unique().astype(str).tolist())
        sub_sel = st.sidebar.selectbox("Subcategoria", lista_subs)
        
        if sub_sel != "Todas":
            df_filtrado = df_filtrado[df_filtrado["subcategoria"] == sub_sel]

        cols = st.columns(3)
        for i, (idx, row) in enumerate(df_filtrado.iloc[::-1].iterrows()):
            with cols[i % 3]:
                st.markdown('<div class="card-produto">', unsafe_allow_html=True)
                if os.path.exists(f"images/{row['imagens']}"):
                    st.image(f"images/{row['imagens']}", use_container_width=True)
                st.markdown(f'<div class="sub-texto">{row["categoria"]} | {row["subcategoria"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="nome-prod">{row["nome"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="preco-prod">R$ {float(row["preco"]):.2f}</div>', unsafe_allow_html=True)
                st.link_button("COMPRAR NO WHATSAPP", f"https://wa.me/5585998351874?text=Tenho interesse no produto: {row['nome']}")
                st.markdown('</div>', unsafe_allow_html=True)

# --- ADMIN ---
else:
    senha = st.text_input("Senha", type="password")
    if senha == "suasenha123":
        t1, t2, t3 = st.tabs(["➕ Adicionar", "🗑️ Gerenciar", "💾 Backup"])
        
        with t1:
            with st.form("add_prod", clear_on_submit=True):
                nome = st.text_input("Nome do Produto")
                preco = st.number_input("Preço", min_value=0.0, format="%.2f")
                
                # Seleção Inteligente de Categoria
                exist_cats = sorted(df["categoria"].unique().astype(str).tolist()) if not df.empty else []
                cat_escolha = st.selectbox("Escolha Categoria", ["+ Nova"] + exist_cats)
                cat_final = st.text_input("Nova Categoria") if cat_escolha == "+ Nova" else cat_escolha
                
                # Seleção Inteligente de Subcategoria
                exist_subs = sorted(df["subcategoria"].unique().astype(str).tolist()) if not df.empty else []
                sub_escolha = st.selectbox("Escolha Subcategoria", ["+ Nova"] + exist_subs)
                sub_final = st.text_input("Nova Subcategoria") if sub_escolha == "+ Nova" else sub_escolha
                
                desc = st.text_area("Descrição")
                foto = st.file_uploader("Foto", type=['jpg', 'png', 'jpeg'])
                
                if st.form_submit_button("PUBLICAR"):
                    if nome and foto and cat_final:
                        nome_arq = f"{datetime.now().timestamp()}_{foto.name}".replace(" ","_")
                        with open(f"images/{nome_arq}", "wb") as f: f.write(foto.getbuffer())
                        
                        novo = pd.DataFrame([{"nome": nome, "preco": preco, "imagens": nome_arq, 
                                             "categoria": cat_final, "subcategoria": sub_final, "descricao": desc}])
                        df = pd.concat([df, novo], ignore_index=True)
                        df.to_csv("produtos.csv", index=False)
                        st.success("Produto Publicado!")
                        st.rerun()

        with t2:
            if not df.empty:
                for i, row in df.iterrows():
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"**{row['nome']}** ({row['categoria']})")
                    if c2.button("Remover", key=f"d_{i}"):
                        df = df.drop(i)
                        df.to_csv("produtos.csv", index=False)
                        st.rerun()

        with t3:
            st.subheader("Segurança dos Dados")
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 BAIXAR BACKUP AGORA", csv, "backup_catalogo.csv", "text/csv")
            st.divider()
            up = st.file_uploader("Restaurar via Backup", type="csv")
            if st.button("CONFIRMAR RESTAURAÇÃO") and up:
                pd.read_csv(up).to_csv("produtos.csv", index=False)
                st.success("Dados Restaurados!")
                st.rerun()
