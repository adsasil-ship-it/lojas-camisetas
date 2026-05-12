import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

# 1. CONFIGURAÇÃO E DESIGN
st.set_page_config(page_title="Adriano Designer | Loja", layout="wide", page_icon="🛍️")

# CSS Personalizado para melhorar a UI
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;700;800&display=swap');
    
    /* Cabeçalho */
    .header-container { display: flex; align-items: center; justify-content: center; gap: 15px; padding: 20px 0; }
    .logo-img { width: 70px; height: auto; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    .titulo-principal { font-family: 'Bebas Neue', sans-serif; font-size: clamp(35px, 10vw, 60px); color: #1a1c23; line-height: 0.9; margin: 0; }
    .destaque-verde { color: #25D366; }
    .loja-online-do { font-family: 'Inter', sans-serif; font-size: 12px; letter-spacing: 3px; color: #888; margin-bottom: -5px; font-weight: 700; }
    
    /* Card de Produto */
    .card-produto { 
        background: white; 
        border: 1px solid #f0f0f0; 
        padding: 15px; 
        border-radius: 16px; 
        text-align: center; 
        transition: transform 0.2s;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    .card-produto:hover { transform: translateY(-5px); border-color: #25D366; }

    /* Badges */
    .badge-promo { background: #ff4b4b; color: white; font-size: 10px; padding: 4px 8px; border-radius: 6px; position: absolute; top: 10px; right: 10px; z-index: 10; font-weight: bold; }
    .badge-lancamento { background: #25D366; color: white; font-size: 10px; padding: 4px 8px; border-radius: 6px; position: absolute; top: 10px; left: 10px; z-index: 10; font-weight: bold; }
    
    /* Textos */
    .preco-venda { color: #1a1c23; font-weight: 800; font-size: 20px; font-family: 'Inter', sans-serif; margin: 10px 0; }
    .views-counter { font-size: 10px; color: #bbb; margin-top: 10px; display: block; }
    
    /* Ajustes Streamlit */
    [data-testid="stMetricValue"] { font-size: 24px !important; color: #25D366 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÕES DE DADOS
def carregar_dados():
    caminho = "produtos.csv"
    if os.path.exists(caminho):
        try:
            df = pd.read_csv(caminho)
            if "imagens" not in df.columns: df["imagens"] = ""
            return df
        except: return pd.DataFrame()
    return pd.DataFrame()

def salvar_dados(df_para_salvar):
    df_para_salvar.to_csv("produtos.csv", index=False)

if not os.path.exists("images"): os.makedirs("images")
df = carregar_dados()

# --- COMPONENTE DE DETALHES (POP-UP) ---
@st.dialog("Detalhes do Produto")
def modal_detalhes(produto):
    col_img, col_info = st.columns([1, 1])
    
    img_data = str(produto.get('imagens', ""))
    lista_imgs = img_data.split(";") if (img_data and img_data != "nan") else []

    with col_img:
        if lista_imgs:
            st.image(f"images/{lista_imgs[0]}", use_container_width=True)
            if len(lista_imgs) > 1:
                st.write("📸 **Mais fotos:**")
                # Grid de miniaturas dentro do modal
                sub_cols = st.columns(3)
                for i, img_extra in enumerate(lista_imgs):
                    with sub_cols[i % 3]:
                        st.image(f"images/{img_extra}", use_container_width=True)
        else:
            st.info("Sem imagem disponível.")

    with col_info:
        st.title(produto['nome'])
        st.subheader(f"Categoria: {produto['categoria']}")
        st.write("---")
        st.markdown(f"**Descrição:**\n\n{produto['descricao']}")
        
        v_final = float(produto['preco_venda'])
        if produto.get('promocao'):
            v_final = v_final * 0.85
            st.success(f"🔥 Oferta Especial: R$ {v_final:.2f}")
        else:
            st.metric("Preço", f"R$ {v_final:.2f}")
        
        st.link_button("💬 PEDIR VIA WHATSAPP", 
                       f"https://wa.me/5585998351874?text=Olá Adriano! Tenho interesse no produto: {produto['nome']}",
                       use_container_width=True, type="primary")

# --- CABEÇALHO ---
logo_tag = ""
if os.path.exists("logo.png"):
    with open("logo.png", "rb") as f:
        logo_tag = f'<img src="data:image/png;base64,{base64.b64encode(f.read()).decode()}" class="logo-img">'

st.markdown(f'''
    <div class="header-container">
        {logo_tag}
        <div>
            <p class="loja-online-do">LOJA ONLINE DO:</p>
            <h1 class="titulo-principal">ADRIANO <span class="destaque-verde">DESIGNER</span></h1>
        </div>
    </div>
''', unsafe_allow_html=True)

menu = st.sidebar.radio("Navegar", ["🛍️ Vitrine", "⚙️ Painel Admin"])

# --- VITRINE ---
if menu == "🛍️ Vitrine":
    if df.empty:
        st.info("Nenhum produto cadastrado no momento.")
    else:
        # Filtros e Ordenação
        categorias = ["Todos"] + sorted(df["categoria"].unique().astype(str).tolist())
        cat_sel = st.sidebar.selectbox("Filtrar por Categoria", categorias)
        
        df_v = df if cat_sel == "Todos" else df[df["categoria"] == cat_sel]
        df_v = df_v.sort_values(by="id", ascending=False) # Mais recentes primeiro

        st.divider()
        
        # Grid de Produtos (2 colunas no mobile/PC)
        cols = st.columns(2)
        for i, (idx, row) in enumerate(df_v.iterrows()):
            with cols[i % 2]:
                st.markdown('<div class="card-produto">', unsafe_allow_html=True)
                
                # Badges
                if i < 4: st.markdown('<div class="badge-lancamento">NOVO</div>', unsafe_allow_html=True)
                if row.get('promocao'): st.markdown('<div class="badge-promo">OFF</div>', unsafe_allow_html=True)
                
                # Imagem Principal
                img_data = str(row.get('imagens', ""))
                if img_data and img_data != "nan":
                    lista_imgs = img_data.split(";")
                    st.image(f"images/{lista_imgs[0]}", use_container_width=True)
                
                # Info Resumida
                st.markdown(f"**{row['nome']}**")
                
                v_exibicao = float(row['preco_venda'])
                if row.get('promocao'):
                    st.markdown(f'<span class="preco-venda" style="color:#ff4b4b">R$ {v_exibicao*0.85:.2f}</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="preco-venda">R$ {v_exibicao:.2f}</span>', unsafe_allow_html=True)
                
                # BOTÃO DE DETALHES (Onde o "clique" acontece)
                if st.button(f"🔍 Ver Detalhes", key=f"btn_{row['id']}", use_container_width=True):
                    # Incrementa visualização
                    df.at[idx, "visualizacoes"] = int(row.get("visualizacoes", 0)) + 1
                    salvar_dados(df)
                    modal_detalhes(row) # Abre o Pop-up
                
                st.markdown(f'<span class="views-counter">👁️ {int(row.get("visualizacoes", 0))} visualizações</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                st.write("") # Espaçador

# --- ADMIN ---
else:
    senha = st.sidebar.text_input("Senha de Acesso", type="password")
    if senha == "suasenha123":
        t1, t2, t3, t4 = st.tabs(["➕ Cadastro", "📝 Editar", "🗑️ Remover", "💾 Backup"])
        
        with t1:
            with st.form("add", clear_on_submit=True):
                n = st.text_input("Nome do Produto")
                d = st.text_area("Descrição Completa")
                col1, col2 = st.columns(2)
                pv = col1.number_input("Preço de Venda (R$)", min_value=0.0)
                pc = col2.number_input("Preço de Custo (R$)", min_value=0.0)
                ct = st.text_input("Categoria (Ex: Social Media, Logo, Impressos)")
                im = st.file_uploader("Imagens do Produto", accept_multiple_files=True)
                pr = st.checkbox("Colocar em Promoção (15% OFF)")
                
                if st.form_submit_button("CADASTRAR PRODUTO"):
                    if n and im:
                        nomes_arquivos = []
                        for file in im:
                            fn = f"{int(datetime.now().timestamp())}_{file.name}"
                            with open(f"images/{fn}", "wb") as f: f.write(file.getbuffer())
                            nomes_arquivos.append(fn)
                        
                        novo = pd.DataFrame([{
                            "id": int(datetime.now().timestamp()), 
                            "nome": n, "preco_venda": pv, "preco_custo": pc, 
                            "imagens": ";".join(nomes_arquivos), "categoria": ct, 
                            "descricao": d, "visualizacoes": 0, "promocao": pr
                        }])
                        df = pd.concat([df, novo], ignore_index=True)
                        salvar_dados(df)
                        st.success("Produto cadastrado com sucesso!")
                        st.rerun()

        with t2:
            if not df.empty:
                sel = st.selectbox("Selecione o produto para editar", df["nome"].tolist())
                idx_e = df[df["nome"] == sel].index[0]
                
                with st.form("edit"):
                    en = st.text_input("Nome", value=df.at[idx_e, 'nome'])
                    ed = st.text_area("Descrição", value=df.at[idx_e, 'descricao'])
                    col1, col2 = st.columns(2)
                    ev = col1.number_input("Venda", value=float(df.at[idx_e, 'preco_venda']))
                    ec = col2.number_input("Custo", value=float(df.at[idx_e, 'preco_custo']))
                    ect = st.text_input("Categoria", value=df.at[idx_e, 'categoria'])
                    ep = st.checkbox("Promoção", value=bool(df.at[idx_e, 'promocao']))
                    eim = st.file_uploader("Substituir Imagens (Opcional)", accept_multiple_files=True)
                    
                    if st.form_submit_button("SALVAR ALTERAÇÕES"):
                        df.at[idx_e, 'nome'] = en
                        df.at[idx_e, 'descricao'] = ed
                        df.at[idx_e, 'preco_venda'] = ev
                        df.at[idx_e, 'preco_custo'] = ec
                        df.at[idx_e, 'categoria'] = ect
                        df.at[idx_e, 'promocao'] = ep
                        
                        if eim:
                            novos_nomes = []
                            for file in eim:
                                fn = f"edit_{int(datetime.now().timestamp())}_{file.name}"
                                with open(f"images/{fn}", "wb") as f: f.write(file.getbuffer())
                                novos_nomes.append(fn)
                            df.at[idx_e, 'imagens'] = ";".join(novos_nomes)
                        
                        salvar_dados(df)
                        st.success("Produto atualizado!")
                        st.rerun()

        with t3:
            for i, row in df.iterrows():
                c1, c2 = st.columns([4,1])
                c1.write(f"ID: {row['id']} | **{row['nome']}**")
                if c2.button("Excluir", key=f"del_{row['id']}"):
                    df = df.drop(i)
                    salvar_dados(df)
                    st.rerun()

        with t4:
            st.download_button("Exportar CSV", df.to_csv(index=False).encode('utf-8'), "loja_backup.csv")
