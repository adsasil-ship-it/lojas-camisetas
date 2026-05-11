import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO E DESIGN
st.set_page_config(page_title="Adriano Designer | Loja Oficial", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;800&display=swap');
    .stApp { background-color: #f8f9fa; }
    .header-container { text-align: left; margin-bottom: 20px; }
    .titulo-principal { font-family: 'Inter', sans-serif; font-weight: 800; font-size: 40px; color: #1a1c23; }
    .destaque-verde { color: #25D366; }
    
    /* CARDS */
    .card-produto { 
        background-color: #ffffff; 
        border: 1px solid #e9ecef; 
        padding: 15px; 
        border-radius: 15px; 
        text-align: center; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        position: relative;
    }
    .badge-novidade {
        background-color: #25D366;
        color: white;
        padding: 5px 12px;
        border-radius: 50px;
        font-size: 10px;
        font-weight: bold;
        position: absolute;
        top: 10px;
        left: 10px;
        z-index: 10;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÕES DE DADOS
def carregar_dados():
    caminho = "produtos.csv"
    # Adicionamos a coluna 'novidade'
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

if not os.path.exists("images"): os.makedirs("images")
df = carregar_dados()

# --- CABEÇALHO ---
st.markdown('<div class="header-container"><h1 class="titulo-principal">ADRIANO <span class="destaque-verde">DESIGNER</span></h1></div>', unsafe_allow_html=True)

# --- MENU LATERAL DE FÁCIL ACESSO ---
st.sidebar.image("https://via.placeholder.com/150x50?text=AD+DESIGNER", use_container_width=True) # Coloque seu logo aqui
menu_principal = st.sidebar.radio("Navegar", ["🛍️ Vitrine", "⚙️ Painel Admin"])

# --- VITRINE ---
if menu_principal == "🛍️ Vitrine":
    if df.empty:
        st.info("Nenhum produto cadastrado.")
    else:
        st.sidebar.divider()
        st.sidebar.subheader("📂 Categorias")
        
        # Filtro de Categoria de Fácil Acesso
        lista_cats = ["Todos os Produtos"] + sorted(df["categoria"].unique().astype(str).tolist())
        cat_sel = st.sidebar.selectbox("O que você procura?", lista_cats)
        
        df_f = df if cat_sel == "Todos os Produtos" else df[df["categoria"] == cat_sel]
        
        # Filtro de Subcategoria
        lista_subs = ["Todas as Subcategorias"] + sorted(df_f["subcategoria"].unique().astype(str).tolist())
        sub_sel = st.sidebar.selectbox("Refinar busca", lista_subs)
        if sub_sel != "Todas as Subcategorias": 
            df_f = df_f[df_f["subcategoria"] == sub_sel]

        # ORDENAÇÃO: Novidades primeiro, depois por ID (mais recentes)
        df_f['novidade'] = df_f['novidade'].fillna(False).astype(bool)
        df_exibir = df_f.sort_values(by=['novidade', 'nome'], ascending=[False, True])

        cols = st.columns(3)
        for i, (idx, row) in enumerate(df_exibir.iterrows()):
            with cols[i % 3]:
                st.markdown('<div class="card-produto">', unsafe_allow_html=True)
                
                # Badge de Novidade
                if row['novidade']:
                    st.markdown('<div class="badge-novidade">LANÇAMENTO</div>', unsafe_allow_html=True)
                
                if os.path.exists(f"images/{row['imagens']}"):
                    st.image(f"images/{row['imagens']}", use_container_width=True)
                
                st.write(f"**{row['nome']}**")
                st.caption(f"{row['categoria']} | {row['subcategoria']}")
                st.write(f"### R$ {float(row['preco']):.2f}")
                
                st.link_button("ADQUIRIR NO WHATSAPP", f"https://wa.me/5585998351874?text=Olá! Quero saber sobre: {row['nome']}")
                st.markdown('</div>', unsafe_allow_html=True)

# --- ADMIN ---
else:
    senha = st.text_input("Senha Admin", type="password")
    if senha == "suasenha123":
        t1, t2, t3, t4 = st.tabs(["➕ Novo", "📝 Editar", "🗑️ Remover", "💾 Backup"])
        
        # LISTAS PARA FACILITAR CADASTRO
        exist_cats = sorted(df["categoria"].unique().astype(str).tolist()) if not df.empty else []
        exist_subs = sorted(df["subcategoria"].unique().astype(str).tolist()) if not df.empty else []

        with t1: # ADICIONAR
            with st.form("form_novo", clear_on_submit=True):
                st.write("### Novo Lançamento")
                nome = st.text_input("Nome do Produto")
                preco = st.number_input("Preço", min_value=0.0)
                
                c1, c2 = st.columns(2)
                cat_e = c1.selectbox("Categoria Existente", ["Nova..."] + exist_cats)
                cat_n = c1.text_input("Se nova, digite aqui:") if cat_e == "Nova..." else ""
                
                sub_e = c2.selectbox("Subcategoria Existente", ["Nova..."] + exist_subs)
                sub_n = c2.text_input("Se nova, digite aqui:") if sub_e == "Nova..." else ""
                
                destaque = st.checkbox("Marcar como NOVIDADE (aparece no topo)")
                
                desc = st.text_area("Descrição")
                foto = st.file_uploader("Foto Principal", type=['jpg', 'png', 'jpeg'])
                
                if st.form_submit_button("PUBLICAR"):
                    cat_final = cat_n if cat_e == "Nova..." else cat_e
                    sub_final = sub_n if sub_e == "Nova..." else sub_e
                    
                    if nome and foto:
                        nome_arq = f"{datetime.now().timestamp()}_{foto.name}".replace(" ","_")
                        with open(f"images/{nome_arq}", "wb") as f: f.write(foto.getbuffer())
                        
                        novo = pd.DataFrame([{"nome": nome, "preco": preco, "imagens": nome_arq, 
                                             "categoria": cat_final, "subcategoria": sub_final, 
                                             "descricao": desc, "novidade": destaque}])
                        df = pd.concat([df, novo], ignore_index=True)
                        df.to_csv("produtos.csv", index=False)
                        st.success("Produto Publicado!")
                        st.rerun()

        with t2: # EDITAR
            if not df.empty:
                st.write("### Editar Produto")
                escolha_edit = st.selectbox("Selecione o produto para alterar", df["nome"].tolist())
                idx = df[df["nome"] == escolha_edit].index[0]
                
                with st.form("form_edit"):
                    e_nome = st.text_input("Nome", value=df.at[idx, 'nome'])
                    e_preco = st.number_input("Preço", value=float(df.at[idx, 'preco']))
                    e_destaque = st.checkbox("Novidade", value=bool(df.at[idx, 'novidade']))
                    e_desc = st.text_area("Descrição", value=str(df.at[idx, 'descricao']))
                    
                    if st.form_submit_button("SALVAR ALTERAÇÕES"):
                        df.at[idx, 'nome'] = e_nome
                        df.at[idx, 'preco'] = e_preco
                        df.at[idx, 'novidade'] = e_destaque
                        df.at[idx, 'descricao'] = e_desc
                        df.to_csv("produtos.csv", index=False)
                        st.success("Alterado com sucesso!")
                        st.rerun()

        with t3: # REMOVER
            for i, row in df.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{row['nome']}** - {row['categoria']}")
                if c2.button("Excluir", key=f"del_{i}"):
                    df = df.drop(i)
                    df.to_csv("produtos.csv", index=False)
                    st.rerun()

        with t4: # BACKUP
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 BAIXAR BANCO DE DADOS", csv, "backup_catalogo.csv", "text/csv")
            st.divider()
            up = st.file_uploader("Restaurar via CSV", type="csv")
            if st.button("CONFIRMAR RESTAURAÇÃO") and up:
                pd.read_csv(up).to_csv("produtos.csv", index=False)
                st.rerun()
