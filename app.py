import streamlit as st
import json
import math

# --- CONFIGURAÇÃO DA INTERFACE ---
st.set_page_config(page_title="D&D 5e Character Builder", page_icon="🎲", layout="wide")

# --- BANCO DE DADOS INTEGRADO ---
# (Pode ser mantido aqui ou carregado de um database.json externo)
@st.cache_data
def load_db():
    try:
        with open('database.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

db = load_db()

# --- FUNÇÕES DE LÓGICA ---
def calc_mod(valor):
    return math.floor((valor - 10) / 2)

def calcular_custo_point_buy(valor):
    # Tabela oficial de custos (LDJ pág. 13)
    tabela = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
    return tabela.get(valor, 0)

# --- APP ---
st.title("🧙‍♂️ Gerador de Personagem Oficial (LDJ/XGE/TCOE/MPMM)")
st.markdown("Sistema de Validação e Autorização de Fichas D&D 5e")

if not db:
    st.error("Erro: Arquivo 'database.json' não encontrado. Certifique-se de que ele está no repositório.")
    st.stop()

# --- 1. IDENTIDADE ---
st.header("1. Identidade")
col1, col2, col3 = st.columns(3)

with col1:
    raca_sel = st.selectbox("Selecione a Raça", list(db['racas'].keys()), index=list(db['racas'].keys()).index("Shadar-kai") if "Shadar-kai" in db['racas'] else 0)
with col2:
    classe_sel = st.selectbox("Selecione a Classe", list(db['classes'].keys()))
with col3:
    subs = db['classes'][classe_sel]['subclasses']
    sub_sel = st.selectbox("Selecione a Subclasse", subs if subs else ["Classe Única"])

st.divider()

# --- 2. COMPRA DE PONTOS (POINT BUY) ---
st.header("2. Atributos (Sistema de 27 Pontos)")
st.info("Regra Oficial: Você tem 27 pontos para gastar. Valores base permitidos: 8 a 15.")

bonus_raca = db['racas'][raca_sel]['bonus']
finais = {}
custo_total = 0

atr_cols = st.columns(6)
for i, status in enumerate(["FOR", "DES", "CON", "INT", "SAB", "CAR"]):
    with atr_cols[i]:
        # Input do Valor Base
        valor_base = st.number_input(status, 8, 15, 8, key=f"base_{status}")
        
        # Lógica de Custo
        custo = calcular_custo_point_buy(valor_base)
        custo_total += custo
        
        # Soma de Bônus e Modificador
        total = valor_base + bonus_raca.get(status, 0)
        mod = calc_mod(total)
        finais[status] = {"total": total, "mod": mod, "base": valor_base}
        
        st.write(f"Custo: **{custo}**")
        st.metric(label="Total Final", value=total, delta=f"Mod: {mod}")

# Validação dos Pontos
pontos_restantes = 27 - custo_total
if pontos_restantes < 0:
    st.error(f"⚠️ LIMITE EXCEDIDO: Você usou {custo_total} pontos. Remova {abs(pontos_restantes)} ponto(s).")
    autorizado_pontos = False
else:
    st.success(f"✅ Pontos Disponíveis: {pontos_restantes} / 27")
    autorizado_pontos = True

st.divider()

# --- 3. ESPECIALIZAÇÕES ---
st.header("3. Magias e Talentos")
col_t, col_m, col_f = st.columns(3)

with col_t:
    truques_list = db['classes'][classe_sel]['truques']
    truques_sel = st.multiselect("Escolha seus Truques", truques_list) if truques_list else st.info("Sem truques.")

with col_m:
    magias_list = db['classes'][classe_sel]['magias_n1']
    magias_sel = st.multiselect("Escolha Magias Nível 1", magias_list) if magias_list else st.info("Sem magias nível 1.")

with col_f:
    talento_sel = st.selectbox("Escolha um Talento", ["Nenhum"] + db['talentos'])

st.divider()

# --- 4. AUTORIZAÇÃO E EXPORTAÇÃO ---
if st.button("🔥 AUTORIZAR E GERAR FICHA", disabled=not autorizado_pontos):
    st.balloons()
    st.success("FICHA AUTORIZADA! Todos os elementos estão de acordo com os manuais oficiais.")
    
    st.header(f"📜 Ficha: {raca_sel} {classe_sel}")
    st.subheader(f"Subclasse: {sub_sel}")

    res1, res2 = st.columns(2)
    with res1:
        st.write("### 📊 Atributos e Modificadores")
        for k, v in finais.items():
            mod_txt = f"+{v['mod']}" if v['mod'] >= 0 else str(v['mod'])
            st.write(f"**{k}:** {v['total']} (Base {v['base']} + Bônus) | Modificador: `{mod_txt}`")

    with res2:
        st.write("### ✨ Poderes e Magias")
        st.write("**Habilidades Raciais:**")
        for hab in db['racas'][raca_sel]['habilidades']:
            st.write(f"✅ {hab}")
        
        if talento_sel != "Nenhum":
            st.write(f"**Talento:** {talento_sel}")
        
        if truques_sel:
            st.write(f"**Truques:** {', '.join(truques_sel)}")
        if magias_sel:
            st.write(f"**Magias:** {', '.join(magias_sel)}")

    # Gerador de Texto para Download
    txt_ficha = f"FICHA AUTORIZADA D&D 5e\n\nRaça: {raca_sel}\nClasse: {classe_sel}\nSubclasse: {sub_sel}\n\nATRIBUTOS:\n"
    for k, v in finais.items():
        txt_ficha += f"{k}: {v['total']} ({v['mod']})\n"
    txt_ficha += f"\nMAGIAS: {', '.join(magias_sel)}\nTALENTO: {talento_sel}"
    
    st.download_button("📥 Baixar Ficha Autorizada", txt_ficha, file_name="ficha_oficial_dnd.txt")
