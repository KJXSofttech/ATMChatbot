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
collection_feedback = db['MenteeFeedback']

# Load your JSON dataset for mentee feedback
with open('mentee_feedback.json', 'r') as file:
    data = json.load(file)

# Prepare documents with unique _id for each feedback
def prepare_feedback_documents(data):
    documents = []
    for feedback in data:
        feedback_doc = feedback.copy()
        # Use provided _id if exists or generate one based on feedback identifiers
        feedback_doc['_id'] = feedback_doc.get('_id', f"feedback_{random.randint(1000, 9999)}")
        documents.append(feedback_doc)
    return documents

# Insert feedback documents
def insert_documents(documents, collection):
    try:
        if documents:
            result = collection.insert_many(documents)
            print(f"Inserted {len(result.inserted_ids)} feedback documents.")
        else:
            print("No documents to insert.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Insert into MenteeFeedback collection
documents = prepare_feedback_documents(data)
insert_documents(documents, collection_feedback)
