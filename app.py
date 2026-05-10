import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO DE DESIGN
st.set_page_config(page_title="Adriano Designer | Studio", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0e1117; }
    
    /* Cards de Produto */
    div[data-testid="column"] {
        background-color: #1a1c23;
        border: 1px solid #333;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }

    /* Badge de Destaque */
    .badge-destaque {
        background: linear-gradient(90deg, #FFD700, #FFA500);
        color: black !important;
        padding: 2px 10px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 12px;
        margin-bottom: 10px;
        display: inline-block;
    }

    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
        color: white;
        font-weight: bold;
    }
    
    h1, h2, h3 { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÕES DE DADOS
def carregar_dados():
    colunas = ["nome", "preco", "imagens", "categoria", "subcategoria", "descricao"]
    if os.path.exists("produtos.csv"):
        df = pd.read_csv("produtos.csv")
        # Garantir que todas as colunas existam
        for col in colunas:
            if col not in df.columns: df[col] = ""
        return df
    return pd.DataFrame(columns=colunas)

if not os.path.exists("images"): os.makedirs("images")

# --- CABEÇALHO ---
col_logo, col_titulo = st.columns([1, 5])
with col_titulo:
    st.markdown("<h1>ADRIANO <span style='color: #25D366;'>DESIGNER</span></h1>", unsafe_allow_html=True)
    st.write("Estúdio de Criação & Personalizados Premium")

# --- NAVEGAÇÃO LATERAL ---
pagina = st.sidebar.radio("Navegação", ["🛍️ Vitrine", "⚙️ Painel Admin"])

if pagina == "🛍️ Vitrine":
    df = carregar_dados()
    
    # Menu de Categorias Visível (Horizontal)
    if not df.empty:
        lista_cats = ["Todos"] + sorted(df["categoria"].unique().tolist())
        escolha_cat = st.segmented_control("Filtrar por Coleção:", lista_cats, default="Todos")
        
        df_filtrado = df if escolha_cat == "Todos" else df[df["categoria"] == escolha_cat]
        
        # Ordenar: Recentes primeiro
        df_filtrado = df_filtrado.iloc[::-1] 

        st.markdown("---")
        
        cols = st.columns(3)
        for i, (idx, row) in enumerate(df_filtrado.iterrows()):
            with cols[i % 3]:
                # Selo de Destaque para os 3 mais recentes no sistema
                if idx in df.tail(3).index:
                    st.markdown('<div class="badge-destaque">✨ NOVIDADE / DESTAQUE</div>', unsafe_allow_html=True)
                
                fotos = str(row['imagens']).split(",")
                if os.path.exists(f"images/{fotos[0]}"):
                    st.image(f"images/{fotos[0]}", use_container_width=True)
                
                st.markdown(f"### {row['nome']}")
                st.caption(f"{row['categoria']} › {row['subcategoria']}")
                
                with st.expander("Ver detalhes"):
                    st.write(row['descricao'])
                
                preco = f"R$ {row['preco']:.2f}" if row['preco'] > 0 else "CONSULTAR"
                st.markdown(f"<h3 style='color: #25D366;'>{preco}</h3>", unsafe_allow_html=True)
                
                zap_link = f"https://wa.me/5585998351874?text=Oi! Quero saber sobre o {row['nome']}"
                st.link_button("PEDIR VIA WHATSAPP", zap_link)

elif pagina == "⚙️ Painel Admin":
    senha = st.sidebar.text_input("Senha", type="password")
    if senha == "suasenha123":
        tab1, tab2, tab3 = st.tabs(["➕ Novo", "📝 Editar", "🗑️ Remover"])
        df = carregar_dados()

        with tab1:
            with st.form("add_form"):
                n = st.text_input("Nome do Produto")
                col1, col2 = st.columns(2)
                cat = col1.text_input("Categoria (Ex: Futebol)")
                sub = col2.text_input("Subcategoria (Ex: Camisas Retro)")
                p = st.number_input("Preço", min_value=0.0)
                d = st.text_area("Descrição")
                f = st.file_uploader("Fotos", accept_multiple_files=True)
                
                if st.form_submit_button("CADASTRAR"):
                    if n and f:
                        nomes_f = []
                        for foto in f:
                            nome_f = f"{datetime.now().timestamp()}_{foto.name}"
                            with open(f"images/{nome_f}", "wb") as arq:
                                arq.write(foto.getbuffer())
                            nomes_f.append(nome_f)
                        
                        novo_item = pd.DataFrame([{"nome": n, "preco": p, "imagens": ",".join(nomes_f), 
                                                 "categoria": cat, "subcategoria": sub, "descricao": d}])
                        pd.concat([df, novo_item]).to_csv("produtos.csv", index=False)
                        st.success("Cadastrado!")
                        st.rerun()

        with tab2:
            st.subheader("Selecione um produto para editar")
            prod_edit = st.selectbox("Produto", df["nome"].tolist())
            idx_edit = df[df["nome"] == prod_edit].index[0]
            
            with st.form("edit_form"):
                en = st.text_input("Nome", value=df.at[idx_edit, 'nome'])
                ecat = st.text_input("Categoria", value=df.at[idx_edit, 'categoria'])
                esub = st.text_input("Subcategoria", value=df.at[idx_edit, 'subcategoria'])
                ep = st.number_input("Preço", value=float(df.at[idx_edit, 'preco']))
                ed = st.text_area("Descrição", value=df.at[idx_edit, 'descricao'])
                
                if st.form_submit_button("SALVAR ALTERAÇÕES"):
                    df.at[idx_edit, 'nome'] = en
                    df.at[idx_edit, 'categoria'] = ecat
                    df.at[idx_edit, 'subcategoria'] = esub
                    df.at[idx_edit, 'preco'] = ep
                    df.at[idx_edit, 'descricao'] = ed
                    df.to_csv("produtos.csv", index=False)
                    st.success("Atualizado!")
                    st.rerun()

        with tab3:
            for i, row in df.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.write(f"{row['nome']} | {row['categoria']}")
                if c2.button("Excluir", key=f"del_{i}"):
                    df.drop(i).to_csv("produtos.csv", index=False)
                    st.rerun()
    else:
        st.warning("Insira a senha para acessar o painel.")
