import streamlit as st
import pandas as pd
import os

# Configurações de Design
st.set_page_config(page_title="Adriano Designer | Catálogo", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #25D366; color: white; font-weight: bold; }
    div[data-testid="column"] {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

if not os.path.exists("images"):
    os.makedirs("images")

def carregar_dados():
    if os.path.exists("produtos.csv"):
        df = pd.read_csv("produtos.csv")
        # Garante que as novas colunas existam
        if "descricao" not in df.columns: df["descricao"] = ""
        if "categoria" not in df.columns: df["categoria"] = "Geral"
        return df
    return pd.DataFrame(columns=["nome", "preco", "imagens", "categoria", "descricao"])

# --- NAVEGAÇÃO ---
pagina = st.sidebar.radio("MENU", ["🛍️ Vitrine de Produtos", "⚙️ Painel Admin"])

# --- VITRINE ---
if pagina == "🛍️ Vitrine de Produtos":
    st.title("👕 Catálogo de Coleções")
    df = carregar_dados()
    
    if df.empty:
        st.info("Nenhum item cadastrado.")
    else:
        categorias = ["Todas"] + sorted(df["categoria"].unique().tolist())
        cat_selecionada = st.sidebar.selectbox("Filtrar Categoria", categorias)
        
        df_exibicao = df if cat_selecionada == "Todas" else df[df["categoria"] == cat_selecionada]

        cols = st.columns(3)
        for index, row in df_exibicao.reset_index().iterrows():
            with cols[index % 3]:
                lista_fotos = str(row['imagens']).split(",")
                
                # Exibição da Imagem Principal
                if os.path.exists(f"images/{lista_fotos[0]}"):
                    st.image(f"images/{lista_fotos[0]}", use_container_width=True)
                
                st.subheader(row['nome'])
                st.caption(f"📁 {row['categoria']}")
                
                # Exibição da Descrição
                if row['descricao']:
                    st.write(row['descricao'])
                
                # Lógica de Preço ou Consulta
                if row['preco'] > 0:
                    st.markdown(f"### R$ {row['preco']:.2f}")
                    txt_zap = f"Olá! Tenho interesse na {row['nome']}."
                else:
                    st.markdown("### 📞 Valor sob Consulta")
                    txt_zap = f"Olá Adriano! Gostaria de um orçamento para a {row['nome']}."

                # Link do WhatsApp (Troque pelo seu número com DDD)
                meu_whats = "5585999999999" # COLOQUE SEU NÚMERO AQUI
                link_whatsapp = f"https://wa.me/{meu_whats}?text={txt_zap.replace(' ', '%20')}"
                st.link_button("Solicitar Orçamento", link_whatsapp)
                
                if len(lista_fotos) > 1:
                    with st.expander("Ver mais fotos"):
                        for img in lista_fotos[1:]:
                            if os.path.exists(f"images/{img}"):
                                st.image(f"images/{img}", use_container_width=True)

# --- ADMIN ---
elif pagina == "⚙️ Painel Admin":
    st.title("🛠️ Cadastrar Novo Item")
    
    senha = st.text_input("Senha", type="password")
    if senha == "suasenha123":
        with st.form("form_cadastro", clear_on_submit=True):
            nome = st.text_input("Nome do Produto")
            descricao = st.text_area("Descrição do Produto (Detalhes da malha, estampa, etc.)")
            
            col_p, col_c = st.columns(2)
            preco = col_p.number_input("Preço (Deixe 0 para 'Sob Consulta')", min_value=0.0)
            categoria = col_c.selectbox("Categoria", ["Futebol", "Religiosa", "Empresarial", "Outros"])
            
            fotos = st.file_uploader("Fotos do Produto", accept_multiple_files=True)
            
            if st.form_submit_button("Salvar no Catálogo"):
                if fotos:
                    nomes_fotos = []
                    for f in fotos:
                        n = f.name.replace(" ", "_")
                        with open(os.path.join("images", n), "wb") as arq:
                            arq.write(f.getbuffer())
                        nomes_fotos.append(n)
                    
                    df = carregar_dados()
                    novo = pd.DataFrame([{
                        "nome": nome, 
                        "preco": preco, 
                        "imagens": ",".join(nomes_fotos), 
                        "categoria": categoria,
                        "descricao": descricao
                    }])
                    df = pd.concat([df, novo], ignore_index=True)
                    df.to_csv("produtos.csv", index=False)
                    st.success("Produto cadastrado!")
                    st.rerun()
