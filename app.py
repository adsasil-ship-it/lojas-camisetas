import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO E DESIGN
st.set_page_config(page_title="Adriano Designer | Catálogo", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;800&display=swap');
    .stApp { background-color: #f8f9fa; }
    .header-container { text-align: left; margin-bottom: 20px; }
    .titulo-principal { font-family: 'Inter', sans-serif; font-weight: 800; font-size: 40px; color: #1a1c23; }
    .destaque-verde { color: #25D366; }
    .card-produto { background-color: #ffffff; border: 1px solid #e9ecef; padding: 15px; border-radius: 15px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÕES DE DADOS
def carregar_dados():
    caminho = "produtos.csv"
    colunas = ["nome", "preco", "imagens", "categoria", "subcategoria", "descricao"]
    if os.path.exists(caminho):
        try:
            df = pd.read_csv(caminho)
            for col in colunas:
                if col not in df.columns: df[col] = ""
            return df
        except: pass
    return pd.DataFrame(columns=colunas)

if not os.path.exists("images"): os.makedirs("images")
df = carregar_dados()

# --- CABEÇALHO ---
st.markdown('<div class="header-container"><h1 class="titulo-principal">ADRIANO <span class="destaque-verde">DESIGNER</span></h1></div>', unsafe_allow_html=True)

menu = st.sidebar.radio("Navegar", ["🛍️ Vitrine", "⚙️ Painel Admin"])

# --- VITRINE ---
if menu == "🛍️ Vitrine":
    if df.empty:
        st.info("Catálogo vazio.")
    else:
        st.sidebar.subheader("Filtros")
        cat_sel = st.sidebar.selectbox("Filtrar Categoria", ["Todas"] + sorted(df["categoria"].unique().astype(str).tolist()))
        df_f = df if cat_sel == "Todas" else df[df["categoria"] == cat_sel]
        
        sub_sel = st.sidebar.selectbox("Filtrar Subcategoria", ["Todas"] + sorted(df_f["subcategoria"].unique().astype(str).tolist()))
        if sub_sel != "Todas": df_f = df_f[df_f["subcategoria"] == sub_sel]

        cols = st.columns(3)
        for i, (idx, row) in enumerate(df_f.iloc[::-1].iterrows()):
            with cols[i % 3]:
                st.markdown('<div class="card-produto">', unsafe_allow_html=True)
                if os.path.exists(f"images/{row['imagens']}"):
                    st.image(f"images/{row['imagens']}", use_container_width=True)
                st.write(f"**{row['nome']}**")
                st.write(f"{row['categoria']} > {row['subcategoria']}")
                st.write(f"R$ {float(row['preco']):.2f}")
                st.link_button("WhatsApp", f"https://wa.me/5585998351874?text=Quero: {row['nome']}")
                st.markdown('</div>', unsafe_allow_html=True)

# --- ADMIN ---
else:
    senha = st.text_input("Senha", type="password")
    if senha == "suasenha123":
        t1, t2, t3 = st.tabs(["➕ Novo Produto", "🗑️ Gerenciar", "💾 Backup"])
        
        with t1:
            st.write("### Cadastro de Produto")
            
            # --- NOVA LÓGICA DE CATEGORIA ---
            exist_cats = sorted(df["categoria"].unique().astype(str).tolist()) if not df.empty else []
            exist_subs = sorted(df["subcategoria"].unique().astype(str).tolist()) if not df.empty else []

            with st.expander("📂 Gerenciar Categorias (Criar novas aqui)", expanded=True):
                col_c1, col_c2 = st.columns(2)
                nova_cat_input = col_c1.text_input("Nova Categoria (ex: Camisas)")
                nova_sub_input = col_c2.text_input("Nova Subcategoria (ex: Gola Polo)")
                st.caption("Dica: Digite acima apenas se a categoria que você quer ainda não existir na lista abaixo.")

            st.divider()

            with st.form("form_v3", clear_on_submit=True):
                nome = st.text_input("Nome do Produto")
                preco = st.number_input("Preço", min_value=0.0)
                
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    # Se o usuário digitou uma nova, ela tem prioridade
                    cat_final = st.selectbox("Usar Categoria existente:", ["Selecione..."] + exist_cats) if not nova_cat_input else nova_cat_input
                with col_f2:
                    sub_final = st.selectbox("Usar Subcategoria existente:", ["Selecione..."] + exist_subs) if not nova_sub_input else nova_sub_input
                
                desc = st.text_area("Descrição")
                foto = st.file_uploader("Foto", type=['jpg', 'png', 'jpeg'])
                
                if st.form_submit_button("✅ SALVAR PRODUTO"):
                    # Validação
                    cat_para_salvar = nova_cat_input if nova_cat_input else cat_final
                    sub_para_salvar = nova_sub_input if nova_sub_input else sub_final
                    
                    if nome and foto and cat_para_salvar != "Selecione...":
                        nome_arq = f"{datetime.now().timestamp()}_{foto.name}".replace(" ","_")
                        with open(f"images/{nome_arq}", "wb") as f: f.write(foto.getbuffer())
                        
                        novo = pd.DataFrame([{"nome": nome, "preco": preco, "imagens": nome_arq, 
                                             "categoria": cat_para_salvar, "subcategoria": sub_para_salvar, "descricao": desc}])
                        df = pd.concat([df, novo], ignore_index=True)
                        df.to_csv("produtos.csv", index=False)
                        st.success(f"Sucesso! Produto cadastrado em: {cat_para_salvar}")
                        st.rerun()
                    else:
                        st.error("Erro: Verifique se preencheu o Nome, a Foto e selecionou uma Categoria.")

        with t2:
            if not df.empty:
                for i, row in df.iterrows():
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"**{row['nome']}** ({row['categoria']} - {row['subcategoria']})")
                    if c2.button("Excluir", key=f"d_{i}"):
                        df = df.drop(i)
                        df.to_csv("produtos.csv", index=False)
                        st.rerun()
        
        with t3: # Backup
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 BAIXAR BACKUP", csv, "backup.csv", "text/csv")
            up = st.file_uploader("Restaurar", type="csv")
            if st.button("RESTAURAR") and up:
                pd.read_csv(up).to_csv("produtos.csv", index=False)
                st.rerun()
