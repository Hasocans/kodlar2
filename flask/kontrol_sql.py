import pypyodbc
from processing import process_image
import pyodbc
import string


def check_data_in_table(urun_pati_no, malzeme_pati_no):
    db = pypyodbc.connect(
        'Driver={SQL Server};'
        'Server=192.168.101.120;' 
        'Database=BIOCORE_TEST;'  
        'UID=SOFTWARE_TEST;'  
        'PWD=Bftst3442*;'  
    )

    cursor = db.cursor()
    query = """
    SELECT TOP (1000) [OrderNo]
        ,[BatchNo]
        ,[ProductCode]
        ,[ProductName]
        ,[MaterialNo]
        ,[MaterialName]
        ,[MaterialBatchNo]
        ,[NetWeight]
        ,[Unit]
    FROM [dbo].[VW_ProductProcess]
    WHERE BatchNo=? AND MaterialBatchNo=?
    """
    cursor.execute(query, (urun_pati_no, malzeme_pati_no))
    deger = cursor.fetchall()
    if deger:
        print("giriş2")
        query_select = query_select = """
SELECT TOP (1) [BatchNo],[MaterialBatchNo],[NetWeight],[Unit],[MaterialNo],[MaterialName],[ProductName],[ProductCode],[OrderNo]
FROM [dbo].[VW_ProductProcess]
WHERE BatchNo=? AND MaterialBatchNo=?
"""
        cursor.execute(query_select, (urun_pati_no, malzeme_pati_no))
        row = cursor.fetchone()
        print("a")
        result = (deger,row)
    else:
        print("b")
        result = (deger,None)    
    
    cursor.close()
    db.close()

    return result

def yetki(username):
    db = pypyodbc.connect(
        'Driver={SQL Server};'
        'Server=192.168.101.120;'  
        'Database=BIOCORE_TEST;'  
        'UID=SOFTWARE_TEST;'  
        'PWD=Bftst3442*;' 
    )


    cursor = db.cursor()
    query = "SELECT * FROM [dbo].[Authorization] WHERE ApplicationName = 'Tartim' AND AccountName=?"
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

def sıfır_silme(sıfırlı_deger):
    non_zero_index = next((i for i, c in enumerate(sıfırlı_deger) if c != '0'), None)
    if non_zero_index is not None:
        return sıfırlı_deger[non_zero_index:]
    return sıfırlı_deger    

def agirlik_sifir_silme(deger):
    deger_str = str(deger)
    
    if '.' in deger_str:
        deger_str = deger_str.rstrip('0').rstrip('.') 
        if deger_str[-1] == '.':
            deger_str = deger_str[:-1]
    print("sıfır_silme: "+deger_str)        
    return deger_str

def kg_duzenleme(value):
    try:
        cleaned_value = value.replace(" KG", "")
        float_value = float(cleaned_value)
        return float_value
    except ValueError:
        return None   
    