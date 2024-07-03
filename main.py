from flask import Flask,jsonify
from dotenv import load_dotenv
from Party_DataTable.party_view import party_list_bp
import os






load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['JWT_SECRET_KEY'] = SECRET_KEY


# Set the upload folder
UPLOAD_FOLDER = '/static/public'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max upload size: 16MB


# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    


#Register BluePrint
app.register_blueprint(party_list_bp)




if __name__ == "__main__":
    app.run(debug=True,port=8000)


