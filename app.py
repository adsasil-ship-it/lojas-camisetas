import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Adriano Designer | Studio", layout="wide")

# CSS Ajustado para garantir que os textos apareçam
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0e1117; }
    
    .stMarkdown h3 { color: white !important; margin-top: 10px; font-weight: 700; }
    .stMarkdown p { color: #cfcfcf !important; }
    
    div[data-testid="column"] {
        background-color: #1a1c23;
        border: 1px solid #333;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }

    .badge-destaque {
        background: linear-gradient(90deg, #25D366, #128C7E);
        color: white !important;
        padding: 4px 12px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 11px;
        margin-bottom: 10px;
        display: inline-block;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÃO DE DADOS (CORRIGIDA PARA NÃO SUMIR NOMES)
def carregar_dados():
    colunas_obrigatorias = ["nome", "preco", "imagens", "categoria", "subcategoria", "descricao"]
    caminho_csv = "produtos.csv"
    
    if os.path.exists(caminho_csv):
        df = pd.read_csv(caminho_csv)
        # Se faltar alguma coluna (como subcategoria), ele cria vazia para não dar erro
        for col in colunas_obrigatorias:
            if col not in df.columns:
                df[col] = ""
        return df
    return pd.DataFrame(columns=colunas_obrigatorias)

if not os.path.exists("images"): os.makedirs("images")

# --- CABEÇALHO (LOGO VOLTOU) ---
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    else:
        st.markdown("### 🎨 ADRIANO") # Texto reserva se a logo sumir do PC

with col_titulo:
    st.markdown("<h1 style='margin-bottom:0'>ADRIANO <span style='color: #25D366;'>DESIGNER</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:18px; color:#a0a0a0'>Estúdio de Criação & Personalizados Premium</p>", unsafe_allow_html=True)

st.markdown("---")

# --- NAVEGAÇÃO ---
pagina = st.sidebar.radio("Navegação", ["🛍️ Vitrine", "⚙️ Painel Admin"])

if pagina == "🛍️ Vitrine":
    df = carregar_dados()
    
    if df.empty:
        st.info("Nenhum produto cadastrado no momento.")
    else:
        # Menu de Categorias mais visível
        categorias = ["Todos"] + sorted(df["categoria"].unique().astype(str).tolist())
        escolha_cat = st.radio("Selecione uma Coleção:", categorias, horizontal=True)
        
        df_view = df if escolha_cat == "Todos" else df[df["categoria"] == escolha_cat]
        # Recentes primeiro
        df_view = df_view.iloc[::-1]

        cols = st.columns(3)
        for i, (idx, row) in enumerate(df_view.iterrows()):
            with cols[i % 3]:
                # DESTAQUE: Se for um dos últimos 3 cadastrados
                if idx in df.index[-3:]:
                    st.markdown('<div class="badge-destaque">✨ Destaque / Lançamento</div>', unsafe_allow_html=True)
                
                # Imagem
                fotos = str(row['imagens']).split(",")
                caminho_img = f"images/{fotos[0]}"
                if os.path.exists(caminho_img):
                    st.image(caminho_img, use_container_width=True)
                
                # Dados do Produto (Garantindo que apareçam)
                st.markdown(f"### {row['nome']}")
                st.markdown(f"**{row['categoria']}** | {row['subcategoria']}")
                
                with st.expander("Ver Descrição"):
                    st.write(row['descricao'])
                
                preco = f"R$ {row['preco']:.2f}" if row['preco'] > 0 else "CONSULTAR"
                st.markdown(f"<h2 style='color: #25D366; font-size: 24px;'>{preco}</h2>", unsafe_allow_html=True)
                
                link_zap = f"https://wa.me/5585998351874?text=Olá Adriano, tenho interesse no: {row['nome']}"
                st.link_button("🚀 SOLICITAR AGORA", link_zap)

elif pagina == "⚙️ Painel Admin":
    senha = st.sidebar.text_input("Senha", type="password")
    if senha == "suasenha123":
        tab1, tab2, tab3 = st.tabs(["➕ Adicionar", "📝 Editar", "🗑️ Excluir"])
        df = carregar_dados()

        with tab1:
            with st.form("form_add", clear_on_submit=True):
                n = st.text_input("Nome do Produto")
                col1, col2 = st.columns(2)
                cat = col1.text_input("Categoria")
                sub = col2.text_input("Subcategoria")
                p = st.number_input("Preço", min_value=0.0)
                d = st.text_area("Descrição")
                f = st.file_uploader("Fotos", accept_multiple_files=True)
                
                if st.form_submit_button("PUBLICAR"):
                    if n and f:
                        lista_f = []
                        for foto in f:
                            nome_f = f"{datetime.now().timestamp()}_{foto.name}".replace(" ", "_")
                            with open(f"images/{nome_f}", "wb") as arq:
                                arq.write(foto.getbuffer())
                            lista_f.append(nome_f)
                        
                        novo = pd.DataFrame([{"nome": n, "preco": p, "imagens": ",".join(lista_f), "categoria": cat, "subcategoria": sub, "descricao": d}])
                        pd.concat([df, novo], ignore_index=True).to_csv("produtos.csv", index=False)
                        st.success("Produto Publicado!")
                        st.rerun()

        with tab2:
            if not df.empty:
                prod_edit = st.selectbox("Escolha o produto para editar", df["nome"].tolist())
                idx_edit = df[df["nome"] == prod_edit].index[0]
                
                with st.form("form_edit"):
                    en = st.text_input("Nome", value=df.at[idx_edit, 'nome'])
                    ecat = st.text_input("Categoria", value=df.at[idx_edit, 'categoria'])
                    esub = st.text_input("Subcategoria", value=df.at[idx_edit, 'subcategoria'])
                    ep = st.number_input("Preço", value=float(df.at[idx_edit, 'preco']))
                    ed = st.text_area("Descrição", value=df.at[idx_edit, 'descricao'])
                    
                    if st.form_submit_button("ATUALIZAR DADOS"):
                        df.at[idx_edit, 'nome'] = en
                        df.at[idx_edit, 'categoria'] = ecat
                        df.at[idx_edit, 'subcategoria'] = esub
                        df.at[idx_edit, 'preco'] = ep
                        df.at[idx_edit, 'descricao'] = ed
                        df.to_csv("produtos.csv", index=False)
                        st.success("Dados atualizados com sucesso!")
                        st.rerun()
            else:
                st.write("Nada para editar.")

        with tab3:
            for i, row in df.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{row['nome']}**")
                if c2.button("Excluir", key=f"del_{i}"):
                    df.drop(i).to_csv("produtos.csv", index=False)
                    st.rerun()
