import streamlit as st
import pandas as pd
import os

# 1. CONFIGURAÇÃO DE DESIGN PREMIUM
st.set_page_config(page_title="Adriano Designer | Studio", layout="wide")

# CSS Avançado para Estética de Marca
st.markdown("""
    <style>
    /* Fundo e Fontes */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background-color: #0e1117; /* Fundo Escuro Moderno */
    }
    
    /* Card do Produto */
    div[data-testid="column"] {
        background-color: #1a1c23;
        border: 1px solid #333;
        padding: 20px;
        border-radius: 20px;
        transition: transform 0.3s ease;
    }
    div[data-testid="column"]:hover {
        transform: translateY(-10px);
        border-color: #25D366;
    }

    /* Botão de WhatsApp Customizado */
    .stButton>button {
        width: 100%;
        border-radius: 50px;
        background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
        color: white;
        border: none;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Títulos */
    h1, h2, h3 { color: #ffffff !important; }
    p { color: #a0a0a0 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. GESTÃO DE DADOS
if not os.path.exists("images"):
    os.makedirs("images")

def carregar_dados():
    if os.path.exists("produtos.csv"):
        return pd.read_csv("produtos.csv")
    return pd.DataFrame(columns=["nome", "preco", "imagens", "categoria", "descricao"])

# --- BARRA LATERAL (IDENTIDADE VISUAL) ---
# Aqui você sobe sua logo no GitHub e troca o nome do arquivo abaixo
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)
else:
    st.sidebar.title("ADRIANO DESIGNER")

st.sidebar.markdown("---")
pagina = st.sidebar.radio("NAVEGAÇÃO", ["🔥 Vitrine de Lançamentos", "🛠️ Painel Interno"])

# --- VITRINE ---
if pagina == "🔥 Vitrine de Lançamentos":
    st.title("PROJETOS EXCLUSIVOS")
    df = carregar_dados()
    
    if df.empty:
        st.info("Preparando nova coleção...")
    else:
        categorias = ["Todas as Peças"] + sorted(df["categoria"].unique().tolist())
        cat_selecionada = st.sidebar.selectbox("Filtrar por Estilo", categorias)
        
        df_exibicao = df if cat_selecionada == "Todas as Peças" else df[df["categoria"] == cat_selecionada]

        cols = st.columns(3)
        for index, row in df_exibicao.reset_index().iterrows():
            with cols[index % 3]:
                lista_fotos = str(row['imagens']).split(",")
                
                # Exibição de Imagem com borda arredondada
                if os.path.exists(f"images/{lista_fotos[0]}"):
                    st.image(f"images/{lista_fotos[0]}", use_container_width=True)
                
                st.markdown(f"#### {row['nome']}")
                st.caption(f"✨ {row['categoria']}")
                
                with st.expander("Ver Detalhes"):
                    st.write(row['descricao'])
                    if len(lista_fotos) > 1:
                        for img in lista_fotos[1:]:
                            if os.path.exists(f"images/{img}"):
                                st.image(f"images/{img}", use_container_width=True)
                
                if row['preco'] > 0:
                    st.markdown(f"<h3 style='color: #25D366;'>R$ {row['preco']:.2f}</h3>", unsafe_allow_html=True)
                else:
                    st.markdown("<h3 style='color: #25D366;'>CONSULTAR VALOR</h3>", unsafe_allow_html=True)

                # Link WhatsApp com seu número
                meu_whats = "5585999999999" # ALTERAR PARA O SEU
                link_zap = f"https://wa.me/{meu_whats}?text=Quero%20saber%20mais%20sobre%20{row['nome']}"
                st.link_button("🚀 ENCOMENDAR AGORA", link_zap)

# --- ADMIN ---
elif pagina == "🛠️ Painel Interno":
    st.title("GESTÃO DE CATÁLOGO")
    senha = st.text_input("Senha", type="password")
    if senha == "suasenha123":
        with st.form("form_admin", clear_on_submit=True):
            nome = st.text_input("Nome do Modelo")
            descricao = st.text_area("Descrição Técnica (Tecido, Estampa, etc)")
            p, c = st.columns(2)
            preco = p.number_input("Preço Unitário", min_value=0.0)
            categoria = c.selectbox("Nicho", ["Futebol", "Geek", "Religiosa", "Corporativa", "Outros"])
            fotos = st.file_uploader("Subir Mockups", accept_multiple_files=True)
            
            if st.form_submit_button("PUBLICAR NO SITE"):
                if fotos:
                    nomes = []
                    for f in fotos:
                        n = f.name.replace(" ", "_")
                        with open(os.path.join("images", n), "wb") as arq:
                            arq.write(f.getbuffer())
                        nomes.append(n)
                    
                    df = carregar_dados()
                    novo = pd.DataFrame([{"nome": nome, "preco": preco, "imagens": ",".join(nomes), "categoria": categoria, "descricao": descricao}])
                    df = pd.concat([df, novo], ignore_index=True)
                    df.to_csv("produtos.csv", index=False)
                    st.success("Lançamento cadastrado!")
                    st.rerun()
