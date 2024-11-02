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
collection_sessions = db['MentorshipSessions']

# Load your JSON dataset for mentorship sessions
with open('C:\KJX\ATMChatbot\Data-json\mentorship_sessions.json', 'r') as file:
    data = json.load(file)

# Prepare documents with unique _id for each session
def prepare_session_documents(data):
    documents = []
    for session in data:
        session_doc = session.copy()
        # Use provided _id if exists or generate one based on session identifiers
        session_doc['_id'] = session_doc.get('_id', f"session_{random.randint(1000, 9999)}")
        documents.append(session_doc)
    return documents

# Insert session documents
def insert_documents(documents, collection):
    try:
        if documents:
            result = collection.insert_many(documents)
            print(f"Inserted {len(result.inserted_ids)} session documents.")
        else:
            print("No documents to insert.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Insert into MentorshipSessions collection
documents = prepare_session_documents(data)
insert_documents(documents, collection_sessions)
