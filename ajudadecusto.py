import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import date
import locale

# Configurar locale para português brasileiro
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR')
    except:
        pass

# Função para converter valor para extenso
def valor_para_extenso(valor_str):
    # Remover R$ e espaços, converter para float
    valor_str = valor_str.replace('R$', '').replace(' ', '').strip()
    
    # Verificar se tem vírgula decimal
    if ',' in valor_str:
        partes = valor_str.split(',')
        reais = partes[0]
        centavos = partes[1] if len(partes) > 1 else '00'
    else:
        reais = valor_str
        centavos = '00'
    
    # Converter reais para número
    reais_int = int(reais) if reais else 0
    
    # Unidades
    unidades = ['', 'um', 'dois', 'três', 'quatro', 'cinco', 'seis', 'sete', 'oito', 'nove']
    
    # De 10 a 19
    dez_a_dezenove = ['dez', 'onze', 'doze', 'treze', 'catorze', 'quinze', 'dezesseis', 'dezessete', 'dezoito', 'dezenove']
    
    # Dezenas
    dezenas = ['', '', 'vinte', 'trinta', 'quarenta', 'cinquenta', 'sessenta', 'setenta', 'oitenta', 'noventa']
    
    # Centenas
    centenas = ['', 'cento', 'duzentos', 'trezentos', 'quatrocentos', 'quinhentos', 'seiscentos', 'setecentos', 'oitocentos', 'novecentos']
    
    extenso = []
    
    # Converter centavos
    centavos_int = int(centavos) if centavos else 0
    
    # Converter reais
    if reais_int == 0:
        extenso_reais = 'zero'
    elif reais_int == 1:
        extenso_reais = 'um'
    else:
        # Para valores maiores, usar uma abordagem simplificada
        if reais_int < 1000:
            # Para valores até 999
            if reais_int >= 100:
                centena = reais_int // 100
                resto = reais_int % 100
                if centena == 1 and resto == 0:
                    extenso.append('cem')
                else:
                    extenso.append(centenas[centena])
                
                if resto > 0:
                    extenso.append('e')
                    reais_int = resto
                    centena = 0
            
            if reais_int >= 20:
                dezena = reais_int // 10
                unidade = reais_int % 10
                extenso.append(dezenas[dezena])
                if unidade > 0:
                    extenso.append('e')
                    extenso.append(unidades[unidade])
            elif reais_int >= 10:
                extenso.append(dez_a_dezenove[reais_int - 10])
            elif reais_int > 0:
                extenso.append(unidades[reais_int])
            
            extenso_reais = ' '.join(extenso)
        else:
            # Para valores maiores, usar uma representação simplificada
            extenso_reais = f'{reais_int}'
    
    # Montar resultado final
    resultado = f'{extenso_reais} real'
    if reais_int != 1:
        resultado = 'reais'
    
    if centavos_int > 0:
        resultado += f' e {centavos_int:02d}/100'
    
    return resultado

# Função para calcular valor total
def calcular_valor_total(valor_str, quantidade):
    try:
        # Converter valor string para float
        valor_str = valor_str.replace('R$', '').replace(' ', '').strip()
        if ',' in valor_str:
            valor_str = valor_str.replace('.', '').replace(',', '.')
        valor_float = float(valor_str)
        total = valor_float * quantidade
        return total
    except:
        return 0.0

# Configuração da Página
st.set_page_config(page_title="Gerador de Ajuda de Custo", layout="wide")

