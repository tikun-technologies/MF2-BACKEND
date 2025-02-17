# # import json



# # import pandas as pd

# # # Load the CSV file
# # file_path = "Untitled spreadsheet - Sheet1.csv"
# # df = pd.read_csv(file_path)

# # # Display the first few rows to understand the structure
# # df.head()


# # # Identifying column categories
# # mindset_cols = [col for col in df.columns if "Mindset" in str(col)]
# # gender_cols = [col for col in df.columns if "Male" in str(col) or "Female" in str(col)]
# # age_cols = [col for col in df.columns if any(age in str(col) for age in ["13 - 17", "18 - 24", "25 - 34", "35 - 44", "45 - 54", "55 - 64", "65+"])]
# # total_col = "Total"

# # # Prelim-Answer Segments: Columns that are not in the above categories and are not "Total"
# # prelim_answer_cols = [col for col in df.columns[3:] if col not in mindset_cols + gender_cols + age_cols + [total_col] and "Unnamed" not in str(col)]

# # # Extracting categorized data
# # categorized_data = {
# #     "Mindsets": mindset_cols,
# #     "Gender Segments": gender_cols,
# #     "Age Segments": age_cols,
# #     "Prelim-Answer Segments": prelim_answer_cols
# # }

# # categorized_data

# # # Extract the base size value
# # base_size = df.iloc[0, 2]

# # # Initialize the JSON structure
# # output_json = {
# #     "Base Size": base_size,
# #     "Questions": []
# # }

# # # Iterate through the dataframe to extract questions and their options
# # current_question = None

# # for index, row in df.iterrows():
# #     if isinstance(row[1], str) and row[1].startswith("Question"):  # Identify question rows
# #         current_question = {
# #             "Question": row[1].split(": ", 1)[1] if ": " in row[1] else row[1],
# #             "options": []
# #         }
# #         output_json["Questions"].append(current_question)
    
# #     elif isinstance(row[0], str) and current_question:  # Identify option rows
# #         option_data = {
# #             "optiontext": row[1],
# #             "Total":row[2],
# #             "Mindsets": [],
# #             "Gender Segments": {},
# #             "Age Segments": {},
# #             "Prelim-Answer Segments": [],
# #             "Total": row[total_col] if total_col in df.columns else None
# #         }
        
# #         # Extract data dynamically based on the categorized columns
# #         for col in mindset_cols:
# #             option_data["Mindsets"].append({col:row[col]}) 

# #         for col in gender_cols:
# #             print(col)
# #             option_data["Gender Segments"][col] = row[col]

# #         for col in age_cols:
# #             option_data["Age Segments"][col] = row[col]

# #         for col in prelim_answer_cols:
# #             option_data["Prelim-Answer Segments"].append({col:row[col]}) 

# #         current_question["options"].append(option_data)

# # # Convert to JSON format
# # json_output = json.dumps(output_json, indent=4)
# # f=open("output.json","w", encoding="utf-8")
# # f.write(str(json_output))
# # print(json_output)


# def get_file_data_for_study():


#     import json
#     import pandas as pd

#     # Load the Excel file
#     file_path = "base_input_study.xlsx"  # Replace with actual file path
#     xls = pd.ExcelFile(file_path)

#     # Function to process a single sheet

#     def process_sheet_for_info(df):
#         # Initialize variables
#         study_info = {
#             "study_title": None,
#             "study_id": None,
#             "study_started": None,
#             "study_ended": None,
#             "study_status": False,
#             "study_respondents": None,
#             "study_keywords": []
#         }

#         # Iterate over each row and extract information
#         for i in range(len(df)):
#             row = df.iloc[i]
#             print(row)
#             if "Study Title" in str(row[0]):
#                 study_info["study_title"] = str(row[1]).strip()
            
#             elif "Identification Number of the study" in str(row[0]):
#                 study_info["study_id"] = str(row[1]).strip()
            
