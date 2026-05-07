import streamlit as st
import pandas as pd
import os

# Configurações iniciais
st.set_page_config(page_title="Loja Adriano Designer", layout="wide")

# Criar pasta de imagens se não existir
if not os.path.exists("images"):
    os.makedirs("images")

# Função para carregar dados
def carregar_dados():
    if os.path.exists("produtos.csv"):
        df = pd.read_csv("produtos.csv")
        # Garante que a coluna categoria exista se você estiver atualizando o arquivo antigo
        if "categoria" not in df.columns:
            df["categoria"] = "Geral"
        return df
    return pd.DataFrame(columns=["nome", "preco", "imagem", "categoria"])

# --- BARRA LATERAL (Navegação) ---
st.sidebar.title("Navegação")
pagina = st.sidebar.radio("Ir para:", ["Vitrine de Produtos", "Painel Admin"])

# --- PÁGINA 1: VITRINE ---
if pagina == "Vitrine de Produtos":
    st.title("👕 Nossa Coleção")
    df = carregar_dados()
    
    if df.empty:
        st.info("Nenhum produto cadastrado ainda.")
    else:
        # --- SISTEMA DE CATEGORIAS ---
        categorias = ["Todos"] + sorted(df["categoria"].unique().tolist())
        cat_selecionada = st.sidebar.selectbox("Filtrar por Categoria:", categorias)

        # Filtrar o DataFrame
        if cat_selecionada != "Todos":
            df_exibicao = df[df["categoria"] == cat_selecionada]
        else:
            df_exibicao = df

        cols = st.columns(4) # 4 colunas para caber mais produtos
        for index, row in df_exibicao.reset_index().iterrows():
            with cols[index % 4]:
                # Tenta abrir a imagem, se não existir mostra um aviso
                caminho_img = f"images/{row['imagem']}"
                if os.path.exists(caminho_img):
                    st.image(caminho_img, use_container_width=True)
                else:
                    st.warning(f"Foto não encontrada: {row['imagem']}")
                
                st.subheader(row['nome'])
                st.caption(f"Categoria: {row['categoria']}")
                st.write(f"**Valor:** R$ {row['preco']}")
                
                msg = f"Olá Adriano! Tenho interesse na camiseta {row['nome']} (Cat: {row['categoria']})"
                st.link_button("Solicitar no WhatsApp", f"https://wa.me/SEUNUMERO?text={msg.replace(' ', '%20')}")

# --- PÁGINA 2: PAINEL ADMIN ---
elif pagina == "Painel Admin":
    st.title("🔐 Administração da Loja")
    
    senha = st.text_input("Digite a senha", type="password")
    if senha == "suasenha123":
        st.success("Acesso liberado!")
        
        st.subheader("Adicionar Novo Produto")
        with st.form("novo_produto", clear_on_submit=True):
            nome = st.text_input("Nome da Camiseta")
            preco = st.number_input("Preço de Venda", min_value=0.0, format="%.2f")
            
            # CAMPO DE CATEGORIA
            categoria = st.selectbox("Categoria", ["Futebol", "Religiosa", "Infantil", "Empresarial", "Personalizada", "Outros"])
            # Se quiser criar uma categoria nova na hora:
            nova_cat = st.text_input("Ou digite uma nova categoria (opcional)")
            
            foto = st.file_uploader("Upload do Mockup", type=["jpg", "png", "jpeg"])
            submit = st.form_submit_button("Cadastrar Produto")
            
            if submit and foto is not None:
                cat_final = nova_cat if nova_cat else categoria
                # Salvar a imagem
                nome_arquivo = foto.name.replace(" ", "_") # Remove espaços do nome do arquivo
                with open(os.path.join("images", nome_arquivo), "wb") as f:
                    f.write(foto.getbuffer())
                
                # Salvar os dados
                df = carregar_dados()
                novo_item = pd.DataFrame([{"nome": nome, "preco": preco, "imagem": nome_arquivo, "categoria": cat_final}])
                df = pd.concat([df, novo_item], ignore_index=True)
                df.to_csv("produtos.csv", index=False)
                st.success(f"Produto '{nome}' na categoria '{cat_final}' cadastrado!")
                st.rerun()

        # Botão para limpar o CSV se houver erro de imagem sumida
        if st.button("Limpar lista de produtos (CUIDADO)"):
            pd.DataFrame(columns=["nome", "preco", "imagem", "categoria"]).to_csv("produtos.csv", index=False)
            st.warning("Lista resetada!")
            st.rerun()