def gerar_pdf(lista_nomes, data_selecionada, valor):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=False)  # Desativar quebra automática
    
    # Formatar data em português
    meses = {
        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
        5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
        9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
    }
    
    dia = data_selecionada.day
    mes = meses[data_selecionada.month]
    ano = data_selecionada.year
    data_extenso = f"{dia} de {mes} de {ano}"
    
    # Converter valor para extenso
    valor_extenso = valor_para_extenso(valor)
    
    # Configurações da tabela
    margem_esquerda = 10
    largura_tabela = 190
    altura_linha = 10
    
    # Calcular quantos nomes cabem em uma página
    # Posição inicial Y após o cabeçalho
    y_pos_inicial = 65  # Aproximadamente onde começa a tabela após cabeçalho
    
    # Altura máxima da página
    altura_maxima_pagina = 280
    linhas_por_pagina = (altura_maxima_pagina - y_pos_inicial) // altura_linha
    
    # Dividir nomes por páginas
    paginas_nomes = []
    for i in range(0, len(lista_nomes), linhas_por_pagina):
        paginas_nomes.append(lista_nomes[i:i + linhas_por_pagina])
    
    for pagina_num, nomes_pagina in enumerate(paginas_nomes):
        pdf.add_page()
        
        # Cabeçalho exatamente como no modelo (apenas na primeira página)
        if pagina_num == 0:
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "Ajuda de custo estabelecido por CCT do SESSEPE", ln=True, align='C')
            pdf.cell(0, 8, "A J J EMPRESA DE ALIMENTOS - CNPJ. 08.071.185/0001-37", ln=True, align='C')
            
            pdf.ln(15)  # Espaço após cabeçalho
            
            # Linha com valor e data - FORMATO EXATO DO MODELO
            pdf.set_font("Arial", '', 11)
            
            # R$ e valor - alinhado à esquerda
            pdf.set_x(10)
            pdf.cell(40, 8, f"R$: {valor}")
            
            # Adicionar valor por extenso entre parênteses
            pdf.set_x(90)  # Posição para a data
            pdf.cell(0, 8, f"Referente ao dia {data_extenso}", ln=True)
            
            # Linha com valor por extenso
            pdf.set_x(10)
            pdf.set_font("Arial", 'I', 10)
            pdf.cell(0, 8, f"({valor_extenso})", ln=True)
            
            pdf.ln(5)  # Espaço
            
            # Texto de reconhecimento - igual ao modelo
            pdf.set_font("Arial", '', 11)
            pdf.multi_cell(0, 8, "Assino e reconheço que a empresa quitou este valor na data citada.")
            
            pdf.ln(10)  # Espaço antes das assinaturas
            
            y_pos = pdf.get_y()  # Posição atual após cabeçalho
        else:
            # Para páginas seguintes, começar no topo
            y_pos = 20
        
        # Criar uma linha para cada funcionário na página
        for i, nome in enumerate(nomes_pagina):
            # Calcular posição Y
            y_atual = y_pos + (i * altura_linha)
            
            # Desenhar linha horizontal superior da célula (borda superior)
            pdf.line(margem_esquerda, y_atual, margem_esquerda + largura_tabela, y_atual)
            
            # Desenhar linha horizontal inferior da célula (borda inferior)
            pdf.line(margem_esquerda, y_atual + altura_linha, margem_esquerda + largura_tabela, y_atual + altura_linha)
            
            # Desenhar linha vertical esquerda (borda esquerda)
            pdf.line(margem_esquerda, y_atual, margem_esquerda, y_atual + altura_linha)
            
            # Desenhar linha vertical direita (borda direita)
            pdf.line(margem_esquerda + largura_tabela, y_atual, margem_esquerda + largura_tabela, y_atual + altura_linha)
            
            # Adicionar nome do funcionário na linha (lado esquerdo)
            pdf.set_font("Arial", '', 10)
            pdf.set_xy(margem_esquerda + 5, y_atual + 3)
            # Cortar nome se for muito longo
            nome_exibir = nome[:40] if len(nome) > 40 else nome  # Reduzido para 40 caracteres
            pdf.cell(80, 5, nome_exibir, align='L')  # Largura reduzida para 80mm
            
            # Adicionar linha divisória interna (traço) BEM mais à esquerda
            # Posição do traço: ~90mm da margem esquerda (logo após o nome)
            posicao_traco = margem_esquerda + 85
            pdf.line(posicao_traco, y_atual, posicao_traco, y_atual + altura_linha)
            
            # Adicionar "ASS:" padronizado LOGO após o traço - BEM mais à esquerda
            pdf.set_font("Arial", '', 10)
            pdf.set_xy(posicao_traco + 2, y_atual + 3)  # Apenas 2mm após o traço
            pdf.cell(15, 5, "ASS:", align='L')

    # Retornar como bytes
    pdf_output = pdf.output(dest='S')
    if isinstance(pdf_output, str):
        return pdf_output.encode('latin-1')
    return bytes(pdf_output)

# --- INTERFACE STREAMLIT ---
st.title("💵 Ajuda de Custo - AJJ")

