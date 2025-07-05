import uuid
import jwt
import datetime
from flask import Blueprint, json, make_response, redirect, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, decode_token, jwt_required, get_jwt_identity
from DB.db import STUDY_USER_collection, STUDIES_collection,ARTICLE_collection
from extension import jwt,oauth,mail
from flask_mail import Message
def send_reset_email(email, token):
    reset_url = f"https://mindgenome.org/reset-password?token={token}"
    msg = Message("Password Reset Request",
                  sender="studies@tikuntech.com",
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
        user.pop("password")
        return jsonify({'status': 'success',"user":user, 'access_token': str(access_token)})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# Google OAuth Login
@studyuserBp.route("/mf2/login/google")
def google_login():
    frontend_origin = request.headers.get('Origin')  # Get frontend URL dynamically
    if not frontend_origin:
        return jsonify({"error": "No Origin header found"}), 400

    redirect_uri = request.host_url + "mf2/callback/google"  # Dynamically set callback URL
    response = oauth.google.authorize_redirect(redirect_uri)
    
    # Store frontend origin in a secure cookie
    response.set_cookie("frontend_origin", frontend_origin, httponly=True, secure=True, samesite="Strict")
    return response

@studyuserBp.route("/mf2/callback/google")
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
        user_info = oauth.google.get('https://openidconnect.googleapis.com/v1/userinfo').json()

        email = user_info.get('email')
        first_name = user_info.get('given_name')
        last_name = user_info.get('family_name')

        if not email:
            return jsonify({'status': 'error', 'message': 'Failed to retrieve email from Google'}), 400

        # Check if user exists, if not, create one
        user = STUDY_USER_collection.find_one({"email": email})
        if not user:
            user_data = {
                "_id": str(uuid.uuid4()),
                "auth_type": "google",
                "email": email,
                "firstName": first_name,
                "lastName": last_name,
                "companyName": ""
            }
            STUDY_USER_collection.insert_one(user_data)
        else:
            user_data = {
                "_id": user["_id"],
                "auth_type": user["auth_type"],
                "email": user["email"],
                "firstName": user.get("firstName", ""),
                "lastName": user.get("lastName", ""),
                "companyName": user.get("companyName", "")
            }

        # Generate JWT access token
        access_token = create_access_token(identity=email, expires_delta=datetime.timedelta(days=30))

        # Retrieve frontend origin from cookie
        frontend_origin = request.cookies.get("frontend_origin", "https://yourfrontend.com")
        dashboard_url = f"{frontend_origin}/dashboard"

        # Set response with cookies
        response = make_response(redirect(dashboard_url))

        # Store access token securely
        response.set_cookie(
            "authToken", access_token,
            httponly=True, secure=True, samesite="Strict", max_age=30*24*60*60
        )

        # Store user info in cookie (JSON format, URL-safe)
        response.set_cookie(
            "user", json.dumps(user_data),
            httponly=False, secure=True, samesite="Strict", max_age=30*24*60*60
        )

        return response

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
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


@studyuserBp.route("/mf2/user/me", methods=['GET'])
@jwt_required()
def get_user_detail():
    current_user = get_jwt_identity()
    user=STUDY_USER_collection.find_one({"email":current_user},{"password":0})
    return jsonify({'status': 'success', 'user': user})


@studyuserBp.route("/mf2/user/studies", methods=['GET'])
@jwt_required()
def get_user_studies():
    try:
        current_user = get_jwt_identity()
        studies = list(STUDIES_collection.find({"studyCreatedBy.user.email": current_user},{"studyData": 0, "studySummarizationData":0}))
        return jsonify({'status': 'success', 'studies': studies})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    
@studyuserBp.route("/mf2/user/articles", methods=['GET'])
@jwt_required()
def get_user_articles():
    try:
        current_user = get_jwt_identity()
        studies = list(ARTICLE_collection.find({"author.email": current_user}))
        return jsonify({'status': 'success', 'articles': studies})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400