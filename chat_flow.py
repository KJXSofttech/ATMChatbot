from flask import jsonify

def get_chat_response(request_data):
    try:
        user_message = request_data.get("message", "").lower()
        current_tag = request_data.get("current_tag", "start_conversation")
        user_data = request_data.get("user_data", {})
        response = []
        options = []

        if current_tag == "start_conversation":
            response = [
                "Hello! Welcome to AskToMentor. I'm here to assist you in connecting with the perfect mentor.",
                "How can I help you today?"
            ]
            options = [
                {"text": "Find a Mentor", "value": "find_mentor"},
                {"text": "Learn About Programs", "value": "learn_programs"},
                {"text": "Get Technical Support", "value": "get_support"},
                {"text": "Provide Feedback", "value": "provide_feedback"}
            ]
            response_tag = "main_menu"

        elif current_tag == "main_menu":
            if user_message == "find_mentor":
                response = [
                    "Great! What area are you interested in?",
                    "We have mentors in various fields."
                ]
                options = [
                    {"text": "Academic", "value": "academic"},
                    {"text": "Career", "value": "career"},
                    {"text": "Personal Development", "value": "personal_development"}
                ]
                response_tag = "select_area"
            elif user_message == "learn_programs":
                response = [
                    "We offer a variety of mentorship programs tailored to your needs.",
                    "Please select an area to learn more."
                ]
                options = [
                    {"text": "Academic Programs", "value": "academic_programs"},
                    {"text": "Career Programs", "value": "career_programs"},
                    {"text": "Personal Development Programs", "value": "personal_programs"}
                ]
                response_tag = "program_info"
            elif user_message == "get_support":
                response = [
                    "I'm here to help with any technical issues.",
                    "Please describe the problem you're experiencing."
                ]
                response_tag = "technical_support"
            elif user_message == "provide_feedback":
                response = ["We appreciate your feedback! Please share your thoughts with us."]
                response_tag = "feedback"
            else:
                response = ["I'm sorry, I didn't understand that. Please choose one of the options."]
                options = [
                    {"text": "Find a Mentor", "value": "find_mentor"},
                    {"text": "Learn About Programs", "value": "learn_programs"},
                    {"text": "Get Technical Support", "value": "get_support"},
                    {"text": "Provide Feedback", "value": "provide_feedback"}
                ]
                response_tag = "main_menu"

        elif current_tag == "select_area":
            if user_message in ["academic", "career", "personal_development"]:
                response = [
                    f"Excellent choice! To help us find the best {user_message.replace('_', ' ')} mentor for you, we'll need some additional information.",
                    "Please briefly describe what you're looking for."
                ]
                response_tag = "collect_question"
                user_data["area_of_interest"] = user_message
            else:
                response = ["Please select a valid area of interest."]
                options = [
                    {"text": "Academic", "value": "academic"},
                    {"text": "Career", "value": "career"},
                    {"text": "Personal Development", "value": "personal_development"}
                ]
                response_tag = "select_area"

        elif current_tag == "collect_question":
            user_data["question"] = user_message
            response = ["Could you please provide your name?"]
            response_tag = "collect_name"

        elif current_tag == "collect_name":
            user_data["name"] = user_message.title()
            response = [f"Nice to meet you, {user_data['name']}!", "Could you please provide your email address?"]
            response_tag = "collect_email"

        elif current_tag == "collect_email":
            user_data["email"] = user_message
            response = ["Thank you! Lastly, could you provide your phone number?"]
            response_tag = "collect_phone"

        elif current_tag == "collect_phone":
            user_data["phone"] = user_message
            response = [
                "Thanks for providing your details.",
                f"We will reach out to you soon with the best {user_data['area_of_interest'].replace('_', ' ')} mentor matches.",
                "Is there anything else I can assist you with?"
            ]
            options = [
                {"text": "Yes", "value": "restart_chat"},
                {"text": "No", "value": "goodbye"}
            ]
            response_tag = "additional_help"

        elif current_tag == "program_info":
            if user_message in ["academic_programs", "career_programs", "personal_programs"]:
                area = user_message.replace("_programs", "").replace("_", " ")
                response = [
                    f"Our {area} programs are designed to help you excel.",
                    f"Learn more here: [{area.title()} Programs Page Link]",
                    "Would you like to speak with an advisor?"
                ]
                options = [
                    {"text": "Yes", "value": "advisor_collect_question"},
                    {"text": "No", "value": "end_conversation"}
                ]
                response_tag = "offer_advisor"
            else:
                response = ["Please select a valid program category."]
                options = [
                    {"text": "Academic Programs", "value": "academic_programs"},
                    {"text": "Career Programs", "value": "career_programs"},
                    {"text": "Personal Development Programs", "value": "personal_programs"}
                ]
                response_tag = "program_info"

        elif current_tag == "offer_advisor":
            if user_message == "advisor_collect_question":
                response = ["Please describe your question or the information you're seeking."]
                response_tag = "advisor_collect_question"
            else:
                response = ["No problem! Let me know if there's anything else I can assist you with."]
                response_tag = "end_conversation"

        elif current_tag == "advisor_collect_question":
            user_data["question"] = user_message
            response = ["Could you please provide your name?"]
            response_tag = "advisor_collect_name"

        elif current_tag == "advisor_collect_name":
            user_data["name"] = user_message.title()
            response = [f"Thank you, {user_data['name']}!", "May I have your email address?"]
            response_tag = "advisor_collect_email"

        elif current_tag == "advisor_collect_email":
            user_data["email"] = user_message
            response = ["And your phone number, please?"]
            response_tag = "advisor_collect_phone"

        elif current_tag == "advisor_collect_phone":
            user_data["phone"] = user_message
            response = [
                "Thank you for providing your details.",
                "An advisor will contact you shortly to assist with your inquiry.",
                "Is there anything else I can assist you with?"
            ]
            options = [
                {"text": "Yes", "value": "restart_chat"},
                {"text": "No", "value": "goodbye"}
            ]
            response_tag = "additional_help"

        elif current_tag == "technical_support":
            user_data["issue"] = user_message
            response = [
                "Thank you for reporting the issue.",
                "Our technical support team will get in touch with you shortly.",
                "Could you please provide your name, email, and phone number so we can assist you better?"
            ]
            response_tag = "support_collect_name"

        elif current_tag == "support_collect_name":
            user_data["name"] = user_message.title()
            response = ["Thank you! Now, could you provide your email address?"]
            response_tag = "support_collect_email"

        elif current_tag == "support_collect_email":
            user_data["email"] = user_message
            response = ["Lastly, may I have your phone number?"]
            response_tag = "support_collect_phone"

        elif current_tag == "support_collect_phone":
            user_data["phone"] = user_message
            response = [
                "We appreciate your patience.",
                "Our technical support team will reach out to you soon.",
                "Is there anything else I can assist you with?"
            ]
            options = [
                {"text": "Yes", "value": "restart_chat"},
                {"text": "No", "value": "goodbye"}
            ]
            response_tag = "additional_help"

        elif current_tag == "feedback":
            user_data["feedback"] = user_message
            response = [
                "Thank you for your valuable feedback!",
                "Could you please provide your name and email in case we need to follow up?"
            ]
            response_tag = "feedback_collect_name"

        elif current_tag == "feedback_collect_name":
            user_data["name"] = user_message.title()
            response = ["Thank you! Now, could you provide your email address?"]
            response_tag = "feedback_collect_email"

        elif current_tag == "feedback_collect_email":
            user_data["email"] = user_message
            response = [
                "We appreciate your input.",
                "Is there anything else I can assist you with?"
            ]
            options = [
                {"text": "Yes", "value": "restart_chat"},
                {"text": "No", "value": "goodbye"}
            ]
            response_tag = "additional_help"

        elif current_tag == "additional_help":
            if user_message == "restart_chat":
                response = [
                    "Sure! Let's start over.",
                    "How can I assist you today?"
                ]
                options = [
                    {"text": "Find a Mentor", "value": "find_mentor"},
                    {"text": "Learn About Programs", "value": "learn_programs"},
                    {"text": "Get Technical Support", "value": "get_support"},
                    {"text": "Provide Feedback", "value": "provide_feedback"}
                ]
                response_tag = "main_menu"
            else:
                response = ["Thank you for using AskToMentor. Have a great day!"]
                response_tag = "goodbye"

        elif current_tag == "goodbye":
            response = ["Goodbye! Feel free to chat with me anytime."]
            response_tag = "start_conversation"

        else:
            response = ["I'm sorry, I didn't understand that. Could you please rephrase?"]
            response_tag = current_tag

        return jsonify({"response": response, "tag": response_tag, "options": options, "user_data": user_data})

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
