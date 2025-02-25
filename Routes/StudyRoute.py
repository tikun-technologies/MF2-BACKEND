import os
# from turtle import pd
import uuid
from flask import Blueprint, request
from DB.db import STUDIES_collection,USER_collection
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from functions import get_file_data_for_study, protected

studyBp = Blueprint('studyBp', __name__)

@studyBp.route("/studies",methods=['GET', 'POST', 'OPTIONS'])
def study_list():
    all_studies=[i for i in STUDIES_collection.find({})]
    return jsonify({"studies":all_studies})



@studyBp.route("/add/study", methods=["GET","POST"])
@protected
def insert_study():
    try:
        current_user = get_jwt_identity()  # ✅ Get user's email from JWT

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
        result["studyCreatedBy"] = {"email": current_user}

        # Insert the study into the database
        study = STUDIES_collection.insert_one(result)

        return jsonify({
            "status": "success",
            "message": "Study data uploaded successfully",
            "study_id": str(study.inserted_id)
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    
    
@studyBp.route("/study/<study_id>", methods=['GET'])
@protected
def get_study_by_id(study_id):
    study = STUDIES_collection.find_one({"_id": study_id})
    if not study:
        return jsonify({'status': 'error', 'message': 'Study not found'}), 404
    return jsonify({'status': 'success', 'study': study})

# Delete Study
@studyBp.route("/study/<study_id>", methods=['DELETE'])
@protected
def delete_study(study_id):
    result = STUDIES_collection.delete_one({"_id": study_id})
    if result.deleted_count == 0:
        return jsonify({'status': 'error', 'message': 'Study not found'}), 404
    return jsonify({'status': 'success', 'message': 'Study deleted successfully'})