# Dados dos funcionários padrão
funcionarios_padrao = [
    "ABINOAN RINALDO DE MENEZES", "ADRIANA MARIA FRANCISCO DE BARROS", "AILTON VICENTE DA SILVA",
    "ALISSON FELIPE DA SILVA", "ALUIZIO FERREIRA DA SILVA", "ANDRES RICARDO MARQUES MARMANILLO", "ANDRESSA DELMIRO SOARES", "AUGUSTO GALDINO DO BOMFIM",
    "BEATRIZ ASSIS DE SANTANA", "BETANIA MARTINS DOS SANTOS", "BIANCA PRAZERES DA SILVA", "DANIEL RIBEIRO MENDES DA SILVA",
    "EDINALDO FERREIRA DA SILVA", "EDUARDO ANTONIO DO NASCIMENTO", "EDUARDO QUEIROZ DA SILVA",
    "EDVALDO RODRIGUES DA SILVA", "EUGENIO RIBEIRO DA SILVA",
    "EVALDO ALBUQUERQUE DE OLIVEIRA", "FABIANA RODRIGUES DOS SANTOS SOUZA", "FABIANO FAUSTINO SANTOS DE SOUZA",
    "FERNANDO JOSE SOARES DO NASCIMENTO", "GEANE BEZERRA DE ALBUQUERQUE", "GLEYCE SALETE DOS SANTOS SILVA",
    "IGOR ANDRE PEREIRA DE ALBUQUERQUE", "IGOR ANDRE SALUSTIANO BARROS SILVA", "ILVACI RIBEIRO NASCIMENTO",
    "ISAAC ALVES BOTELHO", "ISRAEL SILVA DE SANTANA", "IVANEIDE MARIA DA SILVA", "IZAIAS FRANCISCO DA SILVA",
    "JAILSON FRANCISCO PEREIRA", "JEFFERSON KELWES BARBOSA", "JESSIKA BRAZ DA SILVA",
    "JOAO FIDELIS DA SILVA FILHO", "JONAS GABRIEL LEANDRO DA SILVA","JOSE GABRYEL DA SILVA ALBUQUERQUE",
    "JULIANA FERREIRA DE LIMA SILVA", "KALLYNE VITÓRIA DA SILVA", "LEISON GOMES DA SILVA",
    "LEONARDO CHAGAS DA SILVA", "MANOEL CARLOS DA SILVA", "MARIA DO ROSARIO RIBEIRO DA SILVA",
    "MARIS CLARA PEREIRA", "MIKAEL FERREIRA DA SILVA","RAISSA DANIELLE J. DA SILVA", "RILDO GUEDES DE ARAUJO", "ROBSON LEANDRO DA SILVA",
    "ROMULO DA SILVA ANDRADE", "RUBIA BRUNA DA SILVA", "SINEIA MARIA DA SILVA","SUELEN SANTOS DE MOURA", "SUZANA FERREIRA DE LIMA SILVA",
    "TIAGO ASSIS DE SANTANA", "TUANA MONIQUE TIMOTEO DE SOUZA SILVA", "VANESSA CORREIA DOS SANTOS",
    "VITÓRIA REGINA PEREIRA", "YSLA LARISSA DE BARROS"
]

# Inicializar lista de funcionários na session state
if 'funcionarios' not in st.session_state:
    st.session_state.funcionarios = funcionarios_padrao.copy()

# COLUNAS INVERTIDAS: primeiro seleção, depois valor e data
col1, col2 = st.columns(2)

with col1:
    st.write("### Selecione os Funcionários")
    selecionados = []
    
    # Opção de selecionar todos
    selecionar_todos = st.checkbox("Selecionar Todos")
    
    if selecionar_todos:
        selecionados = st.session_state.funcionarios
        # Mostrar quantos foram selecionados
        st.info(f"✅ {len(st.session_state.funcionarios)} funcionários selecionados")
    else:
        # Mostrar checkboxes em um container com scroll
        with st.container():
            for f in st.session_state.funcionarios:
                if st.checkbox(f, key=f):
                    selecionados.append(f)
    
    # Mostrar contador de funcionários selecionados
    st.metric("Funcionários selecionados", len(selecionados))

