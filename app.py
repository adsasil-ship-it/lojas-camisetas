import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO E DESIGN
st.set_page_config(page_title="Adriano Designer | Loja Oficial", layout="wide")

# CSS PERSONALIZADO
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;700&display=swap');
    
    .stApp { background-color: #f8f9fa; }
    
    .header-container { text-align: center; padding: 20px; }
    
    .loja-online-do {
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        letter-spacing: 2px;
        color: #666;
        margin-bottom: -10px;
    }
    
    .titulo-principal { 
        font-family: 'Bebas Neue', sans-serif; 
        font-size: 65px; 
        color: #1a1c23; 
        line-height: 1;
        margin-bottom: 5px;
    }
    
    .destaque-verde { color: #25D366; }
    
    .slogan {
        font-family: 'Inter', sans-serif;
        font-size: 16px;
        color: #444;
        font-weight: 300;
        margin-top: -5px;
        font-style: italic;
    }

    .card-produto { 
        background-color: #ffffff; border: 1px solid #e9ecef; padding: 15px; 
        border-radius: 15px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        position: relative; height: 100%;
    }
    .badge-novidade {
        background-color: #25D366; color: white; padding: 5px 12px;
        border-radius: 50px; font-size: 10px; font-weight: bold;
        position: absolute; top: 10px; left: 10px; z-index: 10;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÕES DE DADOS
def carregar_dados():
    caminho = "produtos.csv"
    colunas = ["nome", "preco", "imagens", "categoria", "subcategoria", "descricao", "novidade"]
    if os.path.exists(caminho):
        try:
            df = pd.read_csv(caminho)
            for col in colunas:
                if col not in df.columns: 
                    df[col] = False if col == "novidade" else ""
            return df
        except: pass
    return pd.DataFrame(columns=colunas)

def carregar_categorias():
    caminho = "categorias.csv"
    if os.path.exists(caminho):
        return pd.read_csv(caminho)
    return pd.DataFrame(columns=["categoria", "subcategoria"])

if not os.path.exists("images"): os.makedirs("images")
df = carregar_dados()
df_cats = carregar_categorias()

# --- CABEÇALHO COM LOGO E SLOGAN ---
col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])

with col_logo2:
    # Espaço para sua LOGO (Certifique-se de ter um arquivo logo.png na pasta do script)
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    
    st.markdown(f"""
        <div class="header-container">
            <p class="loja-online-do">LOJA ONLINE DO:</p>
            <h1 class="titulo-principal">ADRIANO <span class="destaque-verde">DESIGNER</span></h1>
            <p class="slogan">Estilo que respira, conforto que veste. O melhor do algodão premium.</p>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# --- MENU LATERAL ---
menu_principal = st.sidebar.radio("Navegar", ["🛍️ Vitrine", "⚙️ Painel Admin"])

# --- VITRINE ---
if menu_principal == "🛍️ Vitrine":
    if df.empty:
        st.info("Nenhum produto cadastrado.")
    else:
        st.sidebar.subheader("📂 Filtros")
        lista_cats = ["Todos os Produtos"] + sorted(df["categoria"].unique().astype(str).tolist())
        cat_sel = st.sidebar.selectbox("Escolha uma Categoria", lista_cats)
        
        df_f = df if cat_sel == "Todos os Produtos" else df[df["categoria"] == cat_sel]
        
        lista_subs = ["Todas as Subcategorias"] + sorted(df_f["subcategoria"].unique().astype(str).tolist())
        sub_sel = st.sidebar.selectbox("Refinar por Subcategoria", lista_subs)
        if sub_sel != "Todas as Subcategorias": 
            df_f = df_f[df_f["subcategoria"] == sub_sel]

        df_f['novidade'] = df_f['novidade'].fillna(False).astype(bool)
        df_exibir = df_f.sort_values(by=['novidade', 'nome'], ascending=[False, True])

        cols = st.columns(3)
        for i, (idx, row) in enumerate(df_exibir.iterrows()):
            with cols[i % 3]:
                st.markdown('<div class="card-produto">', unsafe_allow_html=True)
                if row['novidade']:
                    st.markdown('<div class="badge-novidade">LANÇAMENTO</div>', unsafe_allow_html=True)
                if os.path.exists(f"images/{row['imagens']}"):
                    st.image(f"images/{row['imagens']}", use_container_width=True)
                st.write(f"**{row['nome']}**")
                st.caption(f"{row['categoria']} | {row['subcategoria']}")
                st.write(f"### R$ {float(row['preco']):.2f}")
                st.link_button("WHATSAPP", f"https://wa.me/5585998351874?text=Olá Adriano! Quero saber sobre: {row['nome']}")
                st.markdown('</div>', unsafe_allow_html=True)

# --- ADMIN ---
else:
    senha = st.text_input("Senha Admin", type="password")
    if senha == "suasenha123":
        t1, t_cat, t2, t3, t4 = st.tabs(["➕ Novo Produto", "📂 Categorias", "📝 Editar", "🗑️ Remover", "💾 Backup"])
        
        with t_cat:
            st.write("### 📂 Configurar Categorias")
            with st.form("form_categorias"):
                c1, c2 = st.columns(2)
                nova_cat = c1.text_input("Nome da Categoria")
                nova_sub = c2.text_input("Nome da Subcategoria")
                if st.form_submit_button("ADICIONAR À LISTA"):
                    if nova_cat and nova_sub:
                        nova_linha = pd.DataFrame([{"categoria": nova_cat, "subcategoria": nova_sub}])
                        df_cats = pd.concat([df_cats, nova_linha], ignore_index=True).drop_duplicates()
                        df_cats.to_csv("categorias.csv", index=False)
                        st.success("Salvo!")
                        st.rerun()
            
            st.dataframe(df_cats, use_container_width=True)
            if st.button("Apagar todas as Categorias"):
                if os.path.exists("categorias.csv"): os.remove("categorias.csv")
                st.rerun()

        with t1:
            if df_cats.empty:
                st.warning("Cadastre categorias primeiro!")
            else:
                with st.form("form_novo_v7", clear_on_submit=True):
                    nome = st.text_input("Nome do Produto")
                    preco = st.number_input("Preço", min_value=0.0)
                    c1, c2 = st.columns(2)
                    sel_cat = c1.selectbox("Categoria:", df_cats["categoria"].unique())
                    sel_sub = c2.selectbox("Subcategoria:", df_cats[df_cats["categoria"] == sel_cat]["subcategoria"])
                    destaque = st.checkbox("Destaque Novidade")
                    desc = st.text_area("Descrição")
                    foto = st.file_uploader("Foto", type=['jpg', 'png', 'jpeg'])
                    if st.form_submit_button("CADASTRAR PRODUTO"):
                        if nome and foto:
                            nome_arq = f"{datetime.now().timestamp()}_{foto.name}".replace(" ","_")
                            with open(f"images/{nome_arq}", "wb") as f:
                                f.write(foto.getbuffer())
                            novo = pd.DataFrame([{"nome": nome, "preco": preco, "imagens": nome_arq, 
                                                 "categoria": sel_cat, "subcategoria": sel_sub, 
                                                 "descricao": desc, "novidade": destaque}])
                            df = pd.concat([df, novo], ignore_index=True)
                            df.to_csv("produtos.csv", index=False)
                            st.rerun()

        with t2: # EDITAR
            if not df.empty:
                escolha = st.selectbox("Produto para editar:", df["nome"].tolist())
                idx = df[df["nome"] == escolha].index[0]
                with st.form("form_edit_v7"):
                    enome = st.text_input("Nome", value=df.at[idx, 'nome'])
                    epreco = st.number_input("Preço", value=float(df.at[idx, 'preco']))
                    cats_disponiveis = df_cats["categoria"].unique().tolist() if not df_cats.empty else [df.at[idx, 'categoria']]
                    ecat = st.selectbox("Categoria:", cats_disponiveis)
                    subs_disponiveis = df_cats[df_cats["categoria"] == ecat]["subcategoria"].tolist() if not df_cats.empty else [df.at[idx, 'subcategoria']]
                    esub = st.selectbox("Subcategoria:", subs_disponiveis)
                    edestaque = st.checkbox("Novidade", value=bool(df.at[idx, 'novidade']))
                    edesc = st.text_area("Descrição", value=str(df.at[idx, 'descricao']))
                    if st.form_submit_button("SALVAR"):
                        df.at[idx, 'nome'], df.at[idx, 'preco'] = enome, epreco
                        df.at[idx, 'categoria'], df.at[idx, 'subcategoria'] = ecat, esub
                        df.at[idx, 'novidade'], df.at[idx, 'descricao'] = edestaque, edesc
                        df.to_csv("produtos.csv", index=False)
                        st.rerun()

        with t3: # REMOVER
            for i, row in df.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{row['nome']}**")
                if c2.button("Excluir", key=f"del_{i}"):
                    df = df.drop(i)
                    df.to_csv("produtos.csv", index=False)
                    st.rerun()

        with t4: # BACKUP
            st.download_button("📥 BAIXAR BACKUP", df.to_csv(index=False), "produtos.csv")
