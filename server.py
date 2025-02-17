from flask import Flask, jsonify
from Routes.StudyRoute import studyBp
from Routes.UserRoute import userBp
from flask_cors import CORS

app = Flask(__name__)

app.secret_key = 'Dheeraj@2006'

CORS(app, resources={r"/*": {"origins": ["http://localhost:3000","*"],
                             "methods": ["GET", "POST", "OPTIONS"],
                             "supports_credentials": True}})


# Register Blueprints
app.register_blueprint(studyBp)  
app.register_blueprint(userBp)  


@app.route("/")
def index():
    return jsonify("this if dnogdn")

if __name__ == "__main__":
    # print("Server is running on http://127.0.0.1:5000")  # Debugging
    app.run(debug=True, port=5000)
    app.run(host="0.0.0.0",debug=True, port=5000)
