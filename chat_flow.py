from flask import jsonify
from pymongo import MongoClient
import urllib.parse
import os

# MongoDB connection setup
username = urllib.parse.quote_plus("kjxsofttechpvtltd")  # Your actual username
password = urllib.parse.quote_plus("Rz@Fas092311")  # Your actual password
connection_string = f"mongodb+srv://{username}:{password}@kjxwebsite.3mup0.mongodb.net/ATMDatabase"
client = MongoClient(connection_string)
db = client['ATMDatabase']
mentors_collection = db['Mentor_profiles']
mentorship_sessions_collection = db['MentorshipSessions']

def get_number_value(value):
    if isinstance(value, dict):
        if '$numberDouble' in value:
            return value['$numberDouble']
        elif '$numberInt' in value:
            return value['$numberInt']
        else:
            return str(value)
    else:
        return str(value)

def get_chat_response(request_data):
    try:
        user_message = request_data.get("message", "").strip()
        current_tag = request_data.get("current_tag", "start_conversation")
        user_data = request_data.get("user_data", {})
        response = []
        options = []
        response_tag = current_tag  # Default response tag

        # Ensure 'user_name' is set in user_data
        user_name = user_data.get("user_name", "Devam")  # Default to 'Devam' if not provided

        # Start of conversation
        if current_tag == "start_conversation":
            response = [
                f"Hello {user_name}! Welcome to AskToMentor. I'm here to help you find a mentor or manage your sessions.",
                "How can I assist you today?"
            ]
            options = [
                {"text": "Find a Mentor", "value": "find_mentor"},
                {"text": "Session Scheduling and Management", "value": "session_scheduling"}
            ]
            response_tag = "main_menu"

        # Main menu
        elif current_tag == "main_menu":
            if user_message.lower() == "find_mentor":
                # Show main categories
                response = ["Great! Please select a category:"]
                options = [
                    {"text": "Data Science & Analytics", "value": "data_science_analytics"},
                    {"text": "IT & Networking", "value": "it_networking"},
                    {"text": "Software Development", "value": "software_development"},
                    {"text": "Account & Consulting", "value": "account_consulting"},
                    {"text": "Admin Support", "value": "admin_support"}
                ]
                response_tag = "select_category"
            elif user_message.lower() == "session_scheduling":
                response = [
                    "Would you like to schedule a new session or manage existing sessions?"
                ]
                options = [
                    {"text": "Schedule a New Session", "value": "schedule_new_session"},
                    {"text": "Manage Existing Sessions", "value": "manage_sessions"}
                ]
                response_tag = "session_scheduling_menu"
            else:
                response = ["Please select a valid option."]
                options = [
                    {"text": "Find a Mentor", "value": "find_mentor"},
                    {"text": "Session Scheduling and Management", "value": "session_scheduling"}
                ]
                response_tag = "main_menu"

        # Session Scheduling Menu
        elif current_tag == "session_scheduling_menu":
            if user_message.lower() == "schedule_new_session":
                # Show main categories
                response = ["Great! Please select a category for scheduling:"]
                options = [
                    {"text": "Data Science & Analytics", "value": "data_science_analytics"},
                    {"text": "IT & Networking", "value": "it_networking"},
                    {"text": "Software Development", "value": "software_development"},
                    {"text": "Account & Consulting", "value": "account_consulting"},
                    {"text": "Admin Support", "value": "admin_support"}
                ]
                response_tag = "select_category_for_scheduling"
            elif user_message.lower() == "manage_sessions":
                # Adjusted query using $elemMatch to search within the mentees array
                user_sessions = mentorship_sessions_collection.find({
                    "mentees": {
                        "$elemMatch": {
                            "mentee_name": {"$regex": f"^{user_name}$", "$options": "i"}
                        }
                    }
                })
                session_list = list(user_sessions)

                if session_list:
                    response = ["Here are your existing sessions:"]
                    options = []
                    for session in session_list:
                        for mentee in session.get('mentees', []):
                            if mentee.get('mentee_name', '').lower() == user_name.lower():
                                session_name = f"Session with {session.get('mentor_id')} on {mentee.get('requested_slot_date')}"
                                session_id = str(session.get('_id'))
                                options.append({
                                    "text": session_name,
                                    "value": session_id
                                })
                                break  # Since we found the mentee, no need to check other mentees
                    response_tag = "select_session_to_view"
                    return jsonify({
                        "response": response,
                        "tag": response_tag,
                        "options": options,
                        "user_data": user_data
                    })
                else:
                    response = ["You have no existing sessions."]
                    response_tag = "main_menu"
            else:
                response = ["Please select a valid option."]
                response_tag = "session_scheduling_menu"

        # User selects a session to view
        elif current_tag == "select_session_to_view":
            selected_session_id = user_message.strip()
            session = mentorship_sessions_collection.find_one({"_id": selected_session_id})

            if session:
                user_data["selected_session_id"] = selected_session_id
                mentee_details = None
                for mentee in session.get('mentees', []):
                    if mentee.get('mentee_name', '').lower() == user_name.lower():
                        mentee_details = mentee
                        break
                if mentee_details:
                    session_info = {
                        "Mentor ID": session.get('mentor_id'),
                        "Slot Date": mentee_details.get('requested_slot_date'),
                        "Slot": mentee_details.get('requested_slot'),
                        "Status": mentee_details.get('status'),
                        "Session Type": mentee_details.get('session_type'),
                        "Duration": mentee_details.get('session_actual_duration')
                    }
                    # Include session details in the response messages
                    response = ["Here are the details of your session:"]
                    for key, value in session_info.items():
                        response.append(f"{key}: {value}")
                    options = [{"text": "Edit Session", "url": "https://www.example.com/edit-session"}]
                    response_tag = "after_session_details"
                    return jsonify({
                        "response": response,
                        "tag": response_tag,
                        "options": options,
                        "user_data": user_data
                    })
                else:
                    response = ["Unable to find your session details."]
                    response_tag = "session_scheduling_menu"
            else:
                response = ["Session not found. Please select a valid session."]
                response_tag = "session_scheduling_menu"

        # After displaying session details
        elif current_tag == "after_session_details":
            response = ["Is there anything else I can assist you with?"]
            options = [
                {"text": "Return to Main Menu", "value": "start_conversation"},
                {"text": "Exit", "value": "goodbye"}
            ]
            response_tag = "main_menu"

        # Selecting a category
        elif current_tag == "select_category":
            category = user_message.lower()
            valid_categories = ["data_science_analytics", "it_networking", "software_development", "account_consulting", "admin_support"]
            if category in valid_categories:
                # Save the selected category
                user_data["selected_category"] = category
                # Show subcategories based on the selected category
                if category == "data_science_analytics":
                    subcategories = [
                        "Knowledge Representation",
                        "Machine Learning",
                        "Deep Learning",
                        "A/B Testing",
                        "Data Analytics",
                        "Experimentation & Testing",
                        "Data Visualization",
                        "Data Processing",
                        "Data Extraction"
                    ]
                elif category == "it_networking":
                    subcategories = [
                        "Database Administration",
                        "DevOps Engineering",
                        "Solution Architecture",
                        "Cloud Engineering",
                        "Business Applications Development",
                        "Systems Engineering",
                        "Network Security",
                        "IT Compliance",
                        "Information Security",
                        "Network Administration",
                        "System Administration"
                    ]
                elif category == "software_development":
                    subcategories = [
                        "Desktop Software Development",
                        "Ecommerce Website Development",
                        "Mobile App Development",
                        "Database Development",
                        "AR/VR Development",
                        "Emerging Tech",
                        "Firmware Development",
                        "Coding Tutoring",
                        "Agile Leadership",
                        "Scrum Leadership",
                        "Manual Testing",
                        "Automation Testing",
                        "Scripting & Automation",
                        "Back-End Development",
                        "CMS Development",
                        "Front-End Development",
                        "Full Stack Development"
                    ]
                elif category == "account_consulting":
                    subcategories = [
                        "Bookkeeping",
                        "Accounting",
                        "Financial Management/CFO",
                        "Financial Analysis & Modeling",
                        "Business Analysis & Strategy",
                        "Instructional Design",
                        "Management Consulting",
                        "Tax Preparation",
                        "Training & Development",
                        "HR Administration",
                        "Recruiting & Talent Sourcing"
                    ]
                elif category == "admin_support":
                    subcategories = [
                        "Data Entry",
                        "Transcription",
                        "Other Data Entry & Transcription Services",
                        "Dropshipping & Order Processing",
                        "General Research Services",
                        "Product Reviews",
                        "Other Market Research & Product Reviews",
                        "Qualitative Research",
                        "Market Research",
                        "Quantitative Research",
                        "Web & Software Product Research",
                        "Construction & Engineering Project Management",
                        "Other Project Management",
                        "Business Project Management",
                        "Digital Project Management",
                        "Supply Chain & Logistics Project Management",
                        "Development & IT Project Management",
                        "Healthcare Project Management"
                    ]
                response = ["Please select a subcategory:"]
                options = [{"text": subcat, "value": subcat} for subcat in subcategories]
                response_tag = "select_subcategory"
            else:
                response = ["Please select a valid category."]
                options = [
                    {"text": "Data Science & Analytics", "value": "data_science_analytics"},
                    {"text": "IT & Networking", "value": "it_networking"},
                    {"text": "Software Development", "value": "software_development"},
                    {"text": "Account & Consulting", "value": "account_consulting"},
                    {"text": "Admin Support", "value": "admin_support"}
                ]
                response_tag = "select_category"

        # Selecting a subcategory
        elif current_tag == "select_subcategory":
            subcategory = user_message.strip()
            user_data["selected_subcategory"] = subcategory
            # Map subcategory to database and show mentors
            mentors_in_subcategory = mentors_collection.find(
                {"other_details.subcategory": subcategory}
            ).limit(5)

            mentor_list = list(mentors_in_subcategory)
            if mentor_list:
                mentor_table_data = [
                    {
                        "Name": mentor['basic_info']['full_name'],
                        "Rating": get_number_value(mentor['rating_info']['rating']),
                        "Skills": ", ".join(mentor['professional_details']['skills']),
                        "Specialization": ", ".join(mentor['professional_details']['specialization']),
                        "Courses Taught": ", ".join(mentor['other_details']['courses_taught'])
                    }
                    for mentor in mentor_list
                ]

                response = ["Here are some mentors available in your selected subcategory:"]
                response_tag = "select_mentor"
                return jsonify({
                    "response": response,
                    "tag": response_tag,
                    "table_data": mentor_table_data,
                    "options": [{"text": mentor["Name"], "value": mentor["Name"]} for mentor in mentor_table_data],
                    "user_data": user_data
                })
            else:
                response = ["No mentors found in this subcategory. Please select another subcategory."]
                # Re-display subcategories
                category = user_data.get("selected_category", "")
                if category == "data_science_analytics":
                    subcategories = [
                        "Knowledge Representation",
                        "Machine Learning",
                        "Deep Learning",
                        "A/B Testing",
                        "Data Analytics",
                        "Experimentation & Testing",
                        "Data Visualization",
                        "Data Processing",
                        "Data Extraction"
                    ]
                elif category == "it_networking":
                    subcategories = [
                        "Database Administration",
                        "DevOps Engineering",
                        "Solution Architecture",
                        "Cloud Engineering",
                        "Business Applications Development",
                        "Systems Engineering",
                        "Network Security",
                        "IT Compliance",
                        "Information Security",
                        "Network Administration",
                        "System Administration"
                    ]
                elif category == "software_development":
                    subcategories = [
                        "Desktop Software Development",
                        "Ecommerce Website Development",
                        "Mobile App Development",
                        "Database Development",
                        "AR/VR Development",
                        "Emerging Tech",
                        "Firmware Development",
                        "Coding Tutoring",
                        "Agile Leadership",
                        "Scrum Leadership",
                        "Manual Testing",
                        "Automation Testing",
                        "Scripting & Automation",
                        "Back-End Development",
                        "CMS Development",
                        "Front-End Development",
                        "Full Stack Development"
                    ]
                elif category == "account_consulting":
                    subcategories = [
                        "Bookkeeping",
                        "Accounting",
                        "Financial Management/CFO",
                        "Financial Analysis & Modeling",
                        "Business Analysis & Strategy",
                        "Instructional Design",
                        "Management Consulting",
                        "Tax Preparation",
                        "Training & Development",
                        "HR Administration",
                        "Recruiting & Talent Sourcing"
                    ]
                elif category == "admin_support":
                    subcategories = [
                        "Data Entry",
                        "Transcription",
                        "Other Data Entry & Transcription Services",
                        "Dropshipping & Order Processing",
                        "General Research Services",
                        "Product Reviews",
                        "Other Market Research & Product Reviews",
                        "Qualitative Research",
                        "Market Research",
                        "Quantitative Research",
                        "Web & Software Product Research",
                        "Construction & Engineering Project Management",
                        "Other Project Management",
                        "Business Project Management",
                        "Digital Project Management",
                        "Supply Chain & Logistics Project Management",
                        "Development & IT Project Management",
                        "Healthcare Project Management"
                    ]
                options = [{"text": subcat, "value": subcat} for subcat in subcategories]
                response_tag = "select_subcategory"

        # Selecting a mentor
        elif current_tag == "select_mentor":
            selected_mentor = mentors_collection.find_one({"basic_info.full_name": user_message})
            if selected_mentor:
                user_data["selected_mentor"] = selected_mentor['basic_info']['full_name']
                response = [
                    f"Name: {selected_mentor['basic_info']['full_name']}",
                    f"Skills: {', '.join(selected_mentor['professional_details']['skills'])}",
                    f"Specialization: {', '.join(selected_mentor['professional_details']['specialization'])}",
                    f"Courses Taught: {', '.join(selected_mentor['other_details']['courses_taught'])}",
                    "Would you like to connect with this mentor?"
                ]
                options = [{"text": "Connect with Mentor", "value": "connect_with_mentor"}]
                response_tag = "view_mentor_availability"
            else:
                response = ["Sorry, I couldn't find that mentor. Please select another mentor."]
                response_tag = "select_mentor"

        elif current_tag == "view_mentor_availability":
            if user_message == "connect_with_mentor":
                selected_mentor = mentors_collection.find_one({"basic_info.full_name": user_data.get("selected_mentor")})
                if selected_mentor:
                    response = ["Here are the available days and time slots:"]
                    available_day_slots = selected_mentor["availability"].get("available_day_slots", {})
                    if available_day_slots:
                        options = []
                        for day, times in available_day_slots.items():
                            time_slots = times.split(',')
                            for time_slot in time_slots:
                                option_text = f"{day} {time_slot.strip()}"
                                options.append({"text": option_text, "value": option_text})
                        response_tag = "select_time_slot"
                        return jsonify({
                            "response": response,
                            "tag": response_tag,
                            "options": options,
                            "user_data": user_data
                        })
                    else:
                        response = ["The mentor has no available slots at the moment."]
                        response_tag = "start_conversation"
                else:
                    response = ["Sorry, I couldn't retrieve the mentor's availability."]
                    response_tag = "start_conversation"
            else:
                response = ["Please select a valid option."]
                response_tag = "view_mentor_availability"

        elif current_tag == "select_time_slot":
            # Save the selected time slot and redirect to booking link
            selected_time_slot = user_message.strip()
            user_data["selected_time_slot"] = selected_time_slot
            response = ["Redirecting you to the session booking page."]
            options = [{"text": "Proceed to Booking", "url": "https://www.example.com/booking"}]
            response_tag = "goodbye"

        # Schedule New Session Flow
        elif current_tag == "select_category_for_scheduling":
            category = user_message.lower()
            valid_categories = ["data_science_analytics", "it_networking", "software_development", "account_consulting", "admin_support"]
            if category in valid_categories:
                # Save the selected category
                user_data["selected_category"] = category
                # Show subcategories based on the selected category
                if category == "data_science_analytics":
                    subcategories = [
                        "Knowledge Representation",
                        "Machine Learning",
                        "Deep Learning",
                        "A/B Testing",
                        "Data Analytics",
                        "Experimentation & Testing",
                        "Data Visualization",
                        "Data Processing",
                        "Data Extraction"
                    ]
                elif category == "it_networking":
                    subcategories = [
                        "Database Administration",
                        "DevOps Engineering",
                        "Solution Architecture",
                        "Cloud Engineering",
                        "Business Applications Development",
                        "Systems Engineering",
                        "Network Security",
                        "IT Compliance",
                        "Information Security",
                        "Network Administration",
                        "System Administration"
                    ]
                elif category == "software_development":
                    subcategories = [
                        "Desktop Software Development",
                        "Ecommerce Website Development",
                        "Mobile App Development",
                        "Database Development",
                        "AR/VR Development",
                        "Emerging Tech",
                        "Firmware Development",
                        "Coding Tutoring",
                        "Agile Leadership",
                        "Scrum Leadership",
                        "Manual Testing",
                        "Automation Testing",
                        "Scripting & Automation",
                        "Back-End Development",
                        "CMS Development",
                        "Front-End Development",
                        "Full Stack Development"
                    ]
                elif category == "account_consulting":
                    subcategories = [
                        "Bookkeeping",
                        "Accounting",
                        "Financial Management/CFO",
                        "Financial Analysis & Modeling",
                        "Business Analysis & Strategy",
                        "Instructional Design",
                        "Management Consulting",
                        "Tax Preparation",
                        "Training & Development",
                        "HR Administration",
                        "Recruiting & Talent Sourcing"
                    ]
                elif category == "admin_support":
                    subcategories = [
                        "Data Entry",
                        "Transcription",
                        "Other Data Entry & Transcription Services",
                        "Dropshipping & Order Processing",
                        "General Research Services",
                        "Product Reviews",
                        "Other Market Research & Product Reviews",
                        "Qualitative Research",
                        "Market Research",
                        "Quantitative Research",
                        "Web & Software Product Research",
                        "Construction & Engineering Project Management",
                        "Other Project Management",
                        "Business Project Management",
                        "Digital Project Management",
                        "Supply Chain & Logistics Project Management",
                        "Development & IT Project Management",
                        "Healthcare Project Management"
                    ]
                response = ["Please select a subcategory for scheduling:"]
                options = [{"text": subcat, "value": subcat} for subcat in subcategories]
                response_tag = "select_subcategory_for_scheduling"
            else:
                response = ["Please select a valid category."]
                options = [
                    {"text": "Data Science & Analytics", "value": "data_science_analytics"},
                    {"text": "IT & Networking", "value": "it_networking"},
                    {"text": "Software Development", "value": "software_development"},
                    {"text": "Account & Consulting", "value": "account_consulting"},
                    {"text": "Admin Support", "value": "admin_support"}
                ]
                response_tag = "select_category_for_scheduling"

        elif current_tag == "select_subcategory_for_scheduling":
            subcategory = user_message.strip()
            user_data["selected_subcategory"] = subcategory
            # Map subcategory to database and show mentors
            mentors_in_subcategory = mentors_collection.find(
                {"other_details.subcategory": subcategory}
            ).limit(5)

            mentor_list = list(mentors_in_subcategory)
            if mentor_list:
                mentor_table_data = [
                    {
                        "Name": mentor['basic_info']['full_name'],
                        "Rating": get_number_value(mentor['rating_info']['rating']),
                        "Skills": ", ".join(mentor['professional_details']['skills']),
                        "Specialization": ", ".join(mentor['professional_details']['specialization']),
                        "Courses Taught": ", ".join(mentor['other_details']['courses_taught'])
                    }
                    for mentor in mentor_list
                ]

                response = ["Here are some mentors available in your selected subcategory:"]
                response_tag = "select_mentor_for_scheduling"
                return jsonify({
                    "response": response,
                    "tag": response_tag,
                    "table_data": mentor_table_data,
                    "options": [{"text": mentor["Name"], "value": mentor["Name"]} for mentor in mentor_table_data],
                    "user_data": user_data
                })
            else:
                response = ["No mentors found in this subcategory. Please select another subcategory."]
                # Re-display subcategories
                category = user_data.get("selected_category", "")
                if category == "data_science_analytics":
                    subcategories = [
                        "Knowledge Representation",
                        "Machine Learning",
                        "Deep Learning",
                        "A/B Testing",
                        "Data Analytics",
                        "Experimentation & Testing",
                        "Data Visualization",
                        "Data Processing",
                        "Data Extraction"
                    ]
                elif category == "it_networking":
                    subcategories = [
                        "Database Administration",
                        "DevOps Engineering",
                        "Solution Architecture",
                        "Cloud Engineering",
                        "Business Applications Development",
                        "Systems Engineering",
                        "Network Security",
                        "IT Compliance",
                        "Information Security",
                        "Network Administration",
                        "System Administration"
                    ]
                elif category == "software_development":
                    subcategories = [
                        "Desktop Software Development",
                        "Ecommerce Website Development",
                        "Mobile App Development",
                        "Database Development",
                        "AR/VR Development",
                        "Emerging Tech",
                        "Firmware Development",
                        "Coding Tutoring",
                        "Agile Leadership",
                        "Scrum Leadership",
                        "Manual Testing",
                        "Automation Testing",
                        "Scripting & Automation",
                        "Back-End Development",
                        "CMS Development",
                        "Front-End Development",
                        "Full Stack Development"
                    ]
                elif category == "account_consulting":
                    subcategories = [
                        "Bookkeeping",
                        "Accounting",
                        "Financial Management/CFO",
                        "Financial Analysis & Modeling",
                        "Business Analysis & Strategy",
                        "Instructional Design",
                        "Management Consulting",
                        "Tax Preparation",
                        "Training & Development",
                        "HR Administration",
                        "Recruiting & Talent Sourcing"
                    ]
                elif category == "admin_support":
                    subcategories = [
                        "Data Entry",
                        "Transcription",
                        "Other Data Entry & Transcription Services",
                        "Dropshipping & Order Processing",
                        "General Research Services",
                        "Product Reviews",
                        "Other Market Research & Product Reviews",
                        "Qualitative Research",
                        "Market Research",
                        "Quantitative Research",
                        "Web & Software Product Research",
                        "Construction & Engineering Project Management",
                        "Other Project Management",
                        "Business Project Management",
                        "Digital Project Management",
                        "Supply Chain & Logistics Project Management",
                        "Development & IT Project Management",
                        "Healthcare Project Management"
                    ]
                options = [{"text": subcat, "value": subcat} for subcat in subcategories]
                response_tag = "select_subcategory_for_scheduling"

        elif current_tag == "select_mentor_for_scheduling":
            selected_mentor = mentors_collection.find_one({"basic_info.full_name": user_message})
            if selected_mentor:
                user_data["selected_mentor"] = selected_mentor['basic_info']['full_name']
                response = [
                    f"Name: {selected_mentor['basic_info']['full_name']}",
                    f"Skills: {', '.join(selected_mentor['professional_details']['skills'])}",
                    f"Specialization: {', '.join(selected_mentor['professional_details']['specialization'])}",
                    f"Courses Taught: {', '.join(selected_mentor['other_details']['courses_taught'])}",
                    "Would you like to connect with this mentor?"
                ]
                options = [{"text": "Connect with Mentor", "value": "connect_with_mentor_for_scheduling"}]
                response_tag = "view_mentor_availability_for_scheduling"
            else:
                response = ["Sorry, I couldn't find that mentor. Please select another mentor."]
                response_tag = "select_mentor_for_scheduling"

        elif current_tag == "view_mentor_availability_for_scheduling":
            if user_message == "connect_with_mentor_for_scheduling":
                selected_mentor = mentors_collection.find_one({"basic_info.full_name": user_data.get("selected_mentor")})
                if selected_mentor:
                    response = ["Here are the available days and time slots:"]
                    available_day_slots = selected_mentor["availability"].get("available_day_slots", {})
                    if available_day_slots:
                        options = []
                        for day, times in available_day_slots.items():
                            time_slots = times.split(',')
                            for time_slot in time_slots:
                                option_text = f"{day} {time_slot.strip()}"
                                options.append({"text": option_text, "value": option_text})
                        response_tag = "select_time_slot_for_scheduling"
                        return jsonify({
                            "response": response,
                            "tag": response_tag,
                            "options": options,
                            "user_data": user_data
                        })
                    else:
                        response = ["The mentor has no available slots at the moment."]
                        response_tag = "start_conversation"
                else:
                    response = ["Sorry, I couldn't retrieve the mentor's availability."]
                    response_tag = "start_conversation"
            else:
                response = ["Please select a valid option."]
                response_tag = "view_mentor_availability_for_scheduling"

        elif current_tag == "select_time_slot_for_scheduling":
            # Save the selected time slot and create a new session
            selected_time_slot = user_message.strip()
            try:
                # Assume format "Day Time"
                parts = selected_time_slot.split(' ')
                day = parts[0]
                time = ' '.join(parts[1:])
                # Save session to MentorshipSessions collection
                new_session = {
                    "_id": "session_" + user_data.get("selected_mentor", "") + "_" + day + "_" + time.replace(":", "").replace(" ", ""),
                    "mentor_id": user_data.get("selected_mentor"),
                    "mentor_final_rating": None,
                    "mentees": [
                        {
                            "mentee_id": user_name,
                            "mentee_name": user_name,
                            "requested_slot_date": day,
                            "requested_slot": time,
                            "status": "Accepted",
                            "session_type": "One-on-One",
                            "session_actual_duration": "",
                            "session_held": "",
                            "mentor_response_time": "",
                            "feedback": "",
                            "mentee_rating": None,
                            "mentee_satisfaction_level": "",
                            "_id": "unique-session-id-" + user_name + "-" + day + "-" + time.replace(":", "").replace(" ", "")
                        }
                    ]
                }
                mentorship_sessions_collection.insert_one(new_session)
                response = ["Your session has been scheduled successfully!"]
                options = [{"text": "Proceed to Session Details", "url": "https://www.example.com/session-details"}]
                response_tag = "goodbye"
            except Exception as e:
                response = [f"An error occurred: {e}"]
                response_tag = "select_time_slot_for_scheduling"

        elif current_tag == "goodbye":
            response = ["Thank you for using AskToMentor. Have a great day!"]
            response_tag = "start_conversation"

        else:
            response = ["I'm sorry, I didn't understand that. Could you please try again?"]
            response_tag = "start_conversation"

        # Return the response as JSON
        return jsonify({
            "response": response,
            "tag": response_tag,
            "options": options,
            "user_data": user_data
        })

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
