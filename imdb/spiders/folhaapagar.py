import re
n_passageiros = 72
listadeestrelas = ['sirius', 'lalande', 'procion', 'alpha centauri', 'barnard']
dicVogal = {'a': 1,
			'e': 2,
			'i': 3,
			'o': 5,
			'u': 8}

produto = 1
for i in range(len(listadeestrelas)):
	print(i)
	for x in re.sub(r'[^aeiou]','', listadeestrelas[i]):
		produto = produto * dicVogal[x]
		print("x:",x)
		print("dic:", dicVogal[x])
		print("produto", produto)
	if produto == n_passageiros:
		break
	else:
		produto = 1

print("resposta:", listadeestrelas[i])