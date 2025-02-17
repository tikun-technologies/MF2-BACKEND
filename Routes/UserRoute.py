import uuid
from flask import Blueprint, request

from Model.User import UserSchema
from DB.db import STUDIES_collection,USER_collection
from flask import jsonify

userBp = Blueprint('userBp', __name__)

@userBp.route("/user/create")
def user_list():
    all_users=[i for i in USER_collection.find({})]
    return jsonify(all_users)

@userBp.route("/create", methods=['POST'])
def create_user():
    try:
        print("i am in try block ")
        email = request.json.get('email')
        print(email)
        if USER_collection.find_one({"email":email}):
            return jsonify({'status': 'success', 'message': f'User already exist with email {email} '})
        else:
            print("in the second it ")
            user_data = request.json
            user_schema = UserSchema()
            user_data["_id"] = str(uuid.uuid4())
            result = user_schema.load(user_data)
            inserted_user = USER_collection.insert_one(result).inserted_id
            return jsonify({'status': 'success', 'message': 'User added successfully', 'user_id': str(inserted_user)})
           
          
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    
@userBp.route('/test', methods=['GET'])
def test_study():
    return jsonify({"message": "Study route is working!"})