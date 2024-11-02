username = urllib.parse.quote_plus("kjxsofttechpvtltd")  # Your actual username
password = urllib.parse.quote_plus("Rz@Fas092311")  # Your actual password
connection_string = f"mongodb+srv://{username}:{password}@kjxwebsite.3mup0.mongodb.net/ATMDatabase"
client = MongoClient(connection_string)
db = client['ATMDatabase']
mentors_collection = db['Mentor_profiles']
mentorship_sessions_collection = db['MentorshipSessions']