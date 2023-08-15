from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
from processing import process_image
from kontrol_sql import check_data_in_table,int_kontrolu,net_parcalama,yetki
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
            ana_result=check_data_in_table(urun_parti_no,malzeme_parti_no)
            result=ana_result[0]
            agirlik=str(ana_result[1])
            Birim=str(ana_result[2])
            net_img_degerler_agirlik,net_img_degerler_birim=net_parcalama(Net)


            if net_img_degerler_birim!=Birim and net_img_degerler_agirlik!=agirlik:
                message="Ağırlık ve KG/GR Değerlerinin İkiside Sistemdekiler İle Eşleşmedi"
            elif net_img_degerler_birim!=Birim:
                message="KG/GR Değerleri Sistemdekiler İle Eşleşmedi"
            elif net_img_degerler_agirlik!=agirlik:
                message="AğırlıK Değerleri Sistemdekiler İle Eşleşmedi"
            else:
                message="Eşleşti"    
            return render_template('confirm.html', urun_parti_no=urun_parti_no, malzeme_parti_no=malzeme_parti_no,Net=Net,result=result,message=message)
        except:
            error_message = "Fotoğraf işlenirken bir hata oluştu, lütfen daha net çekin ve tekrar deneyin."
            return render_template('error.html', error_message=error_message)    
    

# ... (diğer importlar ve kodlar)

@app.route('/confirm', methods=['POST'])#confirm.htmldeki basılan butonların ne yapması gerektiğini söylüyor
def confirm_data():
    urun_parti_no = request.form['urun_parti_no']
    malzeme_parti_no = request.form['malzeme_parti_no']
    confirm_choice = request.form['confirm']
    Net = request.form['Net']
    result = request.form['result']

    if confirm_choice == 'yes':
         return redirect('/')
    elif confirm_choice == 'no':
        return redirect('/')
    elif confirm_choice == 'manual':
        return render_template('manual.html', urun_parti_no=urun_parti_no, malzeme_parti_no=malzeme_parti_no, Net=Net, result=result)
    else:
        return redirect('/')


@app.route('/manual_edit', methods=['POST'])
def manual_check():
    urun_parti_no = request.form['urun_parti_no']
    malzeme_parti_no = request.form['malzeme_parti_no']
    Net = request.form['Net']
    int_kontrol=int_kontrolu(urun_parti_no,malzeme_parti_no)
    if int_kontrol==False:
        error_message2="Değiştirdiğiniz değerler sadece rakam içermeli.Lütfen girdiğiniz değerleri konrtol edip tekrar deneyin."
        return render_template('manual_error.html', error_message2=error_message2)
    new_result_ana = check_data_in_table(urun_parti_no, malzeme_parti_no) 
    new_result=new_result_ana[0]
    agirlik=str(new_result_ana[1])
    Birim=str(new_result_ana[2])
    net_img_degerler_agirlik,net_img_degerler_birim=net_parcalama(Net)


    if net_img_degerler_birim!=Birim and net_img_degerler_agirlik!=agirlik:
        message="Ağırlık ve KG/GR Değerlerinin İkiside Sistemdekiler İle Eşleşmedi"
    elif net_img_degerler_birim!=Birim:
                message="KG/GR Değerleri Sistemdekiler İle Eşleşmedi"
    elif net_img_degerler_agirlik!=agirlik:
         message="AğırlıK Değerleri Sistemdekiler İle Eşleşmedi"
    else:
        message="Eşleşti"    
    return render_template('manual_result.html',urun_parti_no=urun_parti_no, malzeme_parti_no=malzeme_parti_no,Net=Net,new_result=new_result,message=message)

@app.route('/check_user_permission', methods=['POST'])
def check_user_permission():
    username = request.form['username']
    user_permission = yetki(username)

    if user_permission:
        return "Authorized"
    else:
        return "Unauthorized"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
