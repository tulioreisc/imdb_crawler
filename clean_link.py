
link = 'https://pro.imdb.com/title/tt6644200?ref_=mojo_rl_summary&rf=mojo_rl_summary'
print('length:',len(link))
link = link[27:]
print("link:",link)
linkfinal = ''
for i in link:
	if i == '?':
		break
	else:
		linkfinal = linkfinal + i

print("linkfinal:",linkfinal)