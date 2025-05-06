import requests
from django.conf import settings

FLASK_API_BASE_URL = 'http://127.0.0.1:5000'  # Update this with your Flask server URL

class FlaskAPIService:
    @staticmethod
    def get_transactions():
        response = requests.get(f'{FLASK_API_BASE_URL}/transactions')
        return response.json() if response.status_code == 200 else None

    @staticmethod
    def get_transaction(transaction_id):
        response = requests.get(f'{FLASK_API_BASE_URL}/transactions/{transaction_id}')
        return response.json() if response.status_code == 200 else None

    @staticmethod
    def create_transaction(data):
        response = requests.post(f'{FLASK_API_BASE_URL}/transactions', json=data)
        return response.json() if response.status_code == 201 else None

    @staticmethod
    def update_transaction(transaction_id, data):
        response = requests.put(f'{FLASK_API_BASE_URL}/transactions/{transaction_id}', json=data)
        return response.json() if response.status_code == 200 else None

    @staticmethod
    def delete_transaction(transaction_id):
        response = requests.delete(f'{FLASK_API_BASE_URL}/transactions/{transaction_id}')
        return response.status_code == 204

    @staticmethod
    def login(username, password):
        response = requests.post(f'{FLASK_API_BASE_URL}/login', json={
            'username': username,
            'password': password
        })
        return response.json() if response.status_code == 200 else None

    @staticmethod
    def signup(user_data):
        response = requests.post(f'{FLASK_API_BASE_URL}/signup', json=user_data)
        return response.json() if response.status_code == 201 else None 