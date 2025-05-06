import requests
import json
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from requests.exceptions import RequestException
from urllib.parse import urljoin

class FlaskAPIClient:
    def __init__(self):
        self.base_url = getattr(settings, "FLASK_API_BASE_URL", "http://localhost:5000/api")
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Add API key if configured
        api_key = getattr(settings, "FLASK_API_KEY", None)
        if api_key:
            self.headers['X-API-KEY'] = api_key

    def _make_request(self, method, endpoint, data=None, params=None):
        """Handle API requests with proper error handling"""
        url = urljoin(f"{self.base_url}/", endpoint.lstrip('/'))
        
        try:
            kwargs = {
                'headers': self.headers,
                'params': params,
                'timeout': 10
            }
            
            if data:
                kwargs['data'] = json.dumps(data, cls=DjangoJSONEncoder)
            
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            
            return response.json() if response.status_code != 204 else True
            
        except RequestException as e:
            print(f"API Error: {str(e)}")
            if hasattr(e, 'response') and e.response:
                try:
                    error_data = e.response.json()
                    print(f"Error details: {error_data}")
                except json.JSONDecodeError:
                    print(f"Response text: {e.response.text}")
            return None

    # CRUD operations
    def create_item(self, endpoint, data):
        return self._make_request('POST', endpoint, data)
    
    def get_items(self, endpoint, params=None):
        try:
            result = self._make_request('GET', endpoint, params=params)
            print(f"API Client get_items('{endpoint}') result:", result)
            return result
        except Exception as e:
            print(f"Error in get_items('{endpoint}'): {e}")
            return None
    
    def get_item(self, endpoint, item_id):
        return self._make_request('GET', f"{endpoint}/{item_id}")
    
    def update_item(self, endpoint, item_id, data):
        return self._make_request('PUT', f"{endpoint}/{item_id}", data)
    
    def delete_item(self, endpoint, item_id):
        return self._make_request('DELETE', f"{endpoint}/{item_id}")