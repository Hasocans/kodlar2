from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
from processing import process_image
from kontrol_sql import kg_duzenleme,check_data_in_table,int_kontrolu,net_parcalama,yetki,sıfır_silme,agirlik_sifir_silme
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = r'./gorseller'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/index') # Yeni bir route tanımlıyoruz
def show_index():
    return render_template('index.html')

@app.route('/')
def index():
    return render_template('login_page.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        now = datetime.now()
        timestamp = now.strftime("%d_%m_%Y_%H_%M")
        filename = f"{timestamp}.jpg"  # Dosya türüne göre düzenleyebilirsiniz
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('process_uploaded_file', filename=filename))
    else:
        return "Geçersiz dosya türü!"

@app.route('/uploaded/<filename>')
def process_uploaded_file(filename):
    global toplam
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    liste,Net = process_image(image_path)
    print(liste)
    print(Net) 
    if not liste and not Net:
        error_message = "Veri listesi boş, lütfen daha net çekin ve tekrar deneyin."
        return render_template('error.html', error_message=error_message)
        
    else:
        try:
            urun_parti_no = liste[0]
            malzeme_parti_no = liste[1]
            print(urun_parti_no)
            print(type(urun_parti_no))
            print(malzeme_parti_no)
            print(type(malzeme_parti_no))
            ana_result,ana_degerler=check_data_in_table(urun_parti_no,malzeme_parti_no)
            print(ana_degerler)
            try:
                yeni_urun_parti_no = str(ana_degerler[0])
            except:
                a,b=net_parcalama(Net)
                c=a+b
                return render_template('manual_result.html',urun_parti_no=urun_parti_no,malzeme_parti_no=malzeme_parti_no,yeni_net_img_degerler_agirlik=c)

            yeni_malzeme_parti_no = str(ana_degerler[1])
            yeni_agirlik_no=str(ana_degerler[2])
            yeni_birim=str(ana_degerler[3])
            yeni_net=yeni_agirlik_no+" "+yeni_birim
            yeni_malzeme_no2=str(ana_degerler[4])
            yeni_malzeme_no=sıfır_silme(yeni_malzeme_no2)
            yeni_malzeme_adi=str(ana_degerler[5])
            yeni_urun_adi=str(ana_degerler[6])
            yeni_urun_kodu2=str(ana_degerler[7])
            yeni_urun_kodu=sıfır_silme(yeni_urun_kodu2)
            yeni_siparis_no2=str(ana_degerler[8])
            yeni_siparis_no=sıfır_silme(yeni_siparis_no2)
            net_img_degerler_agirlik,net_img_degerler_birim=net_parcalama(Net)#Okunan değer
            
            yeni_net_img_degerler_agirlik=str(float(agirlik_sifir_silme(net_img_degerler_agirlik))+toplam)
            yeni_net_img=yeni_net_img_degerler_agirlik+' '+'KG'
            karsilastir=None
            if yeni_net_img_degerler_agirlik==yeni_agirlik_no:
                karsilastir=True

            return render_template('confirm.html',karsilastir=karsilastir,urun_parti_no=urun_parti_no, malzeme_parti_no=malzeme_parti_no,yeni_net_img=yeni_net_img,ana_result=ana_result,yeni_net_img_degerler_agirlik=yeni_net_img_degerler_agirlik,net_img_degerler_birim=net_img_degerler_birim,yeni_urun_parti_no=yeni_urun_parti_no,yeni_malzeme_parti_no=yeni_malzeme_parti_no,yeni_net=yeni_net,yeni_malzeme_no=yeni_malzeme_no,yeni_malzeme_adi=yeni_malzeme_adi,yeni_urun_adi=yeni_urun_adi,yeni_urun_kodu=yeni_urun_kodu,yeni_siparis_no=yeni_siparis_no)
        except Exception as e:
            error_message = "Fotoğraf işlenirken bir hata oluştu: " + str(e)
            return render_template('error.html', error_message=error_message)

    


