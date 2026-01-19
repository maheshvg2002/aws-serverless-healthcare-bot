import json
import boto3
import re
import uuid

# --- CONFIG ---
dynamodb = boto3.resource('dynamodb')
faq_table = dynamodb.Table('MentalHealthFAQ')           
appointments_table = dynamodb.Table('PatientAppointments') 

# NLP Stop Words (Noise to ignore)
STOP_WORDS = set(["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"])

def lambda_handler(event, context):
    try:
        intent_name = event['sessionState']['intent']['name']
        
        # 1. Booking Logic
        if intent_name == 'BookAppointment':
            return book_appointment(event)
        
        # 2. Smart Search Logic (GetSymptomInfo OR Fallback)
        elif intent_name == 'GetSymptomInfo' or intent_name == 'FallbackIntent':
            return perform_smart_search(event)
            
        else:
            return close_dialog("Sorry, I didn't understand that request.")
            
    except Exception as e:
        return close_dialog(f"SYSTEM ERROR: {str(e)}")

# --- REAL BOOKING LOGIC (Restored) ---
def book_appointment(event):
    try:
        slots = event['sessionState']['intent']['slots']
        
        # Safely extract values (handling potential missing slots)
        try:
            patient_name = slots['Name']['value']['originalValue']
            date = slots['Date']['value']['originalValue']
            time = slots['Time']['value']['originalValue']
            department = slots['Department']['value']['originalValue']
        except (KeyError, TypeError):
            return close_dialog("I missed some details. Please try booking again.")

        # Generate a unique Reference ID
        patient_id = "REF-" + str(uuid.uuid4())[:8].upper()
        
        # Save to DynamoDB
        appointments_table.put_item(
            Item={
                'PatientID': patient_id,
                'AppointmentDate': date,
                'PatientName': patient_name,
                'Time': time,
                'Department': department,
                'Status': 'Confirmed'
            }
        )
        
        return close_dialog(f"Appointment confirmed for {patient_name} on {date} at {time}. Ref: {patient_id}")
        
    except Exception as e:
        return close_dialog(f"BOOKING ERROR: {str(e)}")

# --- SMART SEARCH LOGIC (NLP) ---
def perform_smart_search(event):
    try:
        user_text = ""
        
        # Method A: Fallback Input
        if 'inputTranscript' in event:
            user_text = event['inputTranscript']
            
        # Method B: Slot Input
        elif 'sessionState' in event and 'slots' in event['sessionState']['intent']:
            slots = event['sessionState']['intent']['slots']
            if slots and 'Symptom' in slots and slots['Symptom']:
                user_text = slots['Symptom']['value']['originalValue']
        
        if not user_text:
            return close_dialog("I'm listening, but I didn't catch that.")

        user_tokens = clean_and_tokenize(user_text)
        
        response = faq_table.scan()
        items = response['Items']
        if not items: return close_dialog("My memory is empty.")

        best_score = 0
        best_answer = "I'm not sure about that."
        
        for item in items:
            db_question = item['Question']
            db_tokens = clean_and_tokenize(db_question)
            score = calculate_similarity(user_tokens, db_tokens)
            
            if score > best_score:
                best_score = score
                best_answer = item['Answer']

        if best_score < 0.2:
            return close_dialog("I don't have information on that topic in my mental health database.")
            
        return close_dialog(best_answer)

    except Exception as inner_e:
        return close_dialog(f"SEARCH ERROR: {str(inner_e)}")

def clean_and_tokenize(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text).lower()
    tokens = text.split()
    return {word for word in tokens if word not in STOP_WORDS}

def calculate_similarity(user_tokens, db_tokens):
    if not user_tokens or not db_tokens: return 0.0
    intersection = user_tokens.intersection(db_tokens)
    union = user_tokens.union(db_tokens)
    return len(intersection) / len(union)

def close_dialog(message):
    return {
        "sessionState": {
            "dialogAction": {"type": "Close"},
            "intent": {"name": "FallbackIntent", "state": "Fulfilled"}
        },
        "messages": [{"contentType": "PlainText", "content": message}]
    }