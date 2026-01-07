import streamlit as st
import json

# Simulação da base de dados (em um projeto real, você carrega o JSON)
with open('database.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

st.title("🧙‍♂️ Validador de Fichas D&D 5e")

# Interface de Entrada
raca = st.selectbox("Escolha a Raça", db['racas'])
classe = st.selectbox("Escolha a Classe", db['classes'])
nivel = st.number_input("Nível", min_value=1, max_value=20, value=1)
magias_input = st.text_area("Digite as magias (separadas por vírgula)")

if st.button("Gerar e Autorizar Ficha"):
    # PROMPT PARA A IA (Configuração do Sistema)
    prompt_sistema = f"""
    Você é um validador de D&D 5e estrito. 
    Fontes permitidas: {db['livros_permitidos']}.
    O usuário quer um {raca} {classe} nível {nivel}.
    Magias escolhidas: {magias_input}.
    
    Verifique:
    1. Se as magias pertencem à lista da classe {classe}.
    2. Se o nível das magias é compatível com o nível {nivel}.
    3. Se os bônus raciais de {raca} estão corretos conforme os livros.
    
    Retorne a ficha formatada ou aponte os erros de 'Não Autorizado'.
    """
    
    st.info("Enviando para a IA validar...")
    # Aqui você conectaria a API do Gemini ou OpenAI
    st.markdown(f"### Resultado da Verificação:\n(A IA processaria o prompt aqui)")
