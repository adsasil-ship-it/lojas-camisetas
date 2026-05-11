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
    .titulo-principal { font-family: 'Inter', sans-serif; font-weight: 800; font-size: 40px; color: #1a1c23; }
    .destaque-verde { color: #25D366; }
    .card-produto { 
        background-color: #ffffff; border: 1px solid #e9ecef; padding: 15px; 
        border-radius: 15px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        position: relative;
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

if not os.path.exists("images"): os.makedirs("images")
df = carregar_dados()

# --- CABEÇALHO ---
st.markdown('<h1 class="titulo-principal">ADRIANO <span class="destaque-verde">DESIGNER</span></h1>', unsafe_allow_html=True)

# --- MENU LATERAL ---
menu_principal = st.sidebar.radio("Navegar", ["🛍️ Vitrine", "⚙️ Painel Admin"])

# --- VITRINE ---
if menu_principal == "🛍️ Vitrine":
    if df.empty:
        st.info("Nenhum produto cadastrado.")
    else:
        st.sidebar.subheader("📂 Categorias")
        lista_cats = ["Todos os Produtos"] + sorted(df["categoria"].unique().astype(str).tolist())
        cat_sel = st.sidebar.selectbox("Escolha uma Categoria", lista_cats)
        
        df_f = df if cat_sel == "Todos os Produtos" else df[df["categoria"] == cat_sel]
        
        lista_subs = ["Todas as Subcategorias"] + sorted(df_f["subcategoria"].unique().astype(str).tolist())
        sub_sel = st.sidebar.selectbox("Refinar por Subcategoria", lista_subs)
        if sub_sel != "Todas as Subcategorias": 
            df_f = df_f[df_f["subcategoria"] == sub_sel]

        # ORDENAÇÃO: Novidades no topo
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
        t1, t2, t3, t4 = st.tabs(["➕ Novo Produto", "📝 Editar", "🗑️ Remover", "💾 Backup"])
        
        # Pega o que já existe para sugerir
        exist_cats = sorted(df["categoria"].unique().astype(str).tolist()) if not df.empty else []
        exist_subs = sorted(df["subcategoria"].unique().astype(str).tolist()) if not df.empty else []

        with t1:
            st.write("### Cadastro de Lançamento")
            
            with st.form("form_novo_v4", clear_on_submit=True):
                nome = st.text_input("Nome do Produto")
                preco = st.number_input("Preço", min_value=0.0)
                
                st.write("---")
                st.write("**Organização (Categoria e Subcategoria)**")
                c1, c2 = st.columns(2)
                
                with c1:
                    cat_op = st.radio("Categoria:", ["Usar Existente", "Criar Nova"], key="opt_cat")
                    if cat_op == "Usar Existente":
                        cat_final = st.selectbox("Selecione:", exist_cats if exist_cats else ["Nenhuma cadastrada"], key="sel_cat")
                    else:
                        cat_final = st.text_input("Digite o nome da nova Categoria:", key="in_cat")
                
                with c2:
                    sub_op = st.radio("Subcategoria:", ["Usar Existente", "Criar Nova"], key="opt_sub")
                    if sub_op == "Usar Existente":
                        sub_final = st.selectbox("Selecione:", exist_subs if exist_subs else ["Nenhuma cadastrada"], key="sel_sub")
                    else:
                        sub_final = st.text_input("Digite o nome da nova Subcategoria:", key="in_sub")
                
                st.write("---")
                destaque = st.checkbox("Destaque: Marcar como NOVIDADE (topo da vitrine)")
                desc = st.text_area("Descrição do Produto")
                foto = st.file_uploader("Foto Principal", type=['jpg', 'png', 'jpeg'])
                
                btn_salvar = st.form_submit_button("PUBLICAR PRODUTO")
                
                if btn_salvar:
                    if nome and foto and cat_final and cat_final != "Nenhuma cadastrada":
                        nome_arq = f"{datetime.now().timestamp()}_{foto.name}".replace(" ","_")
                        with open(f"images/{nome_arq}", "wb") as f:
                            f.write(foto.getbuffer())
                        
                        novo = pd.DataFrame([{"nome": nome, "preco": preco, "imagens": nome_arq, 
                                             "categoria": cat_final, "subcategoria": sub_final, 
                                             "descricao": desc, "novidade": destaque}])
                        df = pd.concat([df, novo], ignore_index=True)
                        df.to_csv("produtos.csv", index=False)
                        st.success(f"✅ Produto '{nome}' cadastrado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro: Preencha o Nome, Foto e defina uma Categoria válida!")

        with t2: # EDITAR
            if not df.empty:
                st.write("### Editar Produto Existente")
                escolha_edit = st.selectbox("Qual produto deseja alterar?", df["nome"].tolist())
                idx = df[df["nome"] == escolha_edit].index[0]
                
                with st.form("form_edit_v4"):
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
                        st.success("Alterações salvas!")
                        st.rerun()

        with t3: # REMOVER
            for i, row in df.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{row['nome']}** ({row['categoria']} | {row['subcategoria']})")
                if c2.button("Excluir", key=f"del_v4_{i}"):
                    df = df.drop(i)
                    df.to_csv("produtos.csv", index=False)
                    st.rerun()

        with t4: # BACKUP
            st.write("### Backup e Segurança")
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 BAIXAR MEU BANCO DE DADOS", csv, "backup_adriano.csv", "text/csv")
            st.divider()
            up = st.file_uploader("Restaurar via arquivo CSV", type="csv")
            if st.button("RESTAURAR TUDO") and up:
                pd.read_csv(up).to_csv("produtos.csv", index=False)
                st.success("Dados restaurados!")
                st.rerun()
