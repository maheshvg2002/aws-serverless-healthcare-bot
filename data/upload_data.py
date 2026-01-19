import pandas as pd
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

# 2. Get the keys securely
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
region = os.getenv("REGION_NAME")

# 3. Connect to DynamoDB using the variables
dynamodb = boto3.resource(
    'dynamodb',
    region_name=region,
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)
table = dynamodb.Table('MentalHealthFAQ')

# 2. LOAD DATASET
try:
    df = pd.read_csv('Mental_Health_FAQ.csv')
    # Filter only necessary columns to avoid errors
    df = df[['Question_ID', 'Questions', 'Answers']]
except FileNotFoundError:
    print("Error: Could not find Mental_Health_FAQ.csv in this folder.")
    exit()

print("Starting upload...")

# 3. UPLOAD TO DYNAMODB
for index, row in df.iterrows():
    try:
        item = {
            'QuestionID': int(row['Question_ID']),
            'Question': str(row['Questions']),
            'Answer': str(row['Answers'])
        }
        table.put_item(Item=item)
        if index % 10 == 0: print(f"Uploaded {index} questions...")
            
    except Exception as e:
        print(f"Error on row {index}: {e}")

print("Upload Complete! The database is ready.")