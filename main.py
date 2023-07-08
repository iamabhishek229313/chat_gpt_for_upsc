import os
import time
import json
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build

# OpenAI API configuration
openai_key = 'sk-...DCVH'
openai_endpoint = 'https://api.openai.com/v1/engines/davinci-codex/completions'

# Google Doc configuration
google_creds = './client_secret_362977113714-utmmon7unalo6u3stjni0hnr7an3rnba.apps.googleusercontent.com.json'
google_doc_id = '1-0o8PvYN7psEUE95UEuw4HfgFIBW-EHoj3kXVEveulE'

# Configure the Google Drive API client
credentials = service_account.Credentials.from_service_account_file(
    google_creds, scopes=['https://www.googleapis.com/auth/documents']
)
service = build('docs', 'v1', credentials=credentials)

# Function to interact with ChatGPT
def chat_with_gpt(prompt):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_key}'
    }
    data = {
        'prompt': prompt,
        'max_tokens': 100,
        'temperature': 0.7,
        'n': 1,
        'stop': None
    }
    response = requests.post(openai_endpoint, headers=headers, json=data)
    response_json = response.json()
    return response_json['choices'][0]['text'].strip()

# Function to save the response to Google Doc
def save_to_google_doc(subject, topic, content):
    doc = service.documents().get(documentId=google_doc_id).execute()
    title = doc['title']
    
    # Create the document body with subject and topic
    body = {
        'content': [
            {
                'paragraph': {
                    'elements': [
                        {
                            'textRun': {
                                'content': subject,
                                'bold': True,
                                'fontSize': {'magnitude': 16},
                                'alignment': 'CENTER'
                            }
                        }
                    ]
                }
            },
            {
                'paragraph': {
                    'elements': [
                        {
                            'textRun': {
                                'content': topic,
                                'bold': True,
                                'fontSize': {'magnitude': 14}
                            }
                        }
                    ]
                }
            },
            {
                'paragraph': {
                    'elements': [
                        {
                            'textRun': {
                                'content': content
                            }
                        }
                    ]
                }
            }
        ]
    }
    
    # Append the body to the document
    service.documents().batchUpdate(
        documentId=google_doc_id,
        body={'requests': [{'insertText': body['content'], 'endOfSegmentLocation': {'segmentId': ''}}]}
    ).execute()

# Main function to run the process
def run_process(topics, initial_question):
    subject = input('Enter the subject name: ')
    prompt = initial_question
    
    # Loop through the list of topics
    for topic in topics:
        prompt += f'\n\nQ. Explain the different aspects of {topic}.'
        
        # Retry for 3 times if no response received
        for _ in range(3):
            response = chat_with_gpt(prompt)
            if response:
                break
            time.sleep(1)
        else:
            print('No response received from ChatGPT.')
            return

        # Save response to Google Doc
        save_to_google_doc(subject, topic, response)
        print(f'Response for {topic} saved to Google Doc.')

# Run the process
if __name__ == '__main__':
    topics = ['topic1', 'topic2', 'topic3']  # List of topics
    initial_question = input('Enter the initial question (Q): ')
    run_process(topics, initial_question)
