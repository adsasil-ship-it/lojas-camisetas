import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA E DESIGN
st.set_page_config(page_title="Adriano Designer | Catálogo", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;800&display=swap');
    
    .stApp { background-color: #f8f9fa; }
    
    /* CABEÇALHO */
    .header-container { text-align: left; margin-bottom: 20px; }
    .subtitulo {
        font-family: 'Inter', sans-serif;
        font-weight: 300;
        font-size: 12px;
        letter-spacing: 3px;
        color: #6c757d;
        text-transform: uppercase;
    }
    .titulo-principal {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 40px;
        color: #1a1c23;
        margin-top: -10px;
    }
    .destaque-verde { color: #25D366; }

    /* ESTILO DOS CARDS */
    .card-produto {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .nome-prod { font-weight: 700; font-size: 18px; color: #343a40; margin-top: 10px; }
    .preco-prod { font-weight: 800; font-size: 22px; color: #212529; margin: 5px 0; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÕES DE DADOS (CSV LOCAL)
def carregar_dados():
    caminho = "produtos.csv"
    if os.path.exists(caminho):
        try:
            return pd.read_csv(caminho)
        except:
            pass
    return pd.DataFrame(columns=["nome", "preco", "imagens", "categoria", "descricao"])

# Inicialização
if not os.path.exists("images"): os.makedirs("images")
df = carregar_dados()

# --- CABEÇALHO ---
st.markdown("""
    <div class="header-container">
        <span class="subtitulo">Premium Collection</span>
        <h1 class="titulo-principal">ADRIANO <span class="destaque-verde">DESIGNER</span></h1>
    </div>
""", unsafe_allow_html=True)

# --- MENU LATERAL ---
pagina = st.sidebar.radio("Navegar", ["🛍️ Vitrine", "⚙️ Painel Admin"])

# --- PÁGINA 1: VITRINE ---
if pagina == "🛍️ Vitrine":
    if df.empty:
        st.info("O catálogo está vazio no momento.")
    else:
        # Filtro simples
        categorias = ["Todos"] + sorted(df["categoria"].unique().astype(str).tolist())
        cat_selecionada = st.sidebar.selectbox("Filtrar Categoria", categorias)
        
        df_view = df if cat_selecionada == "Todos" else df[df["categoria"] == cat_selecionada]
        
        cols = st.columns(3)
        for i, (idx, row) in enumerate(df_view.iterrows()):
            with cols[i % 3]:
                st.markdown('<div class="card-produto">', unsafe_allow_html=True)
                
                # Imagem
                foto = str(row['imagens'])
                if os.path.exists(f"images/{foto}"):
                    st.image(f"images/{foto}", use_container_width=True)
                else:
                    st.warning("Sem imagem")
                
                st.markdown(f'<div class="nome-prod">{row["nome"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="preco-prod">R$ {float(row["preco"]):.2f}</div>', unsafe_allow_html=True)
                
                link_zap = f"https://wa.me/5585998351874?text=Olá Adriano! Gostaria de saber mais sobre: {row['nome']}"
                st.link_button("COMPRAR AGORA", link_zap)
                st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA 2: ADMIN ---
else:
    st.subheader("⚙️ Área Administrativa")
    senha = st.text_input("Senha", type="password")
    
    if senha == "suasenha123": # Troque para sua senha
        tab1, tab2, tab3 = st.tabs(["➕ Adicionar", "🗑️ Gerenciar", "💾 Backup e Restauro"])
        
        with tab1:
            with st.form("novo_produto"):
                nome = st.text_input("Nome do Produto")
                preco = st.number_input("Preço", min_value=0.0, format="%.2f")
                cat = st.text_input("Categoria (ex: Camisetas)")
                desc = st.text_area("Descrição (Tecido, Tamanhos...)")
                foto = st.file_uploader("Foto Principal", type=['jpg', 'png', 'jpeg'])
                
                if st.form_submit_button("PUBLICAR NO SITE"):
                    if nome and foto:
                        nome_arquivo = f"{datetime.now().timestamp()}_{foto.name}".replace(" ", "_")
                        with open(f"images/{nome_arquivo}", "wb") as f:
                            f.write(foto.getbuffer())
                        
                        novo_df = pd.DataFrame([{
                            "nome": nome, "preco": preco, 
                            "imagens": nome_arquivo, "categoria": cat, "descricao": desc
                        }])
                        
                        df = pd.concat([df, novo_df], ignore_index=True)
                        df.to_csv("produtos.csv", index=False)
                        st.success("Produto adicionado!")
                        st.rerun()
                    else:
                        st.error("Preencha o nome e selecione uma imagem.")

        with tab2:
            if not df.empty:
                for i, row in df.iterrows():
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"**{row['nome']}** - R$ {row['preco']:.2f}")
                    if c2.button("Excluir", key=f"del_{i}"):
                        df = df.drop(i)
                        df.to_csv("produtos.csv", index=False)
                        st.rerun()

        with tab3:
            st.markdown("### 📥 Backup")
            st.write("Baixe seu catálogo para garantir que não perderá os dados se o servidor resetar.")
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button("BAIXAR BANCO DE DADOS (CSV)", csv_data, "meu_catalogo_backup.csv", "text/csv")
            
            st.divider()
            
            st.markdown("### 📤 Restauração")
            st.write("Se os produtos sumirem, suba o arquivo de backup aqui.")
            arquivo_up = st.file_uploader("Subir arquivo CSV", type="csv")
            if st.button("RESTAURAR SITE AGORA") and arquivo_up:
                df_restaurado = pd.read_csv(arquivo_up)
                df_restaurado.to_csv("produtos.csv", index=False)
                st.success("Catálogo restaurado com sucesso!")
                st.rerun()
    else:
        if senha: st.error("Senha incorreta.")
