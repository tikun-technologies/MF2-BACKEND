import datetime
import os
import uuid
from flask import Blueprint, request
from DB.db import ARTICLE_collection,STUDY_USER_collection
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from functions import upload_to_azure

articleBp = Blueprint('articleBp', __name__)

@articleBp.route("/mf2/articles",methods=['GET', 'POST', 'OPTIONS'])
@jwt_required()
def get_all_articles():
    try:
        all_articles=[i for i in ARTICLE_collection.find({})]
        return jsonify({"articles":all_articles})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    

@articleBp.route("/mf2/add/article",methods=['POST'])
@jwt_required()
def add_article():
    try:
        data = request.form
        images = request.files.getlist("images")
        thumbnail=request.files.get("thumbnail")# Multiple file uploads
        
        # Upload images/videos to Azure and get URLs
        thumbnail_url=""
        if thumbnail:
            thumbnail_url=upload_to_azure(thumbnail)
        
        media_urls = [upload_to_azure(file) for file in images if file]
        current_user= get_jwt_identity()
        # Create article document
        article = {
            "_id":str(uuid.uuid4()),
            "title": data.get("title"),
            "slug": data.get("title").replace(" ", "-").lower(),  # Generate slug
            "content": data.get("content"),
            "summary": data.get("summary"),
            "author": STUDY_USER_collection.find_one({"email": current_user},{"password": 0}),
            "tags": data.get("tags").split(","),
            "category": data.get("category"),
            "thumbnailUrl":thumbnail_url,  # First file as thumbnail
            "media": media_urls,
            "publishedAt": datetime.datetime.now(datetime.timezone.utc),
            "updatedAt": datetime.datetime.now(datetime.timezone.utc),
        }
        # Insert into MongoDB
        result = ARTICLE_collection.insert_one(article)
        
        return jsonify({"message": "Article added successfully", "article_id": str(result.inserted_id)}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
    
@articleBp.route("/mf2/article/<article_id>", methods=['GET'])
@jwt_required()
def get_article_by_id(article_id):
    try:
        print("hihihihih")
        article = ARTICLE_collection.find_one({"_id": article_id})
        if not article:
            return jsonify({'status': 'error', 'message': 'article not found'}), 404
        return jsonify({'status': 'success', 'article': article})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# Delete article
@articleBp.route("/mf2/article/<article_id>", methods=['DELETE'])
@jwt_required()
def delete_article(article_id):
    try:
        result = ARTICLE_collection.delete_one({"_id": article_id})
        if result.deleted_count == 0:
            return jsonify({'status': 'error', 'message': 'article not found'}), 404
        return jsonify({'status': 'success', 'message': 'article deleted successfully'})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
