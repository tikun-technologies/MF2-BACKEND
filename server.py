from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from authlib.integrations.flask_client import OAuth
from DB.extension import jwt, oauth
app = Flask(__name__)
app.secret_key = 'Dheeraj@2006'


app.config['JWT_SECRET_KEY'] = 'Dheeraj@2006'  # Change this to a secure key

# ✅ Initialize JWT and OAuth with the app
jwt.init_app(app)
oauth.init_app(app)

CORS(app, resources={r"/*": {"origins": ["http://localhost:3000","*"],
                             "methods": ["GET", "POST", "OPTIONS"],
                             "supports_credentials": True}})


# Register Blueprints
@app.route("/", methods=['GET'])
def home():
    return jsonify({"status": "success", "message": "Flask API is running!"})

from Routes.StudyRoute import studyBp
from Routes.UserRoute import studyuserBp
app.register_blueprint(studyBp)  
app.register_blueprint(studyuserBp)  



if __name__ == "__main__":
    # print("Server is running on http://127.0.0.1:5000")  # Debugging
    # app.run(debug=True, port=5000)
    app.run(host="0.0.0.0",debug=True, port=5000)
