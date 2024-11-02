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
collection_mentees = db['Mentee_profiles']
collection_sessions = db['MentorshipSessions']
collection_feedback = db['MenteeFeedback']

# Load your JSON dataset (mentee feedback in this case)
with open('mentee_feedback.json', 'r') as file:
    data = json.load(file)

# Function to prepare documents based on data type
def prepare_documents(data):
    documents = []
    for item in data:
        # Check if the item is feedback data
        if 'feedback_provided' in item and 'feedback' in item:  # Feedback data
            feedback_doc = item.copy()
            # Use provided _id if exists or generate one based on feedback identifiers
            feedback_doc['_id'] = feedback_doc.get('_id', f"feedback_{random.randint(1000, 9999)}")
            documents.append(feedback_doc)
    return documents

# Insert documents into MongoDB
def insert_documents(documents, collection):
    try:
        if documents:
            result = collection.insert_many(documents)
            print(f"Inserted {len(result.inserted_ids)} documents into {collection.name}.")
        else:
            print("No documents to insert.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Prepare and insert feedback documents into MenteeFeedback collection
documents = prepare_documents(data)
insert_documents(documents, collection_feedback)
