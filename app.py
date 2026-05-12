import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO E DESIGN
st.set_page_config(page_title="Adriano Designer | Loja Oficial", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;700;800&display=swap');
    .stApp { background-color: #f8f9fa; }
    .text-box { display: flex; flex-direction: column; align-items: flex-start; justify-content: center; }
    .loja-online-do { font-family: 'Inter', sans-serif; font-size: 11px; letter-spacing: 2px; color: #888; margin-bottom: -10px; font-weight: 700; text-transform: uppercase; }
    .titulo-principal { font-family: 'Bebas Neue', sans-serif; font-size: 60px; color: #1a1c23; line-height: 1; margin: 0; }
    .destaque-verde { color: #25D366; }
    
    .card-produto { background-color: #ffffff; border: 1px solid #e9ecef; padding: 15px; border-radius: 15px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.05); position: relative; height: 100%; }
    
    /* Selos de Destaque */
    .badge-lancamento { background-color: #25D366; color: white; padding: 3px 10px; border-radius: 5px; font-size: 12px; font-weight: bold; position: absolute; top: 10px; left: 10px; z-index: 10; }
    .badge-promocao { background-color: #A020F0; color: white; padding: 3px 10px; border-radius: 5px; font-size: 12px; font-weight: bold; position: absolute; top: 10px; right: 10px; z-index: 10; }
    
    .preco-antigo { text-decoration: line-through; color: #888; font-size: 14px; }
    .views-badge { font-size: 10px; color: #666; background: #eee; padding: 2px 8px; border-radius: 10px; margin-top: 10px; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÕES DE DADOS
def carregar_dados():
    caminho = "produtos.csv"
    cols = ["id", "nome", "preco_venda", "preco_custo", "imagens", "categoria", "subcategoria", "descricao", "visualizacoes", "promocao"]
    if os.path.exists(caminho):
        try:
            df = pd.read_csv(caminho)
            # Garante que todas as colunas existam
            for col in cols:
                if col not in df.columns:
                    if "preco" in col or "visualizacoes" in col:
                        df[col] = 0.0
                    elif col == "promocao":
                        df[col] = False
                    else:
                        df[col] = ""
            return df
        except: pass
    return pd.DataFrame(columns=cols)

if not os.path.exists("images"): os.makedirs("images")
df = carregar_dados()

# --- CABEÇALHO ---
_, col_header, _ = st.columns([1, 4, 1])
with col_header:
    c_logo, c_txt = st.columns([1, 5])
    with c_logo:
        if os.path.exists("logo.png"): st.image("logo.png", width=85) 
    with c_txt:
        st.markdown('<div class="text-box"><p class="loja-online-do">LOJA ONLINE DO:</p><h1 class="titulo-principal">ADRIANO <span class="destaque-verde">DESIGNER</span></h1></div>', unsafe_allow_html=True)

menu_principal = st.sidebar.radio("Navegar", ["🛍️ Vitrine", "⚙️ Painel Admin"])

# --- VITRINE ---
if menu_principal == "🛍️ Vitrine":
    ids_lancamento = df.tail(3)["id"].tolist() if not df.empty else []
    
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        cat_sel = st.selectbox("CATEGORIA", ["Todos"] + sorted(df["categoria"].unique().astype(str).tolist()))
    with c2:
        df_f = df if cat_sel == "Todos" else df[df["categoria"] == cat_sel]
        sub_sel = st.selectbox("SUBCATEGORIA", ["Todas"] + sorted(df_f["subcategoria"].unique().astype(str).tolist()))
    
    df_vitrine = df_f if sub_sel == "Todas" else df_f[df_f["subcategoria"] == sub_sel]
    
    if df_vitrine.empty:
        st.info("Nenhum produto cadastrado.")
    else:
        cols = st.columns(3)
        for i, (idx, row) in enumerate(df_vitrine.iterrows()):
            # Incrementa visualizações
            df.at[idx, "visualizacoes"] += 1
            with cols[i % 3]:
                st.markdown('<div class="card-produto">', unsafe_allow_html=True)
                
                if row['id'] in ids_lancamento:
                    st.markdown('<div class="badge-lancamento">LANÇAMENTO</div>', unsafe_allow_html=True)
                if row['promocao']:
                    st.markdown('<div class="badge-promocao">PROMOÇÃO</div>', unsafe_allow_html=True)

                if os.path.exists(f"images/{row['imagens']}"):
                    st.image(f"images/{row['imagens']}", use_container_width=True)
                
                st.write(f"**{row['nome']}**")
                
                if row['promocao']:
                    valor_desc = float(row['preco_venda']) * 0.85
                    st.markdown(f'<span class="preco-antigo">R$ {float(row["preco_venda"]):.2f}</span>', unsafe_allow_html=True)
                    st.write(f"### R$ {valor_desc:.2f}")
                else:
                    st.write(f"### R$ {float(row['preco_venda']):.2f}")
                
                st.link_button("WHATSAPP", f"https://wa.me/5585998351874?text=Olá Adriano! Tenho interesse no {row['nome']}")
                st.markdown(f'<span class="views-badge">👁️ {int(row["visualizacoes"])}</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        df.to_csv("produtos.csv", index=False)

# --- ADMIN ---
else:
    senha = st.text_input("Senha Admin", type="password")
    if senha == "suasenha123":
        t1, t2, t3, t4 = st.tabs(["➕ Cadastro", "📝 Editar", "🗑️ Remover", "💾 Backup"])
        
        cats = sorted(df["categoria"].unique().astype(str).tolist()) if not df.empty else []
        subs = sorted(df["subcategoria"].unique().astype(str).tolist()) if not df.empty else []

        with t1: # CADASTRO
            with st.form("f_novo", clear_on_submit=True):
                nome = st.text_input("Nome do Produto")
                desc = st.text_area("Descrição")
                c_v = st.number_input("Valor de Venda (R$)", min_value=0.0)
                c_c = st.number_input("Valor de Custo (R$)", min_value=0.0)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    c_op = st.selectbox("Categoria", ["+ Nova"] + cats)
                    c_final = st.text_input("Nova Categoria") if c_op == "+ Nova" else c_op
                with col_b:
                    s_op = st.selectbox("Subcategoria", ["+ Nova"] + subs)
                    s_final = st.text_input("Nova Subcategoria") if s_op == "+ Nova" else s_op
                
                foto = st.file_uploader("Imagem", type=['jpg', 'png', 'jpeg'])
                promo = st.checkbox("Ativar Promoção (15% OFF)")
                
                if st.form_submit_button("FINALIZAR CADASTRO"):
                    if nome and foto:
                        nome_img = f"{datetime.now().timestamp()}_{foto.name}"
                        with open(f"images/{nome_img}", "wb") as f: f.write(foto.getbuffer())
                        novo_id = int(datetime.now().timestamp())
                        novo = pd.DataFrame([{"id": novo_id, "nome": nome, "preco_venda": c_v, "preco_custo": c_c, "imagens": nome_img, "categoria": c_final, "subcategoria": s_final, "descricao": desc, "visualizacoes": 0, "promocao": promo}])
                        df = pd.concat([df, novo], ignore_index=True)
                        df.to_csv("produtos.csv", index=False)
                        st.success("Produto cadastrado!")
                        st.rerun()

        with t2: # EDITAR
            if not df.empty:
                item_edicao = st.selectbox("Selecione o produto para editar:", df["nome"].tolist())
                idx_e = df[df["nome"] == item_edicao].index[0]
                with st.form("f_edit"):
                    e_nome = st.text_input("Nome", value=df.at[idx_e, 'nome'])
                    e_desc = st.text_area("Descrição", value=df.at[idx_e, 'descricao'])
                    e_venda = st.number_input("Venda (R$)", value=float(df.at[idx_e, 'preco_venda']))
                    e_custo = st.number_input("Custo (R$)", value=float(df.at[idx_e, 'preco_custo']))
                    e_cat = st.text_input("Categoria", value=df.at[idx_e, 'categoria'])
                    e_sub = st.text_input("Subcategoria", value=df.at[idx_e, 'subcategoria'])
                    e_promo = st.checkbox("Ativar Promoção (15% OFF)", value=bool(df.at[idx_e, 'promocao']))
                    
                    if st.form_submit_button("SALVAR"):
                        df.at[idx_e, 'nome'] = e_nome
                        df.at[idx_e, 'descricao'] = e_desc
                        df.at[idx_e, 'preco_venda'] = e_venda
                        df.at[idx_e, 'preco_custo'] = e_custo
                        df.at[idx_e, 'categoria'] = e_cat
                        df.at[idx_e, 'subcategoria'] = e_sub
                        df.at[idx_e, 'promocao'] = e_promo
                        df.to_csv("produtos.csv", index=False)
                        st.success("Atualizado!")
                        st.rerun()

        with t3: # REMOVER (CORRIGIDO)
            st.write("### Gerenciar Remoção de Itens")
            if df.empty:
                st.info("Nenhum produto para remover.")
            else:
                for i, row in df.iterrows():
                    col_info, col_btn = st.columns([4, 1])
                    with col_info:
                        st.write(f"🗑️ **{row['nome']}** | Categoria: {row['categoria']}")
                    with col_btn:
                        # Botão de exclusão único para cada item
                        if st.button("EXCLUIR", key=f"btn_del_{row['id']}"):
                            # Remove a imagem da pasta para não ocupar espaço
                            if os.path.exists(f"images/{row['imagens']}"):
                                os.remove(f"images/{row['imagens']}")
                            
                            df = df.drop(i)
                            df.to_csv("produtos.csv", index=False)
                            st.error(f"Produto '{row['nome']}' removido!")
                            st.rerun()

        with t4: # BACKUP
            st.download_button("BAIXAR BACKUP", df.to_csv(index=False).encode('utf-8'), "backup_loja.csv")
            arq_b = st.file_uploader("Subir arquivo para restauração", type="csv")
            if arq_b and st.button("Confirmar Restauração"):
                pd.read_csv(arq_b).to_csv("produtos.csv", index=False)
                st.rerun()
