import streamlit as st
import pandas as pd
import os

# Configurações de Design Moderno
st.set_page_config(page_title="Adriano Designer | Studio", layout="wide")

# CSS para melhorar a estética dos cards
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #000; color: white; }
    .stTextInput>div>div>input { border-radius: 5px; }
    div[data-testid="column"] {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

if not os.path.exists("images"):
    os.makedirs("images")

def carregar_dados():
    if os.path.exists("produtos.csv"):
        df = pd.read_csv("produtos.csv")
        if "categoria" not in df.columns: df["categoria"] = "Geral"
        return df
    return pd.DataFrame(columns=["nome", "preco", "imagens", "categoria"])

# --- NAVEGAÇÃO ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3050/3050222.png", width=100) # Ícone decorativo
pagina = st.sidebar.radio("MENU", ["🛍️ Vitrine Premium", "⚙️ Painel de Controle"])

# --- VITRINE ---
if pagina == "🛍️ Vitrine Premium":
    st.title("✨ Galeria de Conceitos")
    df = carregar_dados()
    
    if df.empty:
        st.info("Aguardando novas coleções...")
    else:
        categorias = ["Todas"] + sorted(df["categoria"].unique().tolist())
        cat_selecionada = st.sidebar.selectbox("Filtrar Coleção", categorias)
        
        df_exibicao = df if cat_selecionada == "Todas" else df[df["categoria"] == cat_selecionada]

        cols = st.columns(3)
        for index, row in df_exibicao.reset_index().iterrows():
            with cols[index % 3]:
                # Lógica para Múltiplas Imagens
                lista_fotos = str(row['imagens']).split(",")
                
                # Container de Imagem com Carrossel Simples (Expansor)
                if os.path.exists(f"images/{lista_fotos[0]}"):
                    st.image(f"images/{lista_fotos[0]}", use_container_width=True)
                    
                    if len(lista_fotos) > 1:
                        with st.expander("👁️ Ver mais ângulos"):
                            for img_adicional in lista_fotos[1:]:
                                if os.path.exists(f"images/{img_adicional}"):
                                    st.image(f"images/{img_adicional}", use_container_width=True)
                else:
                    st.error("Imagem principal não encontrada")

                st.markdown(f"### {row['nome']}")
                st.markdown(f"**{row['categoria']}**")
                st.markdown(f"<h2 style='color: #2e7d32;'>R$ {row['preco']}</h2>", unsafe_allow_html=True)
                
                msg = f"Olá Adriano! Gostaria de detalhes sobre: {row['nome']}"
                st.link_button("💬 Consultar Disponibilidade", f"https://wa.me/SEUNUMERO?text={msg.replace(' ', '%20')}")

# --- ADMIN ---
elif pagina == "⚙️ Painel de Controle":
    st.title("🛠️ Gestão de Ativos")
    
    senha = st.text_input("Chave de Acesso", type="password")
    if senha == "suasenha123":
        with st.form("admin_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            nome = col1.text_input("Nome do Produto")
            preco = col2.number_input("Preço", min_value=0.0)
            
            cat_fixa = st.selectbox("Categoria", ["Futebol", "Religiosa", "Business", "Streetwear"])
            nova_cat = st.text_input("Ou crie uma nova categoria")
            
            # MULTI-UPLOAD
            fotos = st.file_uploader("Selecione as fotos (Múltiplas)", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
            
            if st.form_submit_button("Publicar Produto"):
                if fotos:
                    nomes_arquivos = []
                    for foto in fotos:
                        nome_clean = foto.name.replace(" ", "_")
                        with open(os.path.join("images", nome_clean), "wb") as f:
                            f.write(foto.getbuffer())
                        nomes_arquivos.append(nome_clean)
                    
                    # Salva nomes separados por vírgula
                    string_fotos = ",".join(nomes_arquivos)
                    cat_final = nova_cat if nova_cat else cat_fixa
                    
                    df = carregar_dados()
                    novo_item = pd.DataFrame([{"nome": nome, "preco": preco, "imagens": string_fotos, "categoria": cat_final}])
                    df = pd.concat([df, novo_item], ignore_index=True)
                    df.to_csv("produtos.csv", index=False)
                    st.success("Produto publicado com sucesso!")
                    st.rerun()
