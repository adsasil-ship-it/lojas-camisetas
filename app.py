import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

# 1. CONFIGURAÇÃO E DESIGN DA PÁGINA
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

# 2. FUNÇÕES DE GERENCIAMENTO DE DADOS
def carregar_dados():
    caminho = "produtos.csv"
    if os.path.exists(caminho):
        try:
            df = pd.read_csv(caminho)
            # Normaliza a coluna caso venha do modelo antigo ('images' -> 'imagens')
            if "images" in df.columns and "imagens" not in df.columns:
                df = df.rename(columns={"images": "imagens"})
            if "imagens" not in df.columns:
                df["imagens"] = ""
            return df
        except: 
            return pd.DataFrame()
    return pd.DataFrame()

# Garante que a pasta de imagens exista na raiz do projeto automaticamente
if not os.path.exists("images"): 
    os.makedirs("images")

df = carregar_dados()

# --- CONFIGURAÇÃO DO CABEÇALHO ---
logo_tag = ""
if os.path.exists("logo.png"):
    with open("logo.png", "rb") as f:
        logo_tag = f'<img src="data:image/png;base64,{base64.b64encode(f.read()).decode()}" class="logo-img">'

st.markdown(f'<div class="header-container">{logo_tag}<div><p class="loja-online-do">LOJA ONLINE DO:</p><h1 class="titulo-principal">ADRIANO <span class="destaque-verde">DESIGNER</span></h1></div></div>', unsafe_allow_html=True)

menu = st.sidebar.radio("Navegar", ["🛍️ Vitrine", "⚙️ Painel Admin"])

