import pickle
import os
import matplotlib.pyplot as plt

# --- Estruturas de Dados Globais ---
candidatos = {}  # Chave: Número do Candidato
eleitores = {}   # Chave: Título de Eleitor
votos_apurados = [] # Lista para guardar os votos lidos do pickle
arquivo_candidatos = "candidatos.txt"
arquivo_eleitores = "eleitores.txt"
arquivo_votos = "votos.bin"
arquivo_ja_votaram = "eleitores_que_votaram.txt"
arquivo_boletim = "boletim.txt"

# Dicionário de configuração dos cargos
cargos_info = {
    'F': {'nome': 'Deputado Federal', 'digitos': 4},
    'E': {'nome': 'Deputado Estadual', 'digitos': 5},
    'S': {'nome': 'Senador', 'digitos': 3},
    'G': {'nome': 'Governador', 'digitos': 2},
    'P': {'nome': 'Presidente', 'digitos': 2}
}
# Ordem de votação
ordem_votacao = ['F', 'E', 'S', 'G', 'P']

# --- DESAFIO EXTRA 2: Controle de Votação ---
def verificar_ja_votou(titulo):
    """Verifica se o título já consta no arquivo de quem votou."""
    if not os.path.exists(arquivo_ja_votaram):
        return False

    with open(arquivo_ja_votaram, 'r') as f:
        titulos = f.read().splitlines()
    return titulo in titulos

def registrar_ja_votou(titulo):
    """Salva o título no arquivo de controle."""
    with open(arquivo_ja_votaram, 'a') as f:
        f.write(f"{titulo}\n")

# --- Funções Principais ---

def carregar_candidatos():
    """Lê o arquivo de texto e preenche o dicionário de candidatos."""
    if not os.path.exists(arquivo_candidatos):
        print(f"❌ Arquivo {arquivo_candidatos} não encontrado!")
        return False

    try:
        with open(arquivo_candidatos, 'r', encoding='utf-8') as f:
            for linha in f:
                # Formato esperado: Numero,Nome,Partido,Cargo_Sigla,Estado
                dados = linha.strip().split(',')
                if len(dados) == 5:
                    numero, nome, partido, cargo, uf = dados
                    candidatos[numero] = {
                        'nome': nome,
                        'partido': partido,
                        'cargo': cargo,
                        'uf': uf
                    }
        print(f"✅ {len(candidatos)} candidatos carregados com sucesso.")
        return True
    except Exception as e:
        print(f"Erro ao ler candidatos: {e}")
        return False

def carregar_eleitores():
    """Lê o arquivo de texto e preenche o dicionário de eleitores."""
    if not os.path.exists(arquivo_eleitores):
        print(f"❌ Arquivo {arquivo_eleitores} não encontrado!")
        return False

    try:
        with open(arquivo_eleitores, 'r', encoding='utf-8') as f:
            for linha in f:
                # Formato esperado: Nome,RG,Titulo,Municipio,UF
                dados = linha.strip().split(',')
                if len(dados) == 5:
                    nome, rg, titulo, municipio, uf = dados
                    eleitores[titulo] = {
                        'nome': nome,
                        'rg': rg,
                        'municipio': municipio,
                        'uf': uf
                    }
        print(f"✅ {len(eleitores)} eleitores carregados com sucesso.")
        return True
    except Exception as e:
        print(f"Erro ao ler eleitores: {e}")
        return False

def iniciar_votacao():
    """Gerencia o processo de votação."""
    print("\n--- INICIANDO VOTAÇÃO ---")
    uf_urna = input("Informe a UF desta Urna (ex: MG): ").upper()

    titulo = input("Informe o Título de Eleitor: ")

    # Verifica existência do eleitor
    if titulo not in eleitores:
        print("❌ Eleitor não encontrado!")
        return

    # DESAFIO EXTRA 2: Verifica duplicidade
    if verificar_ja_votou(titulo):
        print("❌ ERRO: Eleitor já votou. Votação não permitida.")
        return

    eleitor = eleitores[titulo]
    print(f"✅ Eleitor: {eleitor['nome']} | Estado: {eleitor['uf']}")

    voto_atual = {"UF": uf_urna}

    for sigla_cargo in ordem_votacao:
        info = cargos_info[sigla_cargo]
        cargo_nome = info['nome']

        confirmado = False
        while not confirmado:
            print(f"\n--- Voto para {cargo_nome} ({info['digitos']} dígitos) ---")
            numero_voto = input("Digite o número (ou B para Branco): ").upper()

            voto_computado = "N" # Padrão é Nulo se não encontrar

            if numero_voto == "B":
                print("Voto em BRANCO.")
                voto_computado = "B"

            elif numero_voto in candidatos:
                cand = candidatos[numero_voto]

                # Regra: Eleitor só vota em candidato do seu estado (exceto Presidente)
                # Nota: O enunciado diz "UF da Urna", mas a regra diz "UF do Eleitor" vs "Candidato".
                # Vamos assumir: Candidato deve ser da UF da Urna ou 'BR' (Presidente)
                if cand['cargo'] == sigla_cargo:
                    if cand['uf'] == uf_urna or cand['uf'] == 'BR':
                        print(f"Candidato: {cand['nome']} | Partido: {cand['partido']}")
                        voto_computado = numero_voto
                    else:
                        print("⚠️  Candidato de outro estado! Voto será considerado NULO.")
                else:
                    print("⚠️  Número pertence a outro cargo! Voto será considerado NULO.")
            else:
                print("⚠️  Número inexistente! Voto será NULO.")

            conf = input("Confirma (S ou N)? ").upper()
            if conf == 'S':
                voto_atual[sigla_cargo] = voto_computado
                confirmado = True

    # Salvar Voto com Pickle
    try:
        with open(arquivo_votos, 'ab') as f: # 'ab' = append binary
            pickle.dump(voto_atual, f)

        # DESAFIO EXTRA 2: Registrar que o eleitor votou
        registrar_ja_votou(titulo)

        print("\n✅ Voto registrado com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar voto: {e}")

