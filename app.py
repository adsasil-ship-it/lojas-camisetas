import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

# 1. CONFIGURAÇÃO E DESIGN
st.set_page_config(page_title="Adriano Designer | Loja", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;700;800&display=swap');
    
    .header-container { display: flex; align-items: center; justify-content: center; gap: 15px; padding: 15px 0; }
    .logo-img { width: 65px; height: auto; border-radius: 8px; }
    .titulo-principal { font-family: 'Bebas Neue', sans-serif; font-size: clamp(30px, 8vw, 50px); color: #1a1c23; line-height: 0.9; margin: 0; }
    .destaque-verde { color: #25D366; }
    .loja-online-do { font-family: 'Inter', sans-serif; font-size: 10px; letter-spacing: 2px; color: #888; margin-bottom: -5px; font-weight: 700; }
    
    [data-testid="stHorizontalBlock"] { display: flex; flex-wrap: wrap; gap: 8px; }
    @media (max-width: 640px) {
        [data-testid="stHorizontalBlock"] > div { width: calc(50% - 8px) !important; flex: 1 1 calc(50% - 8px) !important; min-width: calc(50% - 8px) !important; }
    }

    .card-produto { 
        background: white; border: 1px solid #eee; padding: 10px; border-radius: 12px; 
        text-align: center; height: 100%; position: relative; display: flex; flex-direction: column;
    }

    .badge-promo { background: #A020F0; color: white; font-size: 9px; padding: 3px 7px; border-radius: 4px; position: absolute; top: 8px; right: 8px; z-index: 10; font-weight: bold; }
    .badge-lancamento { background: #25D366; color: white; font-size: 9px; padding: 3px 7px; border-radius: 4px; position: absolute; top: 8px; left: 8px; z-index: 10; font-weight: bold; }
    .badge-novidade { background: #007BFF; color: white; font-size: 9px; padding: 3px 7px; border-radius: 4px; position: absolute; top: 35px; left: 8px; z-index: 10; font-weight: bold; }
    
    .views-counter { font-size: 9px; color: #999; margin-top: 8px; display: block; }
    .preco-antigo { text-decoration: line-through; color: #888; font-size: 11px; }
    .preco-venda { color: #1a1c23; font-weight: 800; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÕES DE DADOS
def carregar_dados():
    caminho = "produtos.csv"
    if os.path.exists(caminho):
        try:
            df = pd.read_csv(caminho)
            if "imagens" not in df.columns:
                df["imagens"] = ""
            return df
        except: return pd.DataFrame()
    return pd.DataFrame()

if not os.path.exists("images"): os.makedirs("images")
df = carregar_dados()

# --- CABEÇALHO ---
logo_tag = ""
if os.path.exists("logo.png"):
    with open("logo.png", "rb") as f:
        logo_tag = f'<img src="data:image/png;base64,{base64.b64encode(f.read()).decode()}" class="logo-img">'

st.markdown(f'<div class="header-container">{logo_tag}<div><p class="loja-online-do">LOJA ONLINE DO:</p><h1 class="titulo-principal">ADRIANO <span class="destaque-verde">DESIGNER</span></h1></div></div>', unsafe_allow_html=True)

menu = st.sidebar.radio("Navegar", ["🛍️ Vitrine", "⚙️ Painel Admin"])

# --- VITRINE ---
if menu == "🛍️ Vitrine":
    if df.empty:
        st.info("Cadastre produtos no Painel Admin.")
    else:
        lista_lancamentos = df.tail(6)["id"].tolist() 
        lista_novidades = df.head(3)["id"].tolist()   

        df['ordem_topo'] = df['id'].apply(lambda x: 0 if x in lista_lancamentos else 1)
        df_exibicao = df.sort_values(by=['ordem_topo', 'id'], ascending=[True, False])

        cat_sel = st.selectbox("Filtrar Categoria", ["Todos"] + sorted(df["categoria"].unique().astype(str).tolist()))
        df_v = df_exibicao if cat_sel == "Todos" else df_exibicao[df_exibicao["categoria"] == cat_sel]
        
        st.divider()
        cols = st.columns(2)
        for i, (idx, row) in enumerate(df_v.iterrows()):
            df.at[idx, "visualizacoes"] = int(row.get("visualizacoes", 0)) + 1
            
            with cols[i % 2]:
                st.markdown('<div class="card-produto">', unsafe_allow_html=True)
                
                if row['id'] in lista_lancamentos:
                    st.markdown('<div class="badge-lancamento">LANÇAMENTO</div>', unsafe_allow_html=True)
                if row['id'] in lista_novidades:
                    st.markdown('<div class="badge-novidade">NOVIDADE</div>', unsafe_allow_html=True)
                if row.get('promocao'): 
                    st.markdown('<div class="badge-promo">15% OFF</div>', unsafe_allow_html=True)
                
                # Lógica para Múltiplas Imagens
                img_data = str(row.get('imagens', ""))
                if img_data and img_data != "nan":
                    lista_imgs = img_data.split(";")
                    # Mostra a primeira imagem como principal
                    st.image(f"images/{lista_imgs[0]}", use_container_width=True)
                
                st.markdown(f"**{row['nome']}**")
                
                if row.get('promocao'):
                    v_desc = float(row['preco_venda']) * 0.85
                    st.markdown(f'<span class="preco-antigo">R$ {float(row["preco_venda"]):.2f}</span>', unsafe_allow_html=True)
                    st.markdown(f'<span class="preco-venda">R$ {v_desc:.2f}</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="preco-venda">R$ {float(row["preco_venda"]):.2f}</span>', unsafe_allow_html=True)
                
                with st.expander("Ver Detalhes"): 
                    st.write(row['descricao'])
                    # Se houver mais fotos, mostra aqui dentro
                    if img_data and ";" in img_data:
                        st.write("---")
                        st.write("Mais fotos:")
                        for extra_img in lista_imgs:
                            st.image(f"images/{extra_img}", width=150)
                
                st.link_button("PEDIR", f"https://wa.me/5585998351874?text=Interesse: {row['nome']}")
                st.markdown(f'<span class="views-counter">👁️ {int(df.at[idx, "visualizacoes"])}</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        df.drop(columns=['ordem_topo']).to_csv("produtos.csv", index=False)

# --- ADMIN ---
else:
    senha = st.sidebar.text_input("Senha", type="password")
    if senha == "suasenha123":
        t1, t2, t3, t4 = st.tabs(["➕ Cadastro", "📝 Editar", "🗑️ Remover", "💾 Backup"])
        
        with t1:
            with st.form("add", clear_on_submit=True):
                n = st.text_input("Nome")
                d = st.text_area("Descrição")
                col1, col2 = st.columns(2)
                pv = col1.number_input("Venda", min_value=0.0)
                pc = col2.number_input("Custo", min_value=0.0)
                ct = st.text_input("Categoria")
                im = st.file_uploader("Imagens (Selecione uma ou mais)", accept_multiple_files=True)
                pr = st.checkbox("Promoção")
                if st.form_submit_button("SALVAR"):
                    if n and im:
                        nomes_arquivos = []
                        for file in im:
                            fn = f"{int(datetime.now().timestamp())}_{file.name}"
                            with open(f"images/{fn}", "wb") as f: f.write(file.getbuffer())
                            nomes_arquivos.append(fn)
                        
                        str_imagens = ";".join(nomes_arquivos)
                        novo = pd.DataFrame([{"id": int(datetime.now().timestamp()), "nome": n, "preco_venda": pv, "preco_custo": pc, "imagens": str_imagens, "categoria": ct, "descricao": d, "visualizacoes": 0, "promocao": pr}])
                        df = pd.concat([df, novo], ignore_index=True)
                        df.to_csv("produtos.csv", index=False)
                        st.success("Produto salvo!")
                        st.rerun()

        with t2:
            if not df.empty:
                sel = st.selectbox("Escolha para editar", df["nome"].tolist())
                idx_e = df[df["nome"] == sel].index[0]
                
                with st.form("edit"):
                    st.write(f"Editando ID: {df.at[idx_e, 'id']}")
                    en = st.text_input("Nome", value=df.at[idx_e, 'nome'])
                    ed = st.text_area("Descrição", value=df.at[idx_e, 'descricao'])
                    col1, col2 = st.columns(2)
                    ev = col1.number_input("Preço Venda", value=float(df.at[idx_e, 'preco_venda']))
                    ec = col2.number_input("Preço Custo", value=float(df.at[idx_e, 'preco_custo']))
                    ect = st.text_input("Categoria", value=df.at[idx_e, 'categoria'])
                    ep = st.checkbox("Promoção", value=bool(df.at[idx_e, 'promocao']))
                    
                    st.warning("Se selecionar novas imagens, as antigas deste produto serão ignoradas.")
                    eim = st.file_uploader("Substituir Imagens", accept_multiple_files=True)
                    
                    if st.form_submit_button("ATUALIZAR TUDO"):
                        # Atualiza campos de texto e números
                        df.at[idx_e, 'nome'] = en
                        df.at[idx_e, 'descricao'] = ed
                        df.at[idx_e, 'preco_venda'] = ev
                        df.at[idx_e, 'preco_custo'] = ec
                        df.at[idx_e, 'categoria'] = ect
                        df.at[idx_e, 'promocao'] = ep
                        
                        # Atualiza imagens se novas forem enviadas
                        if eim:
                            novos_nomes = []
                            for file in eim:
                                fn = f"edit_{int(datetime.now().timestamp())}_{file.name}"
                                with open(f"images/{fn}", "wb") as f: f.write(file.getbuffer())
                                novos_nomes.append(fn)
                            df.at[idx_e, 'imagens'] = ";".join(novos_nomes)
                        
                        df.to_csv("produtos.csv", index=False)
                        st.success("Produto atualizado com sucesso!")
                        st.rerun()

        with t3:
            for i, row in df.iterrows():
                c1, c2 = st.columns([4,1])
                c1.write(f"🗑️ {row['nome']}")
                if c2.button("Apagar", key=f"d_{row['id']}"):
                    df = df.drop(i)
                    df.to_csv("produtos.csv", index=False)
                    st.rerun()

        with t4:
            st.download_button("Download Backup CSV", df.to_csv(index=False).encode('utf-8'), "loja.csv")
            up = st.file_uploader("Restaurar via CSV", type="csv")
            if up and st.button("Confirmar Restauração"):
                pd.read_csv(up).to_csv("produtos.csv", index=False)
                st.rerun()
