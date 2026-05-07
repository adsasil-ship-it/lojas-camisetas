import streamlit as st
import pandas as pd
import os

# 1. CONFIGURAÇÃO DE DESIGN E IDENTIDADE
st.set_page_config(page_title="Adriano Designer | Studio", layout="wide")

# CSS para Estética Dark Premium
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0e1117;
    }

    div[data-testid="column"] {
        background-color: #1a1c23;
        border: 1px solid #333;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        margin-bottom: 30px;
    }

    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
        color: white;
        border: none;
        padding: 10px;
        font-weight: bold;
        transition: 0.3s;
    }
    
    /* Botão de Excluir Vermelho */
    .stButton>button.excluir-btn {
        background: linear-gradient(90deg, #ff4b4b 0%, #a50000 100%) !important;
    }

    h1, h2, h3, h4 { color: #ffffff !important; }
    p, span { color: #cfcfcf !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÃO DE DADOS
def carregar_dados():
    colunas_obrigatorias = ["nome", "preco", "imagens", "categoria", "descricao"]
    caminho_csv = "produtos.csv"
    
    if os.path.exists(caminho_csv):
        try:
            df = pd.read_csv(caminho_csv)
            for col in colunas_obrigatorias:
                if col not in df.columns:
                    df[col] = "Não informado" if col != "preco" else 0.0
            return df
        except:
            return pd.DataFrame(columns=colunas_obrigatorias)
    return pd.DataFrame(columns=colunas_obrigatorias)

if not os.path.exists("images"):
    os.makedirs("images")

# --- CABEÇALHO ---
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)

with col_titulo:
    st.markdown("""
        <h1 style='margin-bottom: 0px;'>ADRIANO <span style='color: #25D366;'>DESIGNER</span></h1>
        <p style='font-size: 20px; color: #a0a0a0; margin-top: -10px;'>Estúdio de Criação & Personalizados Premium</p>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- NAVEGAÇÃO ---
pagina = st.sidebar.radio("Ir para:", ["🛍️ Vitrine Premium", "⚙️ Painel do Designer"])

# --- PÁGINA 1: VITRINE ---
if pagina == "🛍️ Vitrine Premium":
    df = carregar_dados()
    if df.empty:
        st.info("Aguardando o próximo lançamento oficial...")
    else:
        categorias = ["Todos os Estilos"] + sorted(df["categoria"].unique().tolist())
        cat_sel = st.sidebar.selectbox("Filtrar Coleção", categorias)
        df_view = df if cat_sel == "Todos os Estilos" else df[df["categoria"] == cat_sel]

        cols = st.columns(3)
        for index, row in df_view.reset_index().iterrows():
            with cols[index % 3]:
                fotos = str(row['imagens']).split(",")
                
                # --- BLOCO DE SEGURANÇA PARA IMAGEM PRINCIPAL ---
                foto_principal = f"images/{fotos[0]}"
                if os.path.exists(foto_principal):
                    try:
                        st.image(foto_principal, use_container_width=True)
                    except:
                        st.error(f"Erro no arquivo: {fotos[0]}")
                
                st.markdown(f"### {row['nome']}")
                st.markdown(f"<span style='background-color: #333; padding: 4px 10px; border-radius: 5px; font-size: 12px;'>{row['categoria']}</span>", unsafe_allow_html=True)
                
                with st.expander("🔍 Detalhes e + Fotos"):
                    st.write(row['descricao'])
                    if len(fotos) > 1:
                        for f in fotos[1:]:
                            caminho_f = f"images/{f}"
                            # --- FILTRO PARA IGNORAR ARQUIVOS QUE NÃO SÃO IMAGENS ---
                            if os.path.exists(caminho_f) and f.lower().endswith(('.png', '.jpg', '.jpeg')):
                                try:
                                    st.image(caminho_f, use_container_width=True)
                                except:
                                    continue # Se der erro, pula para a próxima
                
                preco_texto = f"R$ {row['preco']:.2f}" if row['preco'] > 0 else "SOB CONSULTA"
                st.markdown(f"<h2 style='color: #25D366;'>{preco_texto}</h2>", unsafe_allow_html=True)
                
                meu_whats = "5585998351874" 
                msg_zap = f"Olá Adriano! Gostaria de falar sobre {row['nome']}."
                st.link_button("🚀 SOLICITAR VIA WHATSAPP", f"https://wa.me/{meu_whats}?text={msg_zap.replace(' ', '%20')}")

# --- PÁGINA 2: ADMIN ---
elif pagina == "⚙️ Painel do Designer":
    st.title("🛠️ Gerenciar Catálogo")
    senha = st.text_input("Senha de Acesso", type="password")
    
    if senha == "suasenha123":
        tab1, tab2 = st.tabs(["➕ Adicionar Produto", "🗑️ Excluir Produtos"])

        # ABA 1: ADICIONAR
        with tab1:
            with st.form("cadastro_form", clear_on_submit=True):
                n = st.text_input("Nome do Lançamento")
                d = st.text_area("Descrição")
                p = st.number_input("Preço", min_value=0.0)
                cat = st.selectbox("Categoria", ["Futebol", "Religiosa", "Geek", "Corporativa", "Outros"])
                f = st.file_uploader("Fotos", accept_multiple_files=True)
                
                if st.form_submit_button("PUBLICAR PRODUTO"):
                    if f and n:
                        lista_nomes = []
                        for foto in f:
                            nome_f = foto.name.replace(" ", "_")
                            with open(os.path.join("images", nome_f), "wb") as arq:
                                arq.write(foto.getbuffer())
                            lista_nomes.append(nome_f)
                        
                        df_atual = carregar_dados()
                        novo = pd.DataFrame([{"nome": n, "preco": p, "imagens": ",".join(lista_nomes), "categoria": cat, "descricao": d}])
                        pd.concat([df_atual, novo], ignore_index=True).to_csv("produtos.csv", index=False)
                        st.success("Produto adicionado!")
                        st.rerun()

        # ABA 2: EXCLUIR
        with tab2:
            st.subheader("Selecione os itens para remover")
            df_excluir = carregar_dados()
            
            if df_excluir.empty:
                st.write("Nenhum produto para excluir.")
            else:
                for index, row in df_excluir.iterrows():
                    col_info, col_btn = st.columns([3, 1])
                    with col_info:
                        st.write(f"**{row['nome']}** ({row['categoria']})")
                    with col_btn:
                        # Botão de excluir para cada linha
                        if st.button(f"Excluir", key=f"del_{index}"):
                            # Remove o item do DataFrame
                            df_novo = df_excluir.drop(index)
                            df_novo.to_csv("produtos.csv", index=False)
                            st.warning(f"Produto '{row['nome']}' removido!")
                            st.rerun()
