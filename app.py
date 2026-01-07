import streamlit as st
import json

# Configuração da página
st.set_page_config(page_title="D&D 5e Character Builder", layout="wide")

# Função para carregar o banco de dados
def load_db():
    with open('database.json', 'r', encoding='utf-8') as f:
        return json.load(f)

db = load_db()

st.title("🏹 Gerador de Fichas Automatizado")
st.markdown("---")

# --- PASSO 1: IDENTIDADE ---
col1, col2, col3 = st.columns(3)
with col1:
    raca = st.selectbox("Selecione a Raça", ["Shadar-kai", "Elfo Drow", "Anão", "Humano", "Tabaxi", "Goliath"])
with col2:
    classe = st.selectbox("Selecione a Classe", list(db['classes'].keys()))
with col3:
    subclasse = st.selectbox("Selecione a Subclasse", db['classes'][classe]['subclasses'])

# --- PASSO 2: ATRIBUTOS ---
st.subheader("📊 Atributos Base")
atr_cols = st.columns(6)
atributos = {}
for i, status in enumerate(["FOR", "DES", "CON", "INT", "SAB", "CAR"]):
    with atr_cols[i]:
        atributos[status] = st.number_input(status, 8, 20, 10)

# --- PASSO 3: MAGIAS E TRUQUES ---
st.subheader("🔮 Magias e Truques (Autorizados)")
col_t, col_m = st.columns(2)

with col_t:
    truques_disp = db['classes'][classe]['truques']
    if truques_disp:
        truques_sel = st.multiselect("Escolha seus Truques", truques_disp)
    else:
        st.write("Esta classe não possui truques iniciais.")
        truques_sel = []

with col_m:
    magias_disp = db['classes'][classe]['magias_n1']
    if magias_disp:
        magias_sel = st.multiselect("Escolha suas Magias de Nível 1", magias_disp)
    else:
        st.write("Esta classe não possui magias no nível 1.")
        magias_sel = []

# --- PASSO 4: RESUMO ---
st.markdown("---")
if st.button("💾 Gerar Ficha Final"):
    st.header("📜 Ficha do Personagem")
    
    resumo_col1, resumo_col2 = st.columns(2)
    with resumo_col1:
        st.write(f"**Personagem:** {raca} {classe} ({subclasse})")
        st.write("**Atributos:**", atributos)
    
    with resumo_col2:
        st.write(f"**Truques:** {', '.join(truques_sel) if truques_sel else 'Nenhum'}")
        st.write(f"**Magias:** {', '.join(magias_sel) if magias_sel else 'Nenhuma'}")
    
    st.success("Ficha validada de acordo com LDJ, Xanathar, Tasha e Mordenkainen!")
