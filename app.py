import streamlit as st
import json
import math

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="D&D 5e Character Builder", layout="wide")

@st.cache_data
def load_db():
    try:
        with open('database.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

db = load_db()

def calc_mod(v):
    return math.floor((v - 10) / 2)

def calc_custo(v):
    tabela = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
    return tabela.get(v, 0)

# --- INTERFACE ---
st.title("🧙‍♂️ Gerador de Personagem Oficial (LDJ/XGE/TCOE/MPMM)")

if not db:
    st.error("Erro: 'database.json' não encontrado!")
    st.stop()

# 1. INFORMAÇÕES BÁSICAS
st.header("1. Informações do Personagem")
c_id1, c_id2, c_id3 = st.columns([2, 1, 1])
with c_id1: nome = st.text_input("Nome do Personagem")
with c_id2: alinhamento = st.selectbox("Alinhamento", ["Leal/Bom", "Neutro/Bom", "Caótico/Bom", "Leal/Neutro", "Neutro", "Caótico/Neutro", "Leal/Mau", "Neutro/Mau", "Caótico/Mau"])
with c_id3: antecedente = st.selectbox("Antecedente", ["Acólito", "Criminoso", "Herói do Povo", "Nobre", "Sábio", "Soldado", "Órfão"])

c_rc1, c_rc2, c_rc3 = st.columns(3)
with c_rc1: raca_sel = st.selectbox("Raça", list(db['racas'].keys()))
with c_rc2: classe_sel = st.selectbox("Classe", list(db['classes'].keys()))
with c_rc3: sub_sel = st.selectbox("Subclasse", db['classes'][classe_sel]['subclasses'])

st.divider()

# 2. ATRIBUTOS (VALORES ÚNICOS E POINT BUY)
st.header("2. Atributos Base (27 Pontos / Sem Repetição)")
bonus_raca = db['racas'][raca_sel]['bonus']
finais = {}
selecionados = []

cols = st.columns(6)
for i, status in enumerate(["FOR", "DES", "CON", "INT", "SAB", "CAR"]):
    with cols[i]:
        base = st.number_input(status, 8, 15, 8+i, key=f"b_{status}")
        selecionados.append(base)
        total = base + bonus_raca.get(status, 0)
        mod = calc_mod(total)
        finais[status] = {"total": total, "mod": mod}
        st.metric(label="Total", value=total, delta=f"Mod: {mod}")

# Validações de Atributos
duplicados = len(selecionados) != len(set(selecionados))
custo_total = sum([calc_custo(v) for v in selecionados])

if duplicados:
    st.error("❌ Erro: Não repita os valores base!")
    autorizado = False
elif custo_total > 27:
    st.error(f"❌ Erro: Custo {custo_total}/27 excedido!")
    autorizado = False
else:
    st.success(f"✅ Atributos Válidos ({custo_total}/27)")
    autorizado = True

st.divider()

# 3. STATUS DE COMBATE (CÁLCULOS COM CHAVES DO JSON)
st.header("3. Status de Combate")
mod_des = finais["DES"]["mod"]
mod_con = finais["CON"]["mod"]
mod_sab = finais["SAB"]["mod"]

# Usando dado_vida e att_magia definidos no JSON
pv_inicial = db['classes'][classe_sel]['dado_vida'] + mod_con
ca_base = 10 + mod_des
percepcao_p = 10 + mod_sab
att_magia = db['classes'][classe_sel]['att_magia']
mod_magia = finais[att_magia]["mod"]

sc1, sc2, sc3, sc4 = st.columns(4)
sc1.metric("Pontos de Vida (PV)", pv_inicial)
sc2.metric("Classe de Armadura", ca_base)
sc3.metric("Iniciativa", f"+{mod_des}")
sc4.metric("Percepção Passiva", percepcao_p)

if db['classes'][classe_sel]['magias_n1']:
    st.info(f"✨ **Conjurador ({att_magia}):** CD de Magia: {8 + 2 + mod_magia} | Bônus de Ataque: +{2 + mod_magia}")

st.divider()

# 4. ESPECIALIZAÇÕES E GERAÇÃO
st.header("4. Magias e Talentos")
t_col, m_col, f_col = st.columns(3)
with t_col: t_sel = st.multiselect("Truques", db['classes'][classe_sel]['truques'])
with m_col: m_sel = st.multiselect("Magias Nível 1", db['classes'][classe_sel]['magias_n1'])
with f_col: f_sel = st.selectbox("Talento", ["Nenhum"] + db['talentos'])

if st.button("🔥 GERAR FICHA COMPLETA", disabled=not autorizado):
    st.balloons()
    st.success("Ficha Autorizada de acordo com as Regras Oficiais!")
