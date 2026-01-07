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

# --- APP ---
st.title("🧙‍♂️ Gerador de Personagem Oficial (LDJ/XGE/TCOE/MPMM)")

if not db:
    st.error("Erro: 'database.json' não encontrado!")
    st.stop()

# 1. IDENTIDADE
st.header("1. Informações Básicas")
c1, c2, c3 = st.columns([2, 1, 1])
with c1: nome = st.text_input("Nome do Personagem")
with c2: alinhamento = st.selectbox("Alinhamento", ["Leal/Bom", "Neutro/Bom", "Caótico/Bom", "Leal/Neutro", "Neutro", "Caótico/Neutro", "Leal/Mau", "Neutro/Mau", "Caótico/Mau"])
with c3: antecedente = st.selectbox("Antecedente", ["Acólito", "Criminoso", "Herói do Povo", "Nobre", "Sábio", "Soldado", "Órfão"])

c4, c5, c6 = st.columns(3)
with c4: raca_sel = st.selectbox("Raça", list(db['racas'].keys()))
with c5: classe_sel = st.selectbox("Classe", list(db['classes'].keys()))
with c6: sub_sel = st.selectbox("Subclasse", db['classes'][classe_sel]['subclasses'])

st.divider()

# 2. ATRIBUTOS
st.header("2. Atributos (27 Pontos / Sem Repetição)")

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

# 3. STATUS DE COMBATE (CORREÇÃO DO ERRO)
st.header("3. Status de Combate")
mod_des = finais["DES"]["mod"]
mod_con = finais["CON"]["mod"]
mod_sab = finais["SAB"]["mod"]

# Usando as chaves corrigidas do JSON
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
    st.info(f"✨ **Conjurador ({att_magia}):** CD de Magia: {8 + 2 + mod_magia} | Bônus: +{2 + mod_magia}")

st.divider()

# 4. BOTÃO FINAL
if st.button("🔥 GERAR FICHA", disabled=not autorizado):
    st.balloons()
    st.success("Ficha Autorizada!")
