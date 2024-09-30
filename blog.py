from flask import Flask, render_template, flash, redirect, url_for, session, logging, request,send_file
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
import os
import uuid





#Kullanıcı Kayıt Formu

class RegisterForm(Form):
    name= StringField("İsim Soyisim",validators=[validators.Length(min=4,max=25)]) 
    username= StringField("Kullanıcı Adı",validators=[validators.Length(min=5,max=35)]) 
    email= StringField("Email",validators=[validators.Email(message="Lütfen geçerli bir mail giriniz...")])
    password=PasswordField("Parola:",validators=[
        validators.DataRequired(message="Lütfen bir parola belirleyin.."),
        validators.EqualTo(fieldname="confirm",message=("Parolanız uyuşmuyor.."))

    ])
    confirm= PasswordField("Parola Doğrula")
    

app=Flask(__name__)


    
app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]=""
app.config["MYSQL_DB"]="ybblog"
app.config['MYSQL_CURSORCLASS']='DictCursor'

mysql =MySQL(app)

@app.route("/")
def index():

    sayi=10
    article=dict()
    article["title"]= "başlık"
    article["body"]="gövde"
    article["author"]="yazar"
    sozluk = [ {"id":1,"isim":"ahmet"},{"id":2,"isim":"dsadasdashmet"}]
    
    return render_template("index.html",number=sayi,article=article,sozluk=sozluk)
@app.route("/about")
def about():


    return render_template("about.html")

@app.route("/image")
def resim():

    return render_template("resim.html")
@app.route("/article/<string:id>")
def detail(id):
    return "Article ID:"+id
#Kayıt olma
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)

    try:
        if request.method == "POST" and form.validate():
            name = form.name.data
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt(form.password.data)
            print(password)

            conn = mysql.connect()
            cursor = conn.cursor()

            sorgu = "INSERT INTO users (name, username, email, password) VALUES (%s, %s, %s, %s)"

            cursor.execute(sorgu, (name, username, email, password))
            conn.commit()
        else:
            return render_template("register.html", form=form)
    except Exception as e:
        print("Error:", e)
    finally:
        if 'conn' in locals() and conn:
            conn.close()
        if 'cursor' in locals() and cursor:
            cursor.close()

    return redirect(url_for("index"))
@app.route("/deneme")
def deneme():

    return render_template("deneme.html")
@app.route("/login")
def login():
    form = RegisterForm(request.form)

    return render_template("login.html",form=form)
@app.route('/upload', methods=["GET","POST"])
def upload_file():
    if 'voice_file' not in request.files:
        return 'No file part'

    file = request.files['voice_file']

    if file.filename == '':
        return 'No selected file'

    if file:
        # You can specify the directory where you want to save the uploaded file
        # Be sure to create the directory if it doesn't exist
        file.save('uploads/' + file.filename)
        return 'File uploaded successfully'



@app.route('/radio')
def radio():
    # List all uploaded files in the 'uploads' directory
    upload_folder = 'uploads'
    files = [f for f in os.listdir(upload_folder) if os.path.isfile(os.path.join(upload_folder, f))]
    return render_template('upload.html', files=files)

@app.route('/', methods=['POST'])
def upload():
    if 'voice_file' not in request.files:
        return 'No file part'

    voice_file = request.files['voice_file']

    if voice_file.filename == '':
        return 'No selected file'

    # Generate a unique filename, for example using uuid
    unique_filename = str(uuid.uuid4()) + '.wav'

    # Save the voice file with the unique filename
    upload_folder = 'uploads'
    file_path = os.path.join(upload_folder, unique_filename)
    voice_file.save(file_path)

    return 'File uploaded successfully'

@app.route('/download/<filename>')
def download(filename):
    upload_folder = 'uploads' 
    file_path = os.path.join(upload_folder, filename)
    
    # Check if the file exists
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True )  # Provide the custom name here
    else:
        return 'File not found'



if __name__=="__main__":
    app.run(debug=True)