def apurar_votos():
    """Lê o arquivo binário e contabiliza os resultados."""
    if not os.path.exists(arquivo_votos):
        print("Nenhum voto registrado ainda.")
        return False

    global votos_apurados
    votos_apurados = []

    try:
        with open(arquivo_votos, 'rb') as f:
            while True:
                try:
                    voto = pickle.load(f)
                    votos_apurados.append(voto)
                except EOFError:
                    break # Fim do arquivo
        print(f"✅ Apuração concluída. {len(votos_apurados)} votos processados.")
        return True
    except Exception as e:
        print(f"Erro na apuração: {e}")
        return False

# --- DESAFIO EXTRA 1: Gráficos ---
def gera_grafico(titulo_grafico, dados_votos):
    """Gera um gráfico de barras usando Matplotlib."""
    nomes = list(dados_votos.keys())
    qtds = list(dados_votos.values())

    plt.figure(figsize=(10, 6))
    plt.bar(nomes, qtds, color='skyblue')
    plt.title(titulo_grafico)
    plt.xlabel('Candidatos/Opções')
    plt.ylabel('Quantidade de Votos')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def mostrar_resultados():
    """Gera o boletim de urna e os gráficos."""
    if not votos_apurados:
        print("É necessário apurar os votos primeiro (Opção 4).")
        return

    resultados = {} # Estrutura para contagem

    # Inicializa contagem
    for sigla in ordem_votacao:
        resultados[sigla] = {'Brancos': 0, 'Nulos': 0, 'Nominais': {}}

    total_votos = len(votos_apurados)

    # Contagem
    for voto in votos_apurados:
        for sigla in ordem_votacao:
            escolha = voto[sigla]

            if escolha == 'B':
                resultados[sigla]['Brancos'] += 1
            elif escolha == 'N':
                resultados[sigla]['Nulos'] += 1
            else:
                # Voto nominal
                nome_cand = candidatos[escolha]['nome']
                if nome_cand in resultados[sigla]['Nominais']:
                    resultados[sigla]['Nominais'][nome_cand] += 1
                else:
                    resultados[sigla]['Nominais'][nome_cand] = 1

    # Gerar Boletim TXT
    with open(arquivo_boletim, 'w', encoding='utf-8') as f:
        f.write("=== BOLETIM DE URNA ===\n\n")
        f.write(f"Total de votos computados: {total_votos}\n")
        f.write("-" * 30 + "\n")

        for sigla in ordem_votacao:
            nome_cargo = cargos_info[sigla]['nome']
            dados = resultados[sigla]

            f.write(f"\nCargo: {nome_cargo}\n")
            f.write(f"Brancos: {dados['Brancos']}\n")
            f.write(f"Nulos: {dados['Nulos']}\n")

            # Prepara dados para o gráfico
            dados_grafico = {
                "Brancos": dados['Brancos'],
                "Nulos": dados['Nulos']
            }

            for nome, qtd in dados['Nominais'].items():
                porcentagem = (qtd / total_votos) * 100
                f.write(f"{nome}: {qtd} votos ({porcentagem:.2f}%)\n")
                dados_grafico[nome] = qtd

            f.write("-" * 30 + "\n")

            # Chamada do Desafio Extra 1
            gera_grafico(f"Resultado - {nome_cargo}", dados_grafico)

    print(f"✅ Boletim salvo em '{arquivo_boletim}'. Gráficos gerados.")

# --- Menu Principal ---
def menu():
    dados_carregados = False

    while True:
        print("\n" + "="*30)
        print("   URNA ELETRÔNICA SIMPLIFICADA")
        print("="*30)
        print("1 - Ler arquivo de candidatos")
        print("2 - Ler arquivo de eleitores")
        print("3 - Iniciar votação")
        print("4 - Apurar votos")
        print("5 - Mostrar resultados e Gráficos")
        print("6 - Fechar programa")

        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            if carregar_candidatos():
                print("Candidatos prontos.")

        elif opcao == '2':
            if carregar_eleitores():
                print("Eleitores prontos.")
                # Se ambos estiverem ok, libera as outras opções
                if len(candidatos) > 0:
                    dados_carregados = True

        elif opcao == '3':
            if not dados_carregados:
                print("⚠️  Carregue candidatos e eleitores primeiro!")
            else:
                iniciar_votacao()

        elif opcao == '4':
            if not dados_carregados:
                print("⚠️  Carregue candidatos e eleitores primeiro!")
            else:
                apurar_votos()

        elif opcao == '5':
            if not dados_carregados:
                print("⚠️  Carregue candidatos e eleitores primeiro!")
            else:
                mostrar_resultados()

        elif opcao == '6':
            print("Encerrando sistema...")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    menu()