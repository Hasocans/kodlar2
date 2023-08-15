# processing.py

import cv2
import easyocr
import string
import re

def process_image(image_path2):
    import cv2
    import easyocr
    import string
    import re
    ocr_lang = "tr"


    reader = easyocr.Reader([ocr_lang])
    ref_img = cv2.imread(image_path2)




    new_width = 800#Daha iyi okuması için görüntüyü küçülttüm
    new_height = int(ref_img.shape[0] * new_width / ref_img.shape[1])
    ref_img_resized = cv2.resize(ref_img, (new_width, new_height))
    results = reader.readtext(ref_img_resized)



    results = reader.readtext(ref_img_resized)




    texts = []#Verileri tutan liste
    locations = []#Verilerin koınumlarını tutan liste
    for (bbox, text, prob) in results:
        texts.append(text)
        locations.append(bbox)




    def arrange_text_lines(text_list, location_list, line_spacing=10):#METİNLERİN KONUMUYLA YAZILARI YAN YANA VE ALT ALTA OLARAK AYARLIYOR
        lines = []
        current_line = []
        current_line_location = []
    
        for i, text in enumerate(text_list):
            if i == 0:
                current_line.append(text)
                current_line_location.append(location_list[i])
            else:
                prev_location = location_list[i - 1]
                current_location = location_list[i]
            
                if abs(current_location[0][1] - prev_location[1][1]) <= line_spacing:
                    current_line.append(text)
                    current_line_location.append(current_location)
                else:
                    lines.append((current_line, current_line_location))
                    current_line = [text]
                    current_line_location = [current_location]
    
        if current_line:#SON SATIRI EKLİYOR
            lines.append((current_line, current_line_location))
    
        return lines


    #KONUMA GRE SON KEZ DÜZELTİR
    lines = arrange_text_lines(texts, locations)


    #YENİ METNİ SONUÇLAR LİSTESİNE EKLEDİM
    Sonuclar = []
    for line_text, line_location in lines:
        line_text_str = " ".join(line_text).strip()
        line_text_str = " ".join(line_text_str.split())  #iki veya daha fazla boşluğu teke düşürür
        Sonuclar.append(line_text_str.upper())


    # Minimum boyut eşiği
    min_size_threshold = 20  # Bu değeri ihtiyaca göre ayarlayın
    for _, line_location in lines:
        for bbox in line_location:
            p1 = (int(bbox[0][0]), int(bbox[0][1]))
            p2 = (int(bbox[2][0]), int(bbox[2][1]))
            width = p2[0] - p1[0]
            height = p2[1] - p1[1]
            if width > min_size_threshold and height > min_size_threshold:
                cv2.rectangle(ref_img_resized, p1, p2, (0, 255, 0), 2)
            



    #SONUÇLARIN DÜZENLENMESİ(Bu kodu silersen ana kod kalır)
    cleaned_Sonuclar = []
    for i, sonuc in enumerate(Sonuclar):
        if i == 0:
            cleaned_sonuc = sonuc.translate(str.maketrans('', '', string.punctuation.replace(".", "").replace("/", "").replace(":", "")))
        else:
            cleaned_sonuc = sonuc.translate(str.maketrans('', '', string.punctuation.replace(".", "")))
        cleaned_Sonuclar.append(cleaned_sonuc)
    #Son defa boşlukları düzenle
    cleaned_Sonuclar2 = [' '.join(degisken.split()) for degisken in cleaned_Sonuclar]

    tek_nokta_liste = []

    try:
        for nokta in cleaned_Sonuclar2:
            if nokta.count(".") == 1:
                tek_nokta_liste.append(nokta)
        Net=tek_nokta_liste[-1] 
    except:
        Net=[]             

    integer_dizi = []

    for string_value in cleaned_Sonuclar2:
        numbers = re.findall(r'\d+', string_value)  # Sayıları bul
        numbers = [int(num) for num in numbers]  # Sayıları integer'a dönüştür
        integer_dizi.extend(numbers)  # Integerları integer_dizi'ye ekle

    sekiz_basamak = [num for num in integer_dizi if len(str(num)) == 8]

    duzgun_liste=[]
    for i in range(len(sekiz_basamak) // 2):
        urun_parti_no = sekiz_basamak[i * 2]
        malzeme_parti_no = sekiz_basamak[i * 2 + 1]
        duzgun_liste.append(urun_parti_no)
        duzgun_liste.append(malzeme_parti_no)
   
    return duzgun_liste,Net