#             elif "Date when the study was run" in str(row[0]):
#                 date_range = str(row[1]).strip().replace("(", "").replace(")", "").split("-")
#                 study_info["study_started"] = date_range[0].strip()
#                 study_info["study_ended"] = date_range[1].strip() if len(date_range) > 1 else None
            
#             elif "Number of respondents" in str(row[0]):
#                 study_info["study_respondents"] = int(row[1]) if pd.notna(row[1]) else None
            
#             elif "Keywords" in str(row[0]):
#                 study_info["study_keywords"] = [kw.strip() for kw in str(row[1]).split(",") if kw.strip()]
#         return study_info
#         # Print the extracted information
#         # print(study_info)
#     def process_sheet(df):
#         # Identifying column categories
#         mindset_cols = [col for col in df.columns if "Mindset" in str(col)]
#         gender_cols = [col for col in df.columns if "Male" in str(col) or "Female" in str(col)]
#         age_cols = [col for col in df.columns if any(age in str(col) for age in ["13 - 17", "18 - 24", "25 - 34", "35 - 44", "45 - 54", "55 - 64", "65+"])]
#         total_col = "Total"

#         # Prelim-Answer Segments: Columns that are not in the above categories and are not "Total"
#         prelim_answer_cols = [col for col in df.columns[3:] if col not in mindset_cols + gender_cols + age_cols + [total_col] and "Unnamed" not in str(col)]

#         # Extract the base size value
#         base_size = df.iloc[0, 2]

#         # Initialize JSON structure
#         output_json = {
#             "Base Size": base_size,
#             "Questions": []
#         }

#         # Iterate through the dataframe to extract questions and options
#         current_question = None
#         for index, row in df.iterrows():
#             if isinstance(row[1], str) and row[1].startswith("Question"):  # Identify question rows
#                 current_question = {
#                     "Question": row[1].split(": ", 1)[1] if ": " in row[1] else row[1],
#                     "options": []
#                 }
#                 output_json["Questions"].append(current_question)
            
#             elif isinstance(row[0], str) and current_question:  # Identify option rows
#                 option_data = {
#                     "optiontext": row[1],
#                     "Total": row[total_col] if total_col in df.columns else None,
#                     "Mindsets": [],
#                     "Gender Segments": {},
#                     "Age Segments": {},
#                     "Prelim-Answer Segments": []
#                 }

#                 # Extract data dynamically based on the categorized columns
#                 for col in mindset_cols:
#                     option_data["Mindsets"].append({col: row[col]}) 

#                 for col in gender_cols:
#                     option_data["Gender Segments"][col] = row[col]

#                 for col in age_cols:
#                     option_data["Age Segments"][col] = row[col]

#                 for col in prelim_answer_cols:
#                     option_data["Prelim-Answer Segments"].append({col: row[col]}) 

#                 current_question["options"].append(option_data)

#         return output_json

#     # Process all sheets
#     print(xls.sheet_names)
#     study_info=process_sheet_for_info(xls.parse(sheet_name="Information Block", header=None).dropna(how="all"))
#     output_data = {sheet: process_sheet(xls.parse(sheet)) for sheet in xls.sheet_names[5:]}
#     print(study_info)
#     # # Save output as JSON
#     # json_output = json.dumps(output_data, indent=4)
#     # with open("output.json", "w", encoding="utf-8") as f:
#     #     f.write(json_output)
#     # print(study_info)
#     # Print output JSON
#     # print(json_output)



import json
import uuid
import pandas as pd
from io import BytesIO

