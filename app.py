import streamlit as st
import json
import math

# --- CONFIGURAÇÃO DA INTERFACE ---
st.set_page_config(page_title="D&D 5e Character Builder", page_icon="🎲", layout="wide")

# --- BANCO DE DADOS INTEGRADO ---
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
    tabela = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
    return tabela.get(valor, 0)

# --- APP ---
st.title("🧙‍♂️ Gerador de Personagem Oficial (LDJ/XGE/TCOE/MPMM)")
st.markdown("Sistema de Validação e Autorização de Fichas D&D 5e")

if not db:
    st.error("Erro: Arquivo 'database.json' não encontrado no repositório.")
    st.stop()

# --- 1. INFORMAÇÕES DO PERSONAGEM (LIVRO BASE) ---
st.header("1. Informações do Personagem")
col_n1, col_n2, col_n3 = st.columns([2, 1, 1])

with col_n1:
    nome = st.text_input("Nome do Personagem", placeholder="Ex: Viconas del'Armgo")
with col_n2:
    alinhamento = st.selectbox("Alinhamento", [
        "Leal e Bom", "Neutro e Bom", "Caótico e Bom",
        "Leal e Neutro", "Neutro", "Caótico e Neutro",
        "Leal e Mau", "Neutro e Mau", "Caótico e Mau"
    ])
with col_n3:
    xp = st.number_input("Experiência (XP)", min_value=0, value=0, step=100)

col_n4, col_n5, col_n6 = st.columns(3)
with col_n4:
    raca_sel = st.selectbox("Raça", list(db['racas'].keys()))
with col_n5:
    classe_sel = st.selectbox("Classe", list(db['classes'].keys()))
with col_n6:
    antecedente = st.selectbox("Antecedente (Background)", [
        "Acólito", "Charlatão", "Criminoso", "Artista", "Herói do Povo", 
        "Artesão de Guilda", "Eremita", "Nobre", "Outlander", "Sábio", "Marinheiro", "Soldado", "Órfão"
    ])

sub_sel = st.selectbox("Subclasse (Arquétipo)", db['classes'][classe_sel]['subclasses'])

st.divider()

# --- 2. ATRIBUTOS (VALORES ÚNICOS E POINT BUY) ---
st.header("2. Atributos Base")
st.info("Regra Especial: Cada valor base deve ser ÚNICO (8 a 15). O total de pontos permitidos é 27.")

bonus_raca = db['racas'][raca_sel]['bonus']
finais = {}
valores_base_escolhidos = []

atr_cols = st.columns(6)
for i, status in enumerate(["FOR", "DES", "CON", "INT", "SAB", "CAR"]):
    with atr_cols[i]:
        # Inicializa com valores diferentes (8, 9, 10...) para evitar erro imediato de duplicata
        base = st.number_input(status, 8, 15, 8 + i, key=f"base_{status}")
        valores_base_escolhidos.append(base)
        
        total = base + bonus_raca.get(status, 0)
        mod = calc_mod(total)
        finais[status] = {"total": total, "mod": mod, "base": base}
        
        st.metric(label="Total Final", value=total, delta=f"Mod: {mod}")

# Validações de Atributos
tem_duplicatas = len(valores_base_escolhidos) != len(set(valores_base_escolhidos))
custo_total = sum([calcular_custo_point_buy(v) for v in valores_base_escolhidos])

if tem_duplicatas:
    st.error("⚠️ ERRO: Você repetiu valores! Cada atributo deve ter um valor base diferente.")
    autorizado = False
elif custo_total > 27:
    st.error(f"⚠️ LIMITE DE PONTOS EXCEDIDO: Você usou {custo_total}/27 pontos.")
    autorizado = False
else:
    st.success(f"✅ Atributos Autorizados! Pontos usados: {custo_total}/27.")
    autorizado = True

st.divider()

# --- 3. ESPECIALIZAÇÕES ---
st.header("3. Magias, Truques e Talentos")
col_t, col_m, col_f = st.columns(3)

with col_t:
    truques_list = db['classes'][classe_sel]['truques']
    truques_sel = st.multiselect("Selecione seus Truques", truques_list) if truques_list else st.info("Sem truques.")

with col_m:
    magias_list = db['classes'][classe_sel]['magias_n1']
    magias_sel = st.multiselect("Selecione Magias Nível 1", magias_list) if magias_list else st.info("Sem magias nível 1.")

with col_f:
    talento_sel = st.selectbox("Escolha um Talento", ["Nenhum"] + db['talentos'])

st.divider()

# --- 4. GERAÇÃO DA FICHA ---
if st.button("🔥 AUTORIZAR E GERAR FICHA", disabled=not autorizado):
    st.balloons()
    
    st.header(f"📜 Ficha: {nome if nome else 'Herói Sem Nome'}")
    st.write(f"**{raca_sel} {classe_sel} ({sub_sel})** | {alinhamento} | {antecedente} | XP: {xp}")

    res1, res2 = st.columns(2)
    with res1:
        st.write("### 📊 Atributos e Modificadores")
        for k, v in finais.items():
            mod_txt = f"+{v['mod']}" if v['mod'] >= 0 else str(v['mod'])
            st.write(f"**{k}:** {v['total']} (Base {v['base']}) | Modificador: `{mod_txt}`")

    with res2:
        st.write("### ✨ Poderes e Magias")
        st.write("**Habilidades Raciais:**")
        for hab in db['racas'][raca_sel]['habilidades']:
            st.write(f"✅ {hab}")
        
        if talento_sel != "Nenhum": st.write(f"**Talento:** {talento_sel}")
        if truques_sel: st.write(f"**Truques:** {', '.join(truques_sel)}")
        if magias_sel: st.write(f"**Magias:** {', '.join(magias_sel)}")

    # Botão de Exportação
    txt_ficha = f"FICHA OFICIAL D&D 5e\n\nNome: {nome}\nRaça/Classe: {raca_sel} {classe_sel}\nAlinhamento: {alinhamento}\nAntecedente: {antecedente}\n\nATRIBUTOS:\n"
    for k, v in finais.items():
        txt_ficha += f"{k}: {v['total']} ({v['mod']})\n"
    
    st.download_button("📥 Baixar Ficha (.txt)", txt_ficha, file_name=f"ficha_{nome}.txt")
