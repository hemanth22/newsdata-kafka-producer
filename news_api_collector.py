from kafka import KafkaProducer
import six
import sys
if sys.version_info >= (3, 12, 0):
    sys.modules['kafka.vendor.six.moves'] = six.moves
import requests
import os
import json

requesturl = os.environ.get('KAFKA_RECEIVER_SERVERLESS')

# Kafka configuration
bootstrap_servers_sv1 = os.environ.get('BOOTSTRAP_SERVER_NAME')
sasl_mechanism_sv1 = os.environ.get('SASL_MECH')
security_protocol_sv1 = os.environ.get('SSL_SEC')
sasl_plain_username_sv1 = os.environ.get('SASL_USERNAME')
sasl_plain_password_sv1 = os.environ.get('SASL_PASSD')

producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers_sv1,
    sasl_mechanism=sasl_mechanism_sv1,
    security_protocol=security_protocol_sv1,
    sasl_plain_username=sasl_plain_username_sv1,
    sasl_plain_password=sasl_plain_password_sv1,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

topic_name = 'news'

# Function to serialize data to JSON string
def serialize_data(data):
    """
    Serialize the given data to a JSON string.

    Args:
        data (dict): The data to serialize

    Returns:
        str: The serialized JSON string
    """
    return json.dumps(data)

def send_dataToFastAPI(url):
    response = requests.get(url)
    if response.status_code == 200:
        print("Request sent successfully")

    if response.status_code != 200:
        print(f"Failed to send data. Status code: {response.status_code}")

NEWSS_API_KEY = os.environ.get('GNEWS_API_KEY')
BASE_URL = 'https://gnews.io/api/v4/top-headlines'
queries = ['in','us','sg']

for query in queries:
    parameters = {
        'country': 'queries',
        'lang': 'en',         # Adjust if needed
        'max': 10,             # Limit to 3 articles per country for brevity
        'apikey': NEWSS_API_KEY
    }

try:
    response = requests.get(BASE_URL, params=parameters)
    if response.status_code == 200:
         news_data = response.json()
         for value in news_data["articles"]:
             formatted_json = {
                 "source": "news",
                 "message": {
                     "title": value.get('title','no news'),
                     "description": value.get('description','no news'),
                     "pubDate": value.get('publishedAt','no news'),
                     "source_id": value.get('url', 'unknown')
                 }
             }
             fomratted_output = json.dumps(formatted_json, ensure_ascii=False, indent=4)
             print(fomratted_output)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
except Exception as e:
    print(f"An error occurred: {str(e)}")


# Ensure all messages are sent before closing
producer.flush()
producer.close()
print("Notifying to Kafka Receiver")
send_dataToFastAPI(requesturl)
print("Producer Job Completed")