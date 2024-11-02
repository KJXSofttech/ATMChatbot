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
collection_mentees = db['Mentee_profiles']

# Load your JSON dataset for mentees
with open('mentee_profiles.json', 'r') as file:
    data = json.load(file)

# Prepare documents with unique _id for each mentee
def prepare_mentee_documents(data):
    documents = []
    for mentee in data:
        mentee_doc = mentee.copy()
        # Generate custom _id using the first name and a random number
        first_name = mentee_doc['basic_info']['full_name'].split()[0]
        random_number = random.randint(1000, 9999)
        mentee_doc['_id'] = f"{first_name}_{random_number}"
        documents.append(mentee_doc)
    return documents

# Insert mentee documents
def insert_documents(documents, collection):
    try:
        if documents:
            result = collection.insert_many(documents)
            print(f"Inserted {len(result.inserted_ids)} mentee documents.")
        else:
            print("No documents to insert.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Insert into Mentee_profiles collection
documents = prepare_mentee_documents(data)
insert_documents(documents, collection_mentees)