def get_file_data_for_study(file_bytes):
    # Load the Excel file from memory
    xls = pd.ExcelFile(BytesIO(file_bytes))

    # Function to process a single sheet
    def process_sheet_for_info(df):
        study_info = {
            "study_title": None,
            "study_id": None,
            "study_started": None,
            "study_ended": None,
            "study_status": False,
            "study_respondents": None,
            "study_keywords": []
        }

        for i in range(len(df)):
            row = df.iloc[i]
            if "Study Title" in str(row[0]):
                study_info["study_title"] = str(row[1]).strip()
            elif "Identification Number of the study" in str(row[0]):
                study_info["study_id"] = str(row[1]).strip()
            elif "Date when the study was run" in str(row[0]):
                date_range = str(row[1]).strip().replace("(", "").replace(")", "").split("-")
                study_info["study_started"] = date_range[0].strip()
                study_info["study_ended"] = date_range[1].strip() if len(date_range) > 1 else None
                study_info["study_status"] = date_range[1].strip() if len(date_range) > 1 else None
            elif "Number of respondents" in str(row[0]):
                study_info["study_respondents"] = int(row[1]) if pd.notna(row[1]) else None
            elif "Keywords" in str(row[0]):
                study_info["study_keywords"] = [kw.strip() for kw in str(row[1]).split(",") if kw.strip()]
        return study_info

    def process_sheet(df):
        mindset_cols = [col for col in df.columns if "Mindset" in str(col)]
        gender_cols = [col for col in df.columns if "Male" in str(col) or "Female" in str(col)]
        age_cols = [col for col in df.columns if any(age in str(col) for age in ["13 - 17", "18 - 24", "25 - 34", "35 - 44", "45 - 54", "55 - 64", "65+"])]
        total_col = "Total"

        prelim_answer_cols = [col for col in df.columns[3:] if col not in mindset_cols + gender_cols + age_cols + [total_col] and "Unnamed" not in str(col)]
        base_size = df.iloc[0, 2]

        output_json = {
            "Base Size": base_size,
            "Questions": []
        }

        current_question = None
        for index, row in df.iterrows():
            if isinstance(row[1], str) and row[1].startswith("Question"):
                current_question = {
                    "Question": row[1].split(": ", 1)[1] if ": " in row[1] else row[1],
                    "options": []
                }
                output_json["Questions"].append(current_question)
            elif isinstance(row[0], str) and current_question:
                option_data = {
                    "optiontext": row[1],
                    "Total": row[total_col] if total_col in df.columns else None,
                    "Mindsets": [],
                    "Gender Segments": {},
                    "Age Segments": {},
                    "Prelim-Answer Segments": []
                }

                for col in mindset_cols:
                    option_data["Mindsets"].append({col: row[col]}) 
                for col in gender_cols:
                    option_data["Gender Segments"][col] = row[col]
                for col in age_cols:
                    option_data["Age Segments"][col] = row[col]
                for col in prelim_answer_cols:
                    option_data["Prelim-Answer Segments"].append({col: row[col]}) 

                current_question["options"].append(option_data)

        return output_json

    print(xls.sheet_names)
    study_info = process_sheet_for_info(xls.parse(sheet_name="Information Block", header=None).dropna(how="all"))
    # output_data = {sheet: process_sheet(xls.parse(sheet)) for sheet in xls.sheet_names[5:]}
    # Extract base values for all sheets
    def extract_base_values(df):
        base_values = {}
        for col in df.columns[3:]:
            base_values[col] = df.iloc[0][col] if not pd.isna(df.iloc[0][col]) else None
        return base_values
    output_data = {}
    for sheet in xls.sheet_names[5:]:
        df = xls.parse(sheet)
        output_data[sheet] = {
            "Base Values": extract_base_values(df),
            "Data": process_sheet(df)
        }
        print(output_data)

    return {"_id":str(uuid.uuid4()),
            "studyTitle":study_info['study_title'],
            "studyStarted":study_info['study_started'],
            "studyEnded":study_info['study_ended'],
            "studyStatus":study_info['study_status'],
            "studyRespondents":study_info['study_respondents'],
            "studyKeywords":study_info['study_keywords'],
            "studyData":output_data
            }
