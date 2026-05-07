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

    /* Estilização dos Cards de Produto */
    div[data-testid="column"] {
        background-color: #1a1c23;
        border: 1px solid #333;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        margin-bottom: 30px;
    }

    /* Botão estilo 'Call to Action' */
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
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(37, 211, 102, 0.4);
    }

    h1, h2, h3, h4 { color: #ffffff !important; }
    p, span { color: #cfcfcf !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÃO DE DADOS BLINDADA (Evita KeyError)
def carregar_dados():
    colunas_obrigatorias = ["nome", "preco", "imagens", "categoria", "descricao"]
    caminho_csv = "produtos.csv"
    
    if os.path.exists(caminho_csv):
        try:
            df = pd.read_csv(caminho_csv)
            # Verifica se alguma coluna está faltando e adiciona
            for col in colunas_obrigatorias:
                if col not in df.columns:
                    df[col] = "Não informado" if col != "preco" else 0.0
            return df
        except:
            return pd.DataFrame(columns=colunas_obrigatorias)
    return pd.DataFrame(columns=colunas_obrigatorias)

# Criar pasta de imagens
if not os.path.exists("images"):
    os.makedirs("images")

# --- CABEÇALHO EM DESTAQUE ---
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    else:
        st.display_logo = st.markdown("## 🎨")

with col_titulo:
    st.markdown("""
        <h1 style='margin-bottom: 0px;'>ADRIANO <span style='color: #25D366;'>DESIGNER</span></h1>
        <p style='font-size: 20px; color: #a0a0a0; margin-top: -10px;'>Estúdio de Criação & Personalizados Premium</p>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- NAVEGAÇÃO LATERAL ---
st.sidebar.markdown("### 🧭 MENU")
pagina = st.sidebar.radio("Ir para:", ["🛍️ Vitrine Premium", "⚙️ Painel do Designer"])

# --- PÁGINA 1: VITRINE ---
if pagina == "🛍️ Vitrine Premium":
    df = carregar_dados()
    
    if df.empty:
        st.info("Aguardando o próximo lançamento oficial...")
    else:
        # Filtros Modernos
        st.sidebar.markdown("---")
        categorias = ["Todos os Estilos"] + sorted(df["categoria"].unique().tolist())
        cat_sel = st.sidebar.selectbox("Filtrar Coleção", categorias)
        
        df_view = df if cat_sel == "Todos os Estilos" else df[df["categoria"] == cat_sel]

        # Exibição em Grade (Grid)
        cols = st.columns(3)
        for index, row in df_view.reset_index().iterrows():
            with cols[index % 3]:
                fotos = str(row['imagens']).split(",")
                
                # Imagem Principal com borda suave
                if os.path.exists(f"images/{fotos[0]}"):
                    st.image(f"images/{fotos[0]}", use_container_width=True)
                
                st.markdown(f"### {row['nome']}")
                st.markdown(f"<span style='background-color: #333; padding: 4px 10px; border-radius: 5px; font-size: 12px;'>{row['categoria']}</span>", unsafe_allow_html=True)
                
                # Descrição e Expansor de Fotos
                with st.expander("🔍 Detalhes e + Fotos"):
                    st.write(row['descricao'])
                    if len(fotos) > 1:
                        for f in fotos[1:]:
                            if os.path.exists(f"images/{f}"):
                                st.image(f"images/{f}", use_container_width=True)
                
                # Lógica de Preço
                if row['preco'] > 0:
                    st.markdown(f"<h2 style='color: #25D366;'>R$ {row['preco']:.2f}</h2>", unsafe_allow_html=True)
                    msg_zap = f"Olá Adriano! Gostaria de encomendar a {row['nome']}."
                else:
                    st.markdown("<h2 style='color: #25D366;'>SOB CONSULTA</h2>", unsafe_allow_html=True)
                    msg_zap = f"Olá Adriano! Gostaria de um orçamento para o projeto: {row['nome']}."

                # Link WhatsApp (COLOQUE SEU NÚMERO ABAIXO)
                meu_whats = "5585998341874" 
                st.link_button("🚀 SOLICITAR VIA WHATSAPP", f"https://wa.me/{meu_whats}?text={msg_zap.replace(' ', '%20')}")

# --- PÁGINA 2: ADMIN ---
elif pagina == "⚙️ Painel do Designer":
    st.title("🛠️ Gerenciar Catálogo")
    senha = st.text_input("Senha de Acesso", type="password")
    
    if senha == "suasenha123":
        with st.form("cadastro_form", clear_on_submit=True):
            n = st.text_input("Nome do Lançamento")
            d = st.text_area("Descrição do Produto")
            c1, c2 = st.columns(2)
            p = c1.number_input("Preço (0 para consulta)", min_value=0.0)
            cat = c2.selectbox("Categoria", ["Futebol", "Religiosa", "Geek", "Corporativa", "Outros"])
            
            f = st.file_uploader("Fotos do Produto (Selecione todas de uma vez)", accept_multiple_files=True)
            
            if st.form_submit_button("PUBLICAR PRODUTO"):
                if f:
                    lista_nomes = []
                    for foto in f:
                        nome_f = foto.name.replace(" ", "_")
                        with open(os.path.join("images", nome_f), "wb") as arq:
                            arq.write(foto.getbuffer())
                        lista_nomes.append(nome_f)
                    
                    df_atual = carregar_dados()
                    novo = pd.DataFrame([{"nome": n, "preco": p, "imagens": ",".join(lista_nomes), "categoria": cat, "descricao": d}])
                    df_novo = pd.concat([df_atual, novo], ignore_index=True)
                    df_novo.to_csv("produtos.csv", index=False)
                    st.success("Produto adicionado com sucesso!")
                    st.rerun()
