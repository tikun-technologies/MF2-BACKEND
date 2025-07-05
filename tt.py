from DB.db import STUDIES_collection

from functions import flatten_all_segments
all_studies=STUDIES_collection.find({},{"studyData": 1,"_id":0})

for i in all_studies:
     # Print the study ID
    print(i)
    # print(i.get("_id")) 
    flattened_data = flatten_all_segments(i)
    print(flattened_data)
    update_field = {"$set": {"studyData": flattened_data}}  # or any key-value pair

    result = STUDIES_collection.update_many({}, update_field)
    print(f"Updated {result.modified_count} documents with flattened study data.")