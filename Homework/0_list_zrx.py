f = open('TestGit\homework\input.txt','r')
tables =[]
n=int(f.readline())
for n in range(0,n):
    temp = []
    for i in range(8):
        temp.append(f.readline())
    tables.append(temp)
#print(len(tables),"\n")

for i in range(n+2):
    times=0
    #print(i);
    for t in range(i):
        #print(t)
        if tables[i-1]==tables[t]:
            times=times+1
    if times<1:
        times=0
    else:
        print(times)