with col2:
    st.write("### Configurações do Documento")
    
    valor_input = st.text_input("💸 Digite o valor (Ex: 52,00):", "0,00")
    data_input = st.date_input(
        "🗓️ Selecione a data", 
        date.today(),
        format="DD/MM/YYYY"
    )
    
    # --- BOTÃO PARA INSERIR FUNCIONÁRIO MANUALMENTE ---
    st.write("---")
    st.write("### Adicionar Funcionário Manualmente")
    
    # Inicializar estado para o novo funcionário
    if 'novo_funcionario' not in st.session_state:
        st.session_state.novo_funcionario = ""
    
    # Campo para digitar o nome do funcionário
    novo_funcionario_input = st.text_input(
        "Digite o nome do funcionário:",
        placeholder="Ex: JOÃO DA SILVA",
        key="input_novo_funcionario"
    )
    
    # Botão para adicionar
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("➕ Inserir Funcionário", use_container_width=True):
            if novo_funcionario_input and novo_funcionario_input.strip():
                # Adicionar à lista de funcionários
                nome_formatado = novo_funcionario_input.strip().upper()
                
                # Verificar se já existe
                if nome_formatado not in st.session_state.funcionarios:
                    st.session_state.funcionarios.append(nome_formatado)
                    st.success(f"✅ {nome_formatado} adicionado à lista!")
                    
                    # Limpar o campo de input
                    st.session_state.input_novo_funcionario = ""
                    
                    # Rerun para atualizar a interface
                    st.rerun()
                else:
                    st.warning("⚠️ Este funcionário já está na lista!")
            else:
                st.warning("⚠️ Por favor, digite um nome válido.")
    
    with col_btn2:
        if st.button("🔄 Limpar Lista", use_container_width=True):
            # Resetar para a lista padrão
            st.session_state.funcionarios = funcionarios_padrao.copy()
            st.success("✅ Lista resetada para os funcionários padrão!")
            st.rerun()
    
    # Mostrar lista atual de funcionários (apenas últimos 5 adicionados)
    if len(st.session_state.funcionarios) > len(funcionarios_padrao):
        st.write("---")
        st.write("**Últimos funcionários adicionados:**")
        # Mostrar apenas os que não estão na lista padrão
        funcionarios_adicionados = [f for f in st.session_state.funcionarios 
                                   if f not in funcionarios_padrao]
        
        if funcionarios_adicionados:
            for i, func in enumerate(funcionarios_adicionados[-5:], 1):  # Mostrar últimos 5
                st.caption(f"• {func}")

st.write("---")

# Pré-visualizar valor por extenso
if valor_input:
    valor_extenso_preview = valor_para_extenso(valor_input)
    st.info(f"**Valor por extenso:** {valor_extenso_preview}")
    
    # Calcular valor total se houver funcionários selecionados
    if selecionados:
        valor_total = calcular_valor_total(valor_input, len(selecionados))
        # Formatar valor total
        valor_total_formatado = f"R$ {valor_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        st.info(f"**Valor total ({len(selecionados)} funcionários × R$ {valor_input}):** {valor_total_formatado}")

# Botão para gerar PDF (TAMANHO NORMAL - sem use_container_width)
if st.button("🔄 Gerar PDF", type="primary"):
    if not selecionados:
        st.warning("⚠️ Por favor, selecione pelo menos um funcionário.")
    else:
        with st.spinner('Gerando PDF...'):
            pdf_bytes = gerar_pdf(selecionados, data_input, valor_input)
            st.success(f"✅ PDF gerado com sucesso para {len(selecionados)} funcionário(s)!")
            
            # Botão de download TAMANHO NORMAL (como era antes)
            st.download_button(
                label="⬇️ Baixar Ajuda de Custo (PDF)",
                data=pdf_bytes,
                file_name=f"ajuda_de_custo_{data_input.strftime('%d-%m-%Y')}.pdf",
                mime="application/pdf"
                # REMOVIDO: use_container_width=True
            )
            
            # Mostrar resumo com VALOR TOTAL
            st.write("---")
            st.write("### 📋 Resumo do Documento")
            
            # Calcular valor total
            valor_total = calcular_valor_total(valor_input, len(selecionados))
            valor_total_formatado = f"R$ {valor_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            col_res1, col_res2, col_res3, col_res4 = st.columns(4)
            with col_res1:
                st.metric("Funcionários", len(selecionados))
            with col_res2:
                st.metric("Valor Unitário", f"R$ {valor_input}")
            with col_res3:
                st.metric("Valor Total", valor_total_formatado)
            with col_res4:
                st.metric("Data", data_input.strftime("%d/%m/%Y"))
