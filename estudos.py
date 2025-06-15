eventos = {}

# Entrada do número de participantes
n = int(input())

temas = {}

for _ in range(n):
  entrada = input().split(", ")
  nome = entrada[0]
  tema = entrada[1]

  if tema not in temas:
    temas[tema] = []
    
  temas[tema].append(nome)  
# TODO: Crie um loop para armazenar participantes e seus temas:




for tema, nomes in temas.items():
    print(f"{tema}: {', '.join(nomes)}")