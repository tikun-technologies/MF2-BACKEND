import uuid
import jwt
import datetime
from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from authlib.integrations.flask_client import OAuth
from functools import wraps
from Model.User import UserSchema
from DB.db import USER_collection, STUDIES_collection
from DB.extension import jwt,oauth
from functions import protected
bcrypt = Bcrypt()

userBp = Blueprint('userBp', __name__)

# Google OAuth Config
oauth.register(
    'google',
    client_id='845665327234-damcdg8g3o5pmqf8079lheckii6sn5cl.apps.googleusercontent.com',
    client_secret='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',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://oauth2.googleapis.com/token',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # ✅ Explicit user info endpoint
    client_kwargs={'scope': 'openid email profile'},
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration"  # ✅ Explicit metadata URL
)
# def protected(f):
#     @wraps(f)  # ✅ This preserves the function's original name
#     @jwt_required()
#     def wrapper(*args, **kwargs):
#         return f(*args, **kwargs)
#     return wrapper
# Signup (Username/Password)
@userBp.route("/signup", methods=['POST'])
def signup():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        if USER_collection.find_one({"email": email}):
            return jsonify({'status': 'error', 'message': 'Email already exists'}), 400
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user_data = {
            "_id": str(uuid.uuid4()),
            "email": email,
            "password": hashed_password,
            "name": data.get('name')
        }
        USER_collection.insert_one(user_data)
        return jsonify({'status': 'success', 'message': 'User registered successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# Login (Username/Password)
@userBp.route("/login", methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        user = USER_collection.find_one({"email": email})
        
        if not user or not bcrypt.check_password_hash(user['password'], password):
            return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401
        
        access_token = create_access_token(identity=email, expires_delta=datetime.timedelta(days=1))
        return jsonify({'status': 'success', 'access_token': access_token.decode('utf-8')})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# Google OAuth Login
@userBp.route("/login/google")
def google_login():
    redirect_uri = request.host_url + "callback/google"
    return oauth.google.authorize_redirect(redirect_uri)

# Google OAuth Callback
@userBp.route("/callback/google")
def google_callback():
    try:
        # ✅ Exchange authorization code for an access token
        token = oauth.google.authorize_access_token()
        print("Google Token:", token)  # Debugging

        # ✅ Get user info using the access token
        user_info = oauth.google.get('https://openidconnect.googleapis.com/v1/userinfo').json()
        print("User Info:", user_info)  # Debugging

        email = user_info.get('email')
        name = user_info.get('name')

        if not email:
            return jsonify({'status': 'error', 'message': 'Failed to retrieve email from Google'}), 400

        # ✅ Check if user exists, if not, create one
        user = USER_collection.find_one({"email": email})
        if not user:
            user_data = {"_id": str(uuid.uuid4()), "email": email, "name": name}
            USER_collection.insert_one(user_data)

        # ✅ Generate JWT Token
        access_token = create_access_token(identity=email, expires_delta=datetime.timedelta(days=1))
        
        return jsonify({'status': 'success', 'access_token': access_token.decode('utf-8'), 'message': 'Google Login Successful'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@userBp.route("/user/studies", methods=['GET'])
@protected
def get_user_studies():
    current_user = get_jwt_identity()
    studies = list(STUDIES_collection.find({"studyCreatedBy.email": current_user}, {"_id": 0}))
    return jsonify({'status': 'success', 'studies': studies})
