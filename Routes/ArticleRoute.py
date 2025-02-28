import os
import uuid
from flask import Blueprint, request
from DB.db import ARTICLE_collection
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

articleBp = Blueprint('articleBp', __name__)

@articleBp.route("/mf2/articles",methods=['GET', 'POST', 'OPTIONS'])
@jwt_required()
def get_all_articles():
    try:
        all_articles=[i for i in ARTICLE_collection.find({})]
        return jsonify({"studies":all_articles})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    


