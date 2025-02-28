import certifi
from pymongo import MongoClient
uri = "mongodb+srv://dlovej009:dlovej009@cluster0.2pepq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri,tlsCAFile=certifi.where())
db = client['MF2']
STUDY_USER_collection = db['USERS']
STUDIES_collection = db['STUDIES']
