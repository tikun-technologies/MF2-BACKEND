from flask_jwt_extended import JWTManager
from authlib.integrations.flask_client import OAuth

jwt = JWTManager()  # Initialize JWT without passing app yet
oauth = OAuth() 