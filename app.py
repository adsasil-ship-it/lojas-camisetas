import streamlit as st
import pandas as pd
import os
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="Adriano Designer - Catálogo", layout="wide")

# 2. DESIGN CSS PERSONALIZADO
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;800&display=swap');
    
    .stApp { background-color: #f4f4f6; }

    .header-container { text-align: left; margin-bottom: 30px; }
    .subtitulo-loja {
        font-family: 'Inter', sans-serif;
        font-weight: 300;
        font-size: 14px;
        letter-spacing: 4px;
        color: #7a7a7a;
        text-transform: uppercase;
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
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }

    .nome-produto {
        color: #1a1c23;
        font-size: 18px;
        font-weight: 700;
        margin-top: 10px;
        display: block;
    }

    .preco-estilo {
        color: #1a1c23;
        font-weight: 800;
        font-size: 22px;
        margin: 10px 0;
    }
    
    .badge-novidade {
        background: #25D366;
        color: white;
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 10px;
        font-weight: bold;
        margin-bottom: 10px;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CONEXÃO COM GOOGLE SHEETS
def inicializar_dados():
    conn = st.connection("gsheets", type=GSheetsConnection)
    try:
        # ttl=0 garante que ele não use cache e pegue os dados novos
        df = conn.read(ttl=0)
        df = df.dropna(how="all") # Remove linhas vazias
        return df, conn
    except:
        # Caso a planilha esteja vazia ou com erro, cria estrutura básica
        colunas = ["nome", "preco", "imagens", "categoria", "subcategoria", "descricao"]
        return pd.DataFrame(columns=colunas), conn

# Inicializa pastas e dados
if not os.path.exists("images"): os.makedirs("images")
df, conn = inicializar_dados()

# --- CABEÇALHO ---
st.markdown("""
    <div class="header-container">
        <span class="subtitulo-loja">Catálogo Online</span>
        <h1 class="titulo-principal">ADRIANO <span class="destaque-verde">DESIGNER</span></h1>
    </div>
    <hr style='border: 0.5px solid #e0e0e0;'>
""", unsafe_allow_html=True)

# --- NAVEGAÇÃO LATERAL ---
pagina = st.sidebar.radio("Navegação", ["🛍️ Vitrine", "⚙️ Painel Admin"])

# --- PÁGINA 1: VITRINE ---
if pagina == "🛍️ Vitrine":
    if not df.empty:
        # Filtros
        categorias = ["Todos"] + sorted(df["categoria"].unique().astype(str).tolist())
        escolha_cat = st.sidebar.selectbox("Filtrar por Categoria", categorias)
        
        df_view = df if escolha_cat == "Todos" else df[df["categoria"] == escolha_cat]
        df_view = df_view.iloc[::-1] # Mostrar os últimos cadastrados primeiro

        cols = st.columns(3)
        for i, (idx, row) in enumerate(df_view.iterrows()):
            with cols[i % 3]:
                # Badge de Novidade (se for um dos últimos 3 itens)
                if i < 3:
                    st.markdown('<div class="badge-novidade">NOVIDADE</div>', unsafe_allow_html=True)
                
                # Exibição da Imagem
                fotos = str(row['imagens']).split(",")
                if fotos and os.path.exists(f"images/{fotos[0]}"):
                    st.image(f"images/{fotos[0]}", use_container_width=True)
                else:
                    st.info("Imagem não encontrada")

                st.markdown(f'<span class="nome-produto">{row["nome"]}</span>', unsafe_allow_html=True)
                st.write(f"_{row['categoria']} | {row['subcategoria']}_")
                
                preco_texto = f"R$ {row['preco']:.2f}" if float(row['preco']) > 0 else "Sob Consulta"
                st.markdown(f'<p class="preco-estilo">{preco_texto}</p>', unsafe_allow_html=True)
                
                with st.expander("Detalhes"):
                    st.write(row['descricao'])
                
                link_zap = f"https://wa.me/5585998351874?text=Olá Adriano! Tenho interesse no produto: {row['nome']}"
                st.link_button("SOLICITAR NO WHATSAPP", link_zap)
    else:
        st.info("Nenhum produto cadastrado no momento.")

# --- PÁGINA 2: PAINEL ADMIN ---
elif pagina == "⚙️ Painel Admin":
    st.subheader("🛠️ Gestão de Produtos (Nuvem)")
    senha = st.text_input("Senha de Acesso", type="password")
    
    if senha == "suasenha123": # Altere para sua senha de preferência
        tab1, tab2, tab3 = st.tabs(["➕ Adicionar", "📝 Editar", "🗑️ Excluir"])

        # ABA ADICIONAR
        with tab1:
            with st.form("form_add", clear_on_submit=True):
                nome = st.text_input("Nome do Produto")
                col1, col2 = st.columns(2)
                cat = col1.text_input("Categoria")
                sub = col2.text_input("Subcategoria")
                preco = st.number_input("Preço", min_value=0.0, format="%.2f")
                desc = st.text_area("Descrição (ex: 100% Algodão Premium)")
                fotos = st.file_uploader("Fotos do Produto", accept_multiple_files=True)
                
                if st.form_submit_button("PUBLICAR PRODUTO"):
                    if nome and fotos:
                        nomes_fotos = []
                        for foto in fotos:
                            arquivo_nome = f"{datetime.now().timestamp()}_{foto.name}".replace(" ","_")
                            with open(f"images/{arquivo_nome}", "wb") as f_arq:
                                f_arq.write(foto.getbuffer())
                            nomes_fotos.append(arquivo_nome)
                        
                        # Criar novo item
                        novo_item = pd.DataFrame([{
                            "nome": nome,
                            "preco": preco,
                            "imagens": ",".join(nomes_fotos),
                            "categoria": cat,
                            "subcategoria": sub,
                            "descricao": desc
                        }])
                        
                        # Atualizar DataFrame e salvar no Google Sheets
                        df_final = pd.concat([df, novo_item], ignore_index=True)
                        conn.update(data=df_final)
                        st.success("✅ Produto salvo no Google Sheets!")
                        st.rerun()
                    else:
                        st.error("Preencha o nome e envie ao menos uma foto.")

        # ABA EDITAR
        with tab2:
            if not df.empty:
                prod_edit = st.selectbox("Selecione para editar", df["nome"].tolist())
                idx_edit = df[df["nome"] == prod_edit].index[0]
                
                with st.form("form_edit"):
                    e_nome = st.text_input("Nome", value=df.at[idx_edit, 'nome'])
                    e_preco = st.number_input("Preço", value=float(df.at[idx_edit, 'preco']))
                    e_desc = st.text_area("Descrição", value=df.at[idx_edit, 'descricao'])
                    
                    if st.form_submit_button("SALVAR ALTERAÇÕES"):
                        df.at[idx_edit, 'nome'] = e_nome
                        df.at[idx_edit, 'preco'] = e_preco
                        df.at[idx_edit, 'descricao'] = e_desc
                        conn.update(data=df)
                        st.success("Atualizado!")
                        st.rerun()

        # ABA EXCLUIR
        with tab3:
            if not df.empty:
                for i, row in df.iterrows():
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"🗑️ {row['nome']}")
                    if c2.button("Remover", key=f"del_{i}"):
                        df_novo = df.drop(i)
                        conn.update(data=df_novo)
                        st.warning("Produto removido!")
                        st.rerun()
    else:
        if senha != "": st.error("Senha incorreta")
