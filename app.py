import streamlit as st
import pandas as pd
import os

# Configurações iniciais
st.set_page_config(page_title="Gestão de Loja - Camisetas", layout="wide")

# Criar pasta de imagens se não existir
if not os.path.exists("images"):
    os.makedirs("images")


# Função para carregar dados
def carregar_dados():
    if os.path.exists("produtos.csv"):
        return pd.read_csv("produtos.csv")
    return pd.DataFrame(columns=["nome", "preco", "imagem"])


# --- BARRA LATERAL (Navegação) ---
st.sidebar.title("Navegação")
pagina = st.sidebar.radio("Ir para:", ["Vitrine de Produtos", "Painel Admin"])

# --- PÁGINA 1: VITRINE (O que o cliente vê) ---
if pagina == "Vitrine de Produtos":
    st.title("👕 Nossa Coleção")
    df = carregar_dados()

    if df.empty:
        st.info("Nenhum produto cadastrado ainda.")
    else:
        cols = st.columns(3)
        for index, row in df.iterrows():
            with cols[index % 3]:
                st.image(f"images/{row['imagem']}", use_container_width=True)
                st.subheader(row['nome'])
                st.write(f"**Valor:** R$ {row['preco']}")
                # Link para seu WhatsApp
                st.link_button("Solicitar Orçamento",
                               f"https://wa.me/SEUNUMERO?text=Quero%20a%20camiseta%20{row['nome']}")

# --- PÁGINA 2: PAINEL ADMIN (Onde você gerencia) ---
elif pagina == "Painel Admin":
    st.title("🔐 Administração da Loja")

    # Autenticação Simples
    senha = st.text_input("Digite a senha de administrador", type="password")
    if senha == "suasenha123":  # Altere para sua senha de preferência
        st.success("Acesso liberado!")

        st.subheader("Adicionar Novo Produto")
        with st.form("novo_produto", clear_on_submit=True):
            nome = st.text_input("Nome da Camiseta")
            preco = st.number_input("Preço de Venda", min_value=0.0, format="%.2f")
            foto = st.file_uploader("Upload do Mockup (JPG/PNG)", type=["jpg", "png", "jpeg"])
            submit = st.form_submit_area = st.form_submit_button("Cadastrar Produto")

            if submit and foto is not None:
                # Salvar a imagem na pasta
                with open(os.path.join("images", foto.name), "wb") as f:
                    f.write(foto.getbuffer())

                # Salvar os dados no CSV
                df = carregar_dados()
                novo_item = pd.DataFrame([{"nome": nome, "preco": preco, "imagem": foto.name}])
                df = pd.concat([df, novo_item], ignore_index=True)
                df.to_csv("produtos.csv", index=False)
                st.success(f"Produto '{nome}' cadastrado com sucesso!")
                st.rerun()

        # Opção de Deletar
        st.subheader("Gerenciar Produtos Atuais")
        df_atual = carregar_dados()
        if not df_atual.empty:
            item_para_remover = st.selectbox("Selecione um produto para excluir", df_atual["nome"])
            if st.button("Excluir Produto"):
                df_atual = df_atual[df_atual["nome"] != item_para_remover]
                df_atual.to_csv("produtos.csv", index=False)
                st.warning(f"'{item_para_remover}' removido!")
                st.rerun()
    else:
        st.error("Senha incorreta.")