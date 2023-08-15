import pypyodbc
from processing import process_image
import pyodbc
import string

#msqlde etiket değerleri kontrol ediliyor
def check_data_in_table(urun_pati_no, malzeme_pati_no):
    db = pypyodbc.connect(
        'Driver={SQL Server};'
        'Server=BFPC1246\SQLEXPRESS;'
        'Database=ogrenci_bilgileri;'#database ismi
        'Trusted_Connection=True;'
    )

    cursor = db.cursor()
    query = "SELECT * FROM PartiNo WHERE UrunPatiNo = ? AND MalzemePartiNo = ?"#table,sütun1,sütun2
    cursor.execute(query, (urun_pati_no, malzeme_pati_no))
    deger = cursor.fetchall()
    if deger:
        query_select = "SELECT agirlik, Birim FROM PartiNo WHERE UrunPatiNo = ? AND MalzemePartiNo = ?"
        cursor.execute(query_select, (urun_pati_no, malzeme_pati_no))
        row = cursor.fetchone()
        agirlik = row[0]
        birim = row[1]
        result = (deger, agirlik, birim)
    else:
        result = (deger, None, None)    
    
    cursor.close()
    db.close()

    return result

def yetki(username):
    db = pypyodbc.connect(
        'Driver={SQL Server};'
        'Server=BFPC1246\SQLEXPRESS;'
        'Database=Yetkiler;'  # database ismi
        'Trusted_Connection=True;'
    )

    cursor = db.cursor()
    query = "SELECT * FROM Yetki WHERE username = ?"  # table, sütun1, sütun2
    cursor.execute(query, (username,))
    result = cursor.fetchall()
    cursor.close()
    db.close()

    return result

#manual olarak değiştirdiğimiz değerlerde rakam hariç herhangi bir değer varmı yokmu omu kontrol eder
def int_kontrolu(urun_parti_no,malzeme_parti_no):
    if urun_parti_no.isdigit() and malzeme_parti_no.isdigit():
        return True
    else:
        return False
    
#Fotoğrafta okunan net değerini ağırlık ve KG/GR olarak ayırıp değerlere atar
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

"""def update_agirlik(urun_pati_no, malzeme_pati_no,agirlik):
    connection_string = (
        'Driver={SQL Server};'
        'Server=BFPC1246\SQLEXPRESS;'
        'Database=ogrenci_bilgileri;'  
        'Trusted_Connection=True;'
    )
    for noktalama_isaretleri in string.punctuation:
        if noktalama_isaretleri != ".":
            agirlik = agirlik.replace(noktalama_isaretleri, ".")#Değişkende nokta hariç başka bir noktalama işareti varsa onları nokta yapıyor

    i = len(agirlik) - 1
    while i >= 0 and not agirlik[i].isdigit():
        i -= 1

    yeni_agirlik = agirlik[:i+1]
    print(yeni_agirlik)

    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()

    query = "UPDATE PartiNo SET agirlik = ? WHERE UrunPatiNo = ? AND MalzemePartiNo = ?"
    cursor.execute(query, (yeni_agirlik, urun_pati_no, malzeme_pati_no))

    if "k" in agirlik or "K" in agirlik:
        query = "UPDATE PartiNo SET Birim = ? WHERE UrunPatiNo = ? AND MalzemePartiNo = ?"
        cursor.execute(query, ("KG", urun_pati_no, malzeme_pati_no))
    elif "r" in agirlik or "R" in agirlik:
        query = "UPDATE PartiNo SET Birim = ? WHERE UrunPatiNo = ? AND MalzemePartiNo = ?"
        cursor.execute(query, ("GR", urun_pati_no, malzeme_pati_no))
    else:
        query = "UPDATE PartiNo SET Birim = ? WHERE UrunPatiNo = ? AND MalzemePartiNo = ?"
        cursor.execute(query, ("NONE", urun_pati_no, malzeme_pati_no))
    connection.commit()
    cursor.close()
    connection.close()
    return"""
   



