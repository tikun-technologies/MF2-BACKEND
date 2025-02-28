import uuid
import jwt
import datetime
from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, decode_token, jwt_required, get_jwt_identity
from DB.db import STUDY_USER_collection, STUDIES_collection
from DB.extension import jwt,oauth




from flask_mail import Mail, Message

# Configure Flask-Mail
mail = Mail()
def send_reset_email(email, token):
    reset_url = f"https://tikunstudies.netlify.app/reset-password?token={token}"
    msg = Message("Password Reset Request",
                  sender="noreply@yourapp.com",
                  recipients=[email])
    msg.body = f"""To reset your password, click the following link:
{reset_url}
If you did not request this, ignore this email.
"""
    mail.send(msg)








bcrypt = Bcrypt()

studyuserBp = Blueprint('studyuserBp', __name__)

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

@studyuserBp.route("/mf2/signup", methods=['POST'])
def signup():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        user=STUDY_USER_collection.find_one({"email": email})
        if user:
            if user.get("auth_type")=="google":
                return jsonify({'status': 'error', 'message': 'This email is registered using Google. Please log in with Google.'}), 400
            else:
                return jsonify({'status': 'error', 'message': 'Email already exists'}), 400
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user_data = data
        
        user_data["_id"]= str(uuid.uuid4())
        user_data["password"]= hashed_password
        user_data["auth_type"]="gmail"
        user_data["email"]=email
        user_data["firstName"]=data.get('firstName')
        user_data["lastName"]=data.get("lastName")
        user_data["companyName"]=data.get("companyName")
            
        STUDY_USER_collection.insert_one(user_data)
        return jsonify({'status': 'success', 'message': 'User registered successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# Login (Username/Password)
@studyuserBp.route("/mf2/login", methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        user = STUDY_USER_collection.find_one({"email": email})
        
        if not user or not bcrypt.check_password_hash(user['password'], password):
            return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401
        
        access_token = create_access_token(identity=email, expires_delta=datetime.timedelta(days=30))
        return jsonify({'status': 'success', 'access_token': access_token})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# Google OAuth Login
@studyuserBp.route("/mf2/login/google")
def google_login():
    redirect_uri = request.host_url + "mf2/callback/google"
    return oauth.google.authorize_redirect(redirect_uri)

# Google OAuth Callback
@studyuserBp.route("/mf2/callback/google")
def google_callback():
    try:
        # ✅ Exchange authorization code for an access token
        token = oauth.google.authorize_access_token()
        print("Google Token:", token)  # Debugging

        # ✅ Get user info using the access token
        user_info = oauth.google.get('https://openidconnect.googleapis.com/v1/userinfo').json()
        print("User Info:", user_info)  # Debugging

        email = user_info.get('email')
        first_name = user_info.get('given_name')  # ✅ Extract first name
        last_name = user_info.get('family_name')

        if not email:
            return jsonify({'status': 'error', 'message': 'Failed to retrieve email from Google'}), 400

        # ✅ Check if user exists, if not, create one
        user = STUDY_USER_collection.find_one({"email": email})
        if not user:
            user_data={}
            user_data["_id"]= str(uuid.uuid4())
            user_data["auth_type"]="google"
            user_data["email"]=email
            user_data["firstName"]=first_name
            user_data["lastName"]=last_name
            user_data["companyName"]=""
            STUDY_USER_collection.insert_one(user_data)

        # ✅ Generate JWT Token
        access_token = create_access_token(identity=email, expires_delta=datetime.timedelta(days=30))
        
        return jsonify({'status': 'success', 'access_token': access_token, 'message': 'Google Login Successful'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@studyuserBp.route("/mf2/reset-password-request", methods=['POST'])
def reset_password_request():
    try:
        data = request.json
        email = data.get("email")
        user = STUDY_USER_collection.find_one({"email": email})
        
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        if user.get("auth_method") == "google":
            return jsonify({'status': 'error', 'message': 'This account is registered with Google. Use Google Login.'}), 400
        
        # Generate password reset token (expires in 1 hour)
        reset_token = create_access_token(identity=email, expires_delta=datetime.timedelta(minutes=10))

        # Send reset email
        send_reset_email(email, reset_token)

        return jsonify({'status': 'success', 'message': 'Password reset link sent to your email'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    
@studyuserBp.route("/mf2/reset-password", methods=['POST'])
@jwt_required()  # ✅ Ensures the token is passed in the request
def reset_password():
    try:
        data = request.json
        new_password = data.get("new_password")

        # ✅ Get email from the JWT token
        email = get_jwt_identity()

        user = STUDY_USER_collection.find_one({"email": email})
        if not user:
            return jsonify({'status': 'error', 'message': 'Invalid token or user not found'}), 400

        # ✅ Hash the new password
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

        # ✅ Update password in database
        STUDY_USER_collection.update_one({"email": email}, {"$set": {"password": hashed_password}})

        return jsonify({'status': 'success', 'message': 'Password reset successfully'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400




























# ####                  #####  user data extraction routes ######################################################

@studyuserBp.route("/mf2/user/studies", methods=['GET'])
@jwt_required()
def get_user_studies():
    current_user = get_jwt_identity()
    studies = list(STUDIES_collection.find({"studyCreatedBy.email": current_user}, {"_id": 0}))
    return jsonify({'status': 'success', 'studies': studies})
