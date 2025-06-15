from datetime import datetime

# ----- Dados globais -----
usuarios = []  # Lista de usuários
contas = []    # Lista de contas
proximo_numero_conta = 1

LIMITE_SAQUES = 3
LIMITE_SAQUE_VALOR = 500.0

# ----- Funções de Usuário -----

def criar_usuario():
    print("\n=== Cadastro de Usuário ===")
    nome = input("Nome completo: ").strip()
    data_nascimento = input("Data de nascimento (dd/mm/aaaa): ").strip()

    try:
        datetime.strptime(data_nascimento, "%d/%m/%Y")
    except ValueError:
        print("Data inválida. Tente novamente.")
        return None

    while True:
        cpf = input("CPF (somente números): ").strip()
        if not cpf.isdigit() or len(cpf) != 11:
            print("CPF inválido. Deve ter 11 dígitos.")
            continue
        if any(cpf == u["cpf"] for u in usuarios):
            print("CPF já cadastrado.")
            return None
        break

    endereco = input("Endereço (rua, número): ").strip()
    bairro = input("Bairro: ").strip()
    cidade = input("Cidade: ").strip()
    estado = input("Estado: ").strip()

    usuario = {
        "nome": nome,
        "data_nascimento": data_nascimento,
        "cpf": cpf,
        "endereco": endereco,
        "bairro": bairro,
        "cidade": cidade,
        "estado": estado
    }

    usuarios.append(usuario)
    print("Usuário cadastrado com sucesso.")
    return usuario

def listar_usuarios():
    if not usuarios:
        print("Nenhum usuário cadastrado.")
        return
    for i, u in enumerate(usuarios, 1):
        print(f"{i} - {u['nome']} (CPF: {u['cpf']})")

def selecionar_usuario():
    listar_usuarios()
    try:
        escolha = int(input("Escolha o número do usuário: "))
        if 1 <= escolha <= len(usuarios):
            return usuarios[escolha - 1]
    except ValueError:
        pass
    print("Escolha inválida.")
    return None

# ----- Funções de Conta -----

def criar_conta(usuario):
    global proximo_numero_conta

    print(f"\nCriando conta para {usuario['nome']}")
    agencia = input("Informe o número da agência: ").strip()

    conta = {
        "numero": proximo_numero_conta,
        "agencia": agencia,
        "usuario": usuario,
        "saldo": 0.0,
        "limite": LIMITE_SAQUE_VALOR,
        "extrato": "",
        "numero_saques": 0
    }

    contas.append(conta)
    proximo_numero_conta += 1
    print(f"Conta criada com sucesso! Número da conta: {conta['numero']}")
    return conta

def listar_contas():
    if not contas:
        print("Nenhuma conta criada.")
        return

    print("\n=== Contas Cadastradas ===")
    for c in contas:
        print(f"Conta: {c['numero']}")
        print(f"Agência: {c['agencia']}")
        print(f"Usuário: {c['usuario']['nome']}")
        print(f"CPF: {c['usuario']['cpf']}")
        print(f"Saldo: R$ {c['saldo']:.2f}")
        print("-" * 40)

def selecionar_conta():
    listar_contas()
    try:
        escolha = int(input("Informe o número da conta: "))
        for conta in contas:
            if conta['numero'] == escolha:
                return conta
    except ValueError:
        pass
    print("Conta não encontrada.")
    return None

# ----- Funções Bancárias -----

def depositar(conta):
    try:
        valor = float(input("Valor do depósito: R$ "))
        if valor <= 0:
            raise ValueError
    except ValueError:
        print("Valor inválido.")
        return
    conta['saldo'] += valor
    conta['extrato'] += f"Depósito: R$ {valor:.2f}\n"
    print("Depósito realizado com sucesso.")

def sacar(conta):
    try:
        valor = float(input("Valor do saque: R$ "))
    except ValueError:
        print("Valor inválido.")
        return
    if valor <= 0:
        print("Valor inválido.")
    elif valor > conta['saldo']:
        print("Saldo insuficiente.")
    elif valor > conta['limite']:
        print(f"Valor excede o limite de R$ {conta['limite']:.2f}")
    elif conta['numero_saques'] >= LIMITE_SAQUES:
        print("Limite diário de saques atingido.")
    else:
        conta['saldo'] -= valor
        conta['extrato'] += f"Saque: R$ {valor:.2f}\n"
        conta['numero_saques'] += 1
        print("Saque realizado com sucesso.")

def visualizar_extrato(conta):
    print("\n=== EXTRATO ===")
    print(conta['extrato'] if conta['extrato'] else "Não houve movimentações.")
    print(f"Saldo atual: R$ {conta['saldo']:.2f}")

# ----- Menu Principal -----

def menu():
    conta_atual = None

    while True:
        print("\n===== MENU =====")
        print("[1] Cadastrar usuário")
        print("[2] Criar conta")
        print("[3] Listar contas")
        print("[4] Selecionar conta")
        print("[5] Depositar")
        print("[6] Sacar")
        print("[7] Extrato")
        print("[0] Sair")

        opcao = input("Escolha: ").strip()

        if opcao == '1':
            criar_usuario()
        elif opcao == '2':
            usuario = selecionar_usuario()
            if usuario:
                criar_conta(usuario)
        elif opcao == '3':
            listar_contas()
        elif opcao == '4':
            conta_atual = selecionar_conta()
            if conta_atual:
                print(f"Conta {conta_atual['numero']} selecionada.")
        elif opcao == '5':
            if conta_atual:
                depositar(conta_atual)
            else:
                print("Nenhuma conta selecionada.")
        elif opcao == '6':
            if conta_atual:
                sacar(conta_atual)
            else:
                print("Nenhuma conta selecionada.")
        elif opcao == '7':
            if conta_atual:
                visualizar_extrato(conta_atual)
            else:
                print("Nenhuma conta selecionada.")
        elif opcao == '0':
            print("Encerrando sistema. Até logo!")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    menu()
