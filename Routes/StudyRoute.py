import os
from turtle import pd
import uuid
from flask import Blueprint, request
from DB.db import STUDIES_collection,USER_collection
from flask import jsonify

from functions import get_file_data_for_study

studyBp = Blueprint('studyBp', __name__)

@studyBp.route("/studies",methods=['GET', 'POST', 'OPTIONS'])
def study_list():
    all_studies=[i for i in STUDIES_collection.find({})]
    return jsonify({"studies":all_studies})



@studyBp.route("/add/study", methods=["GET","POST"])
def insert_study():
    try:
        print(request.files)
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Save the file temporarily
        file_content = file.read()
        print(file_content)
        # Process the file (Modify `get_file_data_for_study` to accept bytes)
        result = get_file_data_for_study(file_content)
        study = STUDIES_collection.insert_one(result)


        return jsonify({"status": "success", "message": "Study data uploaded successfully", "study_id": study.inserted_id})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400