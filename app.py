import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO DE DESIGN
st.set_page_config(page_title="Adriano Designer | Studio", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;800&display=swap');
    
    /* FUNDO DA PÁGINA */
    .stApp { background-color: #f4f4f6; }

    /* CABEÇALHO MODERNO */
    .header-container { text-align: left; margin-bottom: 30px; }
    .subtitulo-loja {
        font-family: 'Inter', sans-serif;
        font-weight: 300;
        font-size: 14px;
        letter-spacing: 4px;
        color: #7a7a7a;
        text-transform: uppercase;
        margin-bottom: -10px;
        display: block;
    }
    .titulo-principal {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 42px;
        color: #1a1c23;
        line-height: 1;
    }
    .destaque-verde { color: #25D366; }

    /* CARD DO PRODUTO */
    div[data-testid="column"] {
        background-color: #ffffff;
        border: 1px solid #eef0f2;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.03);
    }

    /* NOMES DO PRODUTO */
    .nome-produto {
        color: #1a1c23 !important; 
        font-size: 20px !important;
        font-weight: 700 !important;
        margin-top: 15px !important;
        display: block;
    }

    .categoria-texto {
        color: #888 !important;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .badge-destaque {
        background: #25D366;
        color: white !important;
        padding: 5px 15px;
        border-radius: 50px;
        font-weight: bold;
        font-size: 10px;
        margin-bottom: 15px;
        display: inline-block;
    }
    
    .preco-estilo {
        color: #1a1c23 !important;
        font-weight: 800;
        font-size: 26px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÃO DE DADOS
def carregar_dados():
    colunas_obrigatorias = ["nome", "preco", "imagens", "categoria", "subcategoria", "descricao"]
    if os.path.exists("produtos.csv"):
        try:
            df = pd.read_csv("produtos.csv")
            for col in colunas_obrigatorias:
                if col not in df.columns: df[col] = ""
            return df
        except:
            return pd.DataFrame(columns=colunas_obrigatorias)
    return pd.DataFrame(columns=colunas_obrigatorias)

if not os.path.exists("images"): os.makedirs("images")

# --- CABEÇALHO ---
col_logo, col_vazio, col_texto = st.columns([1, 0.1, 5])
with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=110)

with col_texto:
    st.markdown(f"""
        <div class="header-container">
            <span class="subtitulo-loja">Loja Virtual</span>
            <h1 class="titulo-principal">ADRIANO <span class="destaque-verde">DESIGNER</span></h1>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border: 0.5px solid #e0e0e0;'>", unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
pagina = st.sidebar.radio("Navegação", ["🛍️ Vitrine", "⚙️ Painel Admin"])

# --- PÁGINA 1: VITRINE ---
if pagina == "🛍️ Vitrine":
    df = carregar_dados()
    if not df.empty:
        categorias = ["Todos"] + sorted(df["categoria"].unique().astype(str).tolist())
        escolha_cat = st.radio("Explorar Categorias", categorias, horizontal=True)
        
        df_view = df if escolha_cat == "Todos" else df[df["categoria"] == escolha_cat]
        df_view = df_view.iloc[::-1] # Recentes primeiro

        cols = st.columns(3)
        for i, (idx, row) in enumerate(df_view.iterrows()):
            with cols[i % 3]:
                if idx in df.index[-3:]:
                    st.markdown('<div class="badge-destaque">NOVIDADE</div>', unsafe_allow_html=True)
                
                fotos = str(row['imagens']).split(",")
                if os.path.exists(f"images/{fotos[0]}"):
                    st.image(f"images/{fotos[0]}", use_container_width=True)
                
                st.markdown(f'<span class="nome-produto">{row["nome"]}</span>', unsafe_allow_html=True)
                st.markdown(f'<span class="categoria-texto">{row["categoria"]} | {row["subcategoria"]}</span>', unsafe_allow_html=True)
                
                with st.expander("Ver Descrição"):
                    st.write(row['descricao'])
                
                preco_f = f"R$ {row['preco']:.2f}" if row['preco'] > 0 else "Sob Consulta"
                st.markdown(f'<p class="preco-estilo">{preco_f}</p>', unsafe_allow_html=True)
                
                link_zap = f"https://wa.me/5585998351874?text=Olá Adriano! Gostaria de detalhes do produto: {row['nome']}"
                st.link_button("ADQUIRIR AGORA", link_zap)
    else:
        st.info("Nenhum produto cadastrado.")

# --- PÁGINA 2: PAINEL ADMIN (RESTURADO COMPLETO) ---
elif pagina == "⚙️ Painel Admin":
    st.subheader("🛠️ Gestão do Catálogo")
    senha = st.text_input("Senha de Acesso", type="password")
    
    if senha == "suasenha123":
        tab1, tab2, tab3 = st.tabs(["➕ Adicionar", "📝 Editar", "🗑️ Excluir"])
        df = carregar_dados()

        # ABA ADICIONAR
        with tab1:
            with st.form("add_form", clear_on_submit=True):
                n = st.text_input("Nome do Produto")
                c1, c2 = st.columns(2)
                cat_n = c1.text_input("Categoria")
                sub_n = c2.text_input("Subcategoria")
                p = st.number_input("Preço", min_value=0.0)
                d = st.text_area("Descrição")
                f = st.file_uploader("Fotos", accept_multiple_files=True)
                
                if st.form_submit_button("PUBLICAR PRODUTO"):
                    if n and f:
                        lista_f = []
                        for foto in f:
                            nome_f = f"{datetime.now().timestamp()}_{foto.name}".replace(" ", "_")
                            with open(f"images/{nome_f}", "wb") as arq:
                                arq.write(foto.getbuffer())
                            lista_f.append(nome_f)
                        
                        novo = pd.DataFrame([{"nome": n, "preco": p, "imagens": ",".join(lista_f), 
                                             "categoria": cat_n, "subcategoria": sub_n, "descricao": d}])
                        df_final = pd.concat([df, novo], ignore_index=True)
                        df_final.to_csv("produtos.csv", index=False)
                        st.success("Produto adicionado!")
                        st.rerun()

        # ABA EDITAR
        with tab2:
            if not df.empty:
                prod_selecionado = st.selectbox("Selecione o produto para editar", df["nome"].tolist())
                idx_edit = df[df["nome"] == prod_selecionado].index[0]
                
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
                        st.success("Produto atualizado!")
                        st.rerun()
            else:
                st.write("Sem produtos para editar.")

        # ABA EXCLUIR
        with tab3:
            for i, row in df.iterrows():
                col_i, col_b = st.columns([4, 1])
                col_i.write(f"**{row['nome']}** ({row['categoria']})")
                if col_b.button("Remover", key=f"del_{i}"):
                    df_novo = df.drop(i)
                    df_novo.to_csv("produtos.csv", index=False)
                    st.warning(f"Excluído: {row['nome']}")
                    st.rerun()
    else:
        st.error("Senha incorreta.")
