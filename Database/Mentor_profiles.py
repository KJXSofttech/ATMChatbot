from pymongo import MongoClient
import json
import urllib.parse
import random

# MongoDB connection setup
username = urllib.parse.quote_plus("kjxsofttechpvtltd")
password = urllib.parse.quote_plus("Rz@Fas092311")
connection_string = f"mongodb+srv://kjxsofttechpvtltd:{password}@kjxwebsite.3mup0.mongodb.net/"

client = MongoClient(connection_string, tls=True)
db = client['ATMDatabase']
collection_mentors = db['Mentor_profiles']

# Load your JSON dataset for mentors
with open('mentor_profiles.json', 'r') as file:
    data = json.load(file)

# Debug print to verify structure
print("Data loaded:", data)

# Flatten the nested data structure and prepare documents with unique _id for each mentor
def prepare_mentor_documents(data):
    documents = []
    if isinstance(data, list) and len(data) > 0 and 'subcategories' in data[0]:  # Check for 'subcategories' key in the first element of the array
        subcategories = data[0]['subcategories']
        for category, subcats in subcategories.items():
            for subcat, mentors in subcats.items():
                for mentor in mentors:
                    if isinstance(mentor, dict) and 'basic_info' in mentor:
                        mentor_doc = mentor.copy()
                        # Generate custom _id using the first name and a random number
                        first_name = mentor_doc['basic_info']['full_name'].split()[0]
                        random_number = random.randint(1000, 9999)
                        mentor_doc['_id'] = f"{first_name}_{random_number}"
                        documents.append(mentor_doc)
                    else:
                        print("Skipping invalid or improperly formatted mentor entry:", mentor)
    else:
        print("Data structure does not contain 'subcategories'.")
    return documents

# Insert mentor documents
def insert_documents(documents, collection):
    try:
        if documents:
            result = collection.insert_many(documents)
            print(f"Inserted {len(result.inserted_ids)} mentor documents.")
        else:
            print("No documents to insert.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Insert into Mentor_profiles collection
documents = prepare_mentor_documents(data)
insert_documents(documents, collection_mentors)