# --- MODULO: VITRINE ---
if menu == "🛍️ Vitrine":
    if df.empty:
        st.info("Nenhum produto cadastrado no momento. Acesse o Painel Admin para começar.")
    else:
        # Define regras automáticas para os selos visuais
        lista_lancamentos = df.tail(6)["id"].tolist() 
        lista_novidades = df.head(3)["id"].tolist()   

        df['ordem_topo'] = df['id'].apply(lambda x: 0 if x in lista_lancamentos else 1)
        df_exibicao = df.sort_values(by=['ordem_topo', 'id'], ascending=[True, False])

        cat_sel = st.selectbox("Filtrar Categoria", ["Todos"] + sorted(df["categoria"].unique().astype(str).tolist()))
        df_v = df_exibicao if cat_sel == "Todos" else df_exibicao[df_exibicao["categoria"] == cat_sel]
        
        st.divider()
        cols = st.columns(2)
        for i, (idx, row) in enumerate(df_v.iterrows()):
            # Incrementa o contador de visualizações de forma segura
            df.at[idx, "visualizacoes"] = int(row.get("visualizacoes", 0)) + 1
            
            with cols[i % 2]:
                st.markdown('<div class="card-produto">', unsafe_allow_html=True)
                
                # Renderização dos Selos Informativos
                if row['id'] in lista_lancamentos:
                    st.markdown('<div class="badge-lancamento">LANÇAMENTO</div>', unsafe_allow_html=True)
                if row['id'] in lista_novidades:
                    st.markdown('<div class="badge-novidade">NOVIDADE</div>', unsafe_allow_html=True)
                if row.get('promocao'): 
                    st.markdown('<div class="badge-promo">15% OFF</div>', unsafe_allow_html=True)
                
                # Exibição segura da imagem principal no card
                img_data = str(row.get('imagens', ""))
                if img_data and img_data.strip() != "" and img_data != "nan":
                    lista_imgs = img_data.split(";")
                    if lista_imgs[0] and os.path.exists(f"images/{lista_imgs[0]}"):
                        st.image(f"images/{lista_imgs[0]}", use_container_width=True)
                
                st.markdown(f"**{row['nome']}**")
                
                # Bloco de cálculo de preços (com ou sem promoção aplicada)
                if row.get('promocao'):
                    v_desc = float(row['preco_venda']) * 0.85
                    st.markdown(f'<span class="preco-antigo">R$ {float(row["preco_venda"]):.2f}</span>', unsafe_allow_html=True)
                    st.markdown(f'<span class="preco-venda">R$ {v_desc:.2f}</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="preco-venda">R$ {float(row["preco_venda"]):.2f}</span>', unsafe_allow_html=True)
                
                # Detalhes expansíveis e mini-galeria de fotos adicionais
                with st.expander("Ver Detalhes"): 
                    st.write(row['descricao'])
                    if img_data and ";" in img_data and img_data != "nan":
                        st.write("---")
                        st.write("Mais fotos do produto:")
                        # Cria colunas menores para dispor as fotos adicionais lado a lado
                        sub_cols = st.columns(len(lista_imgs))
                        for idx_img, extra_img in enumerate(lista_imgs):
                            if os.path.exists(f"images/{extra_img}"):
                                sub_cols[idx_img].image(f"images/{extra_img}", use_container_width=True)
                
                st.link_button("PEDIR", f"https://wa.me/5585998351874?text=Interesse: {row['nome']}")
                st.markdown(f'<span class="views-counter">👁️ {int(df.at[idx, "visualizacoes"])}</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Salva as novas visualizações limpando a coluna temporária de ordenação
        df.drop(columns=['ordem_topo']).to_csv("produtos.csv", index=False)

# --- MODULO: PAINEL ADMINISTRATIVO ---
else:
    senha = st.sidebar.text_input("Senha de Acesso", type="password")
    if senha == "suasenha123":
        t1, t2, t3, t4 = st.tabs(["➕ Cadastro", "📝 Editar", "🗑️ Remover", "💾 Backup"])
        
        # ABA: CADASTRO DE PRODUTOS
        with t1:
            with st.form("add", clear_on_submit=True):
                n = st.text_input("Nome do Produto")
                d = st.text_area("Descrição Completa")
                col1, col2 = st.columns(2)
                pv = col1.number_input("Preço de Venda (R$)", min_value=0.0)
                pc = col2.number_input("Preço de Custo (R$)", min_value=0.0)
                ct = st.text_input("Categoria")
                im = st.file_uploader("Imagens do Produto (Selecione uma ou mais)", accept_multiple_files=True)
                pr = st.checkbox("Ativar Promoção (Aplica 15% de desconto automático)")
                
                if st.form_submit_button("SALVAR PRODUTO"):
                    if n and im:
                        nomes_arquivos = []
                        for file in im:
                            # Evita conflitos de nomes usando timestamp fixo no lote
                            fn = f"{int(datetime.now().timestamp())}_{file.name}"
                            with open(f"images/{fn}", "wb") as f: 
                                f.write(file.getbuffer())
                            nomes_arquivos.append(fn)
                        
                        str_imagens = ";".join(nomes_arquivos)
                        novo = pd.DataFrame([{"id": int(datetime.now().timestamp()), "nome": n, "preco_venda": pv, "preco_custo": pc, "imagens": str_imagens, "categoria": ct, "descricao": d, "visualizacoes": 0, "promocao": pr}])
                        df = pd.concat([df, novo], ignore_index=True)
                        df.to_csv("produtos.csv", index=False)
                        st.success("Produto cadastrado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Por favor, preencha o Nome e envie pelo menos uma Imagem.")

        # ABA: EDIÇÃO COMPLETA DE PRODUTOS
        with t2:
            if not df.empty:
                sel = st.selectbox("Escolha o produto para modificar", df["nome"].tolist())
                idx_e = df[df["nome"] == sel].index[0]
                
                with st.form("edit"):
                    st.write(f"Modificando ID do Registro: `{df.at[idx_e, 'id']}`")
                    en = st.text_input("Nome do Produto", value=str(df.at[idx_e, 'nome']))
                    ed = st.text_area("Descrição Completa", value=str(df.at[idx_e, 'descricao']))
                    col1, col2 = st.columns(2)
                    ev = col1.number_input("Preço de Venda (R$)", value=float(df.at[idx_e, 'preco_venda']))
                    ec = col2.number_input("Preço de Custo (R$)", value=float(df.at[idx_e, 'preco_custo']))
                    ect = st.text_input("Categoria", value=str(df.at[idx_e, 'categoria']))
                    ep = st.checkbox("Ativar Promoção", value=bool(df.at[idx_e, 'promocao']))
                    
                    st.info("Imagens atuais cadastradas para este produto: " + str(df.at[idx_e, 'imagens']))
                    st.warning("Deixe o campo abaixo em branco se desejar manter as fotos atuais. Subir novos arquivos apagará o histórico de fotos deste item.")
                    eim = st.file_uploader("Substituir lote de Imagens", accept_multiple_files=True)
                    
                    if st.form_submit_button("SALVAR ALTERAÇÕES"):
                        df.at[idx_e, 'nome'] = en
                        df.at[idx_e, 'descricao'] = ed
                        df.at[idx_e, 'preco_venda'] = ev
                        df.at[idx_e, 'preco_custo'] = ec
                        df.at[idx_e, 'categoria'] = ect
                        df.at[idx_e, 'promocao'] = ep
                        
                        # Altera os arquivos de fotos apenas se novos forem enviados no uploader
                        if eim:
                            novos_nomes = []
                            for file in eim:
                                fn = f"edit_{int(datetime.now().timestamp())}_{file.name}"
                                with open(f"images/{fn}", "wb") as f: 
                                    f.write(file.getbuffer())
                                novos_nomes.append(fn)
                            df.at[idx_e, 'imagens'] = ";".join(novos_nomes)
                        
                        df.to_csv("produtos.csv", index=False)
                        st.success("Produto atualizado com sucesso no sistema!")
                        st.rerun()
            else:
                st.info("Não existem produtos cadastrados para edição.")

        # ABA: REMOÇÃO DE PRODUTOS
        with t3:
            if not df.empty:
                for i, row in df.iterrows():
                    c1, c2 = st.columns([4,1])
                    c1.write(f"🗑️ **{row['nome']}** (Categoria: {row['categoria']})")
                    if c2.button("Apagar Definitivamente", key=f"d_{row['id']}"):
                        df = df.drop(i)
                        df.to_csv("produtos.csv", index=False)
                        st.rerun()
            else:
                st.info("Nenhum produto cadastrado para ser removido.")

        # ABA: BACKUP E MANUTENÇÃO
        with t4:
            st.download_button("Exportar Banco de Dados (CSV)", df.to_csv(index=False).encode('utf-8'), "loja_backup.csv")
            st.write("---")
            up = st.file_uploader("Restaurar base de dados via arquivo CSV", type="csv")
            if up and st.button("Confirmar Restauração Forçada"):
                pd.read_csv(up).to_csv("produtos.csv", index=False)
                st.success("Tabelas de dados restauradas.")
                st.rerun()