@app.route('/confirm', methods=['POST'])#confirm.htmldeki basılan butonların ne yapması gerektiğini söylüyor
def confirm_data():
    urun_parti_no = request.form['urun_parti_no']
    malzeme_parti_no = request.form['malzeme_parti_no']
    confirm_choice = request.form['confirm']
    yeni_net_img_degerler_agirlik = request.form['Net']
    result = request.form['result']

    if confirm_choice == 'yes':
         return redirect('/index')
    elif confirm_choice == 'no':
        return redirect('/index')
    elif confirm_choice == 'manual':
        return render_template('manual.html', urun_parti_no=urun_parti_no, malzeme_parti_no=malzeme_parti_no, yeni_net_img_degerler_agirlik=yeni_net_img_degerler_agirlik, result=result)
    else:
        return redirect('/index')


@app.route('/manual_edit', methods=['POST'])
def manual_check():
    urun_parti_no = request.form['urun_parti_no']
    malzeme_parti_no = request.form['malzeme_parti_no']
    yeni_net_img_degerler_agirlik = request.form['Net']
    int_kontrol=int_kontrolu(urun_parti_no,malzeme_parti_no)
    if int_kontrol==False:
        error_message2="Değiştirdiğiniz değerler sadece rakam içermeli.Lütfen girdiğiniz değerleri konrtol edip tekrar deneyin."
        return render_template('manual_error.html', error_message2=error_message2)
    ana_result,ana_degerler=check_data_in_table(urun_parti_no,malzeme_parti_no)

    if ana_result:
        yeni_urun_parti_no = str(ana_degerler[0])
        yeni_malzeme_parti_no = str(ana_degerler[1])
        yeni_agirlik_no=str(ana_degerler[2])
        yeni_birim=str(ana_degerler[3])
        yeni_net=yeni_agirlik_no+" "+yeni_birim
        yeni_malzeme_no2=str(ana_degerler[4])
        yeni_malzeme_no=sıfır_silme(yeni_malzeme_no2)
        yeni_malzeme_adi=str(ana_degerler[5])
        yeni_urun_adi=str(ana_degerler[6])
        yeni_urun_kodu2=str(ana_degerler[7])
        yeni_urun_kodu=sıfır_silme(yeni_urun_kodu2)
        yeni_siparis_no2=str(ana_degerler[8])
        yeni_siparis_no=sıfır_silme(yeni_siparis_no2)
        net_img_degerler_agirlik,net_img_degerler_birim=net_parcalama(yeni_net_img_degerler_agirlik)
        yeni_net_img_degerler_agirlik=str(agirlik_sifir_silme(net_img_degerler_agirlik))
        yeni_net_img=yeni_net_img_degerler_agirlik+' '+'KG'
        karsilastir=None
        if yeni_net_img_degerler_agirlik==yeni_agirlik_no:
            karsilastir=True

        return render_template('confirm.html',karsilastir=karsilastir,urun_parti_no=urun_parti_no, malzeme_parti_no=malzeme_parti_no,yeni_net_img=yeni_net_img,ana_result=ana_result,net_img_degerler_birim=net_img_degerler_birim,yeni_urun_parti_no=yeni_urun_parti_no,yeni_malzeme_parti_no=yeni_malzeme_parti_no,yeni_net=yeni_net,yeni_malzeme_no=yeni_malzeme_no,yeni_malzeme_adi=yeni_malzeme_adi,yeni_urun_adi=yeni_urun_adi,yeni_urun_kodu=yeni_urun_kodu,yeni_siparis_no=yeni_siparis_no)    
    else:
        return render_template('manual_result.html',urun_parti_no=urun_parti_no,malzeme_parti_no=malzeme_parti_no,yeni_net_img_degerler_agirlik=yeni_net_img_degerler_agirlik)
@app.route('/check_user_permission', methods=['POST'])
def check_user_permission():
    username = request.form['username']
    user_permission = yetki(username)

    if user_permission:
        return "Authorized"
    else:
        return "Unauthorized"


toplam=0.0
@app.route('/ekle', methods=['POST'])
def confirm():
    global toplam#float değerinde
    onay_butonu=request.form.get("confirm")
    ekle_butonu=request.form.get("ekle")
    kg_degeri=request.form.get("kg")#2.458 KG

    if ekle_butonu == 'ekle':
        toplam+=kg_duzenleme(kg_degeri)
        return render_template('index.html') 
        
    else:
        toplam=0.0
        return render_template('index.html')   

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

