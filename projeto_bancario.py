# Sistema bancário simples com depósito, saque e extrato

saldo = 0.0
limite = 500.0
extrato = ""
numero_saques = 0
LIMITE_SAQUES = 3

while True:
    print("\n===== MENU =====")
    print("[d] Depositar")
    print("[s] Sacar")
    print("[e] Extrato")
    print("[q] Sair")

    opcao = input("Escolha uma opção: ").lower()

    if opcao == 'd':
        valor = float(input("Informe o valor do depósito: R$ "))
        if valor > 0:
            saldo += valor
            extrato += f"Depósito: R$ {valor:.2f}\n"
            print("Depósito realizado com sucesso.")
        else:
            print("Valor inválido para depósito.")

    elif opcao == 's':
        valor = float(input("Informe o valor do saque: R$ "))
        
        if valor <= 0:
            print("Valor inválido para saque.")
        elif valor > saldo:
            print("Saldo insuficiente.")
        elif valor > limite:
            print(f"O valor excede o limite de R$ {limite:.2f} por saque.")
        elif numero_saques >= LIMITE_SAQUES:
            print("Limite de saques diários atingido.")
        else:
            saldo -= valor
            extrato += f"Saque: R$ {valor:.2f}\n"
            numero_saques += 1
            print("Saque realizado com sucesso.")

    elif opcao == 'e':
        print("\n===== EXTRATO =====")
        print("Não foram realizadas movimentações." if not extrato else extrato)
        print(f"\nSaldo atual: R$ {saldo:.2f}")

    elif opcao == 'q':
        print("Obrigado por usar nosso sistema bancário!")
        break

    else:
        print("Opção inválida. Tente novamente.")
