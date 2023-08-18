import string

def net_parcalama(net):
    Birim = None

    if "k" in net or "K" in net:
        Birim = "KG"
    elif "g" in net or "G" in net:
        Birim = "GR"
    else:
        Birim = None

    for noktalama_isaretleri in string.punctuation:
        if noktalama_isaretleri != ".":
            net = net.replace(noktalama_isaretleri, ".")

    i = len(net) - 1
    while i >= 0 and not net[i].isdigit():
        i -= 1

    yeni_agirlik = net[:i+1]
   
    return yeni_agirlik, Birim   

a=net_parcalama("3.375 KA")

b=a[0]
c=a[1]
print(type(b))
print(b)
print(type(c))
print(c)

d=b+" "+c
print(d)