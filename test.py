import string

agirlik = "3.475 kg"
Birim=None

if "k" in agirlik or "K" in agirlik:
    Birim="KG"
elif "g" in agirlik or "G" in agirlik:
    Birim="GR"
else:
    Birim=None

for noktalama_isaretleri in string.punctuation:
    if noktalama_isaretleri != ".":
        agirlik = agirlik.replace(noktalama_isaretleri, ".")#Değişkende nokta hariç başka bir noktalama işareti varsa onları nokta yapıyor

i = len(agirlik) - 1
while i >= 0 and not agirlik[i].isdigit():
    i -= 1
    
yeni_agirlik = agirlik[:i+1]

