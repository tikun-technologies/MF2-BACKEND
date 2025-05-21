import os
# import threading
from multiprocessing import Process
from flask import Blueprint, request
from DB.db import STUDIES_collection,STUDY_USER_collection
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from functions import get_file_data_for_study, get_ppt

studyBp = Blueprint('studyBp', __name__)

@studyBp.route("/mf2/studies",methods=['GET', 'POST', 'OPTIONS'])
@jwt_required()
def study_list():
    try:
        all_studies=[i for i in STUDIES_collection.find({})]
        return jsonify({"studies":all_studies})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400



@studyBp.route("/mf2/add/study", methods=["GET","POST"])
@jwt_required()
def insert_study():
    # try:
        current_user = get_jwt_identity()  # ✅ Get user's email from JWT
        print(current_user)
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Read file content
        file_content = file.read()

        # Process the file (Modify `get_file_data_for_study` to accept bytes)
        result = get_file_data_for_study(file_content)

        # ✅ Add the authenticated user's email to `studyCreatedBy`
        result["studyCreatedBy"] = {"user":STUDY_USER_collection.find_one({"email": current_user},{"password": 0})}
        # print(result)
        auth_header = request.headers.get('Authorization', '')
        user_token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else None

        # Insert the study into the database
        study = STUDIES_collection.insert_one(result)
        p = Process(target=get_ppt, args=(study.inserted_id, user_token))
        # ppt_thread = threading.Thread(target=get_ppt, args=(study.inserted_id, user_token))
        # ppt_thread.start()
        p.start()

        return jsonify({
            "status": "success",
            "message": "Study data uploaded successfully",
            "study_id": str(study.inserted_id)
        })

    # except Exception as e:
    #     return jsonify({"status": "error", "message": str(e)}), 400
    
    
@studyBp.route("/mf2/study/<study_id>", methods=['GET'])
@jwt_required()
def get_study_by_id(study_id):
    try:
        study = STUDIES_collection.find_one({"_id": study_id})
        if not study:
            return jsonify({'status': 'error', 'message': 'Study not found'}), 404
        return jsonify({'status': 'success', 'study': study})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# Delete Study
@studyBp.route("/mf2/study/<study_id>", methods=['DELETE'])
@jwt_required()
def delete_study(study_id):
    try:
        result = STUDIES_collection.delete_one({"_id": study_id})
        if result.deleted_count == 0:
            return jsonify({'status': 'error', 'message': 'Study not found'}), 404
        return jsonify({'status': 'success', 'message': 'Study deleted successfully'})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
