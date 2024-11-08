from dotenv import load_dotenv
load_dotenv() 

import os
import time
import json
import hmac
import hashlib
import requests
from typing import Optional, Dict, Any
from random import randint
import string
import random
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TuyaClient:
    _client = None
    
    KEY_TU_YA_ACCESS_TOKEN = 'tuya:access_token'
    KEY_TU_YA_TOKEN_RES = 'tuya:token_res'
    
    def __init__(self):
        self.endpoint = os.getenv('API_ENDPOINT')
        self.access_id = os.getenv('ACCESS_ID')
        self.access_secret = os.getenv('ACCESS_KEY')
        self.cache = {}  # Simple in-memory cache implementation
        
    @classmethod
    def get_client(cls) -> 'TuyaClient':
        if cls._client is None:
            cls._client = cls()
            cls._client.initialize_token()
        return cls._client
    
    def initialize_token(self) -> None:
        if not self.cache.get(self.KEY_TU_YA_ACCESS_TOKEN):
            if self.KEY_TU_YA_TOKEN_RES in self.cache:
                refresh_token = self.cache[self.KEY_TU_YA_TOKEN_RES]['refresh_token']
                token_res = self.get_token(refresh_token)
                if not token_res.get('success'):
                    token_res = self.get_token()
            else:
                token_res = self.get_token()
                
            if token_res.get('success'):
                # In a real implementation, you might want to use proper cache expiration
                self.cache[self.KEY_TU_YA_ACCESS_TOKEN] = token_res['result']['access_token']
                self.cache[self.KEY_TU_YA_TOKEN_RES] = token_res['result']
    
    def send(self, method: str, url: str, options: Dict = None) -> Dict:
        if options is None:
            options = {}
            
        method = method.upper()
        url = self._replace_params_in_url(url, options.get('params', {}))
        url = self._append_query_to_url(url, options.get('query', {}))
        
        body = json.dumps(options.get('body', '')) if 'body' in options else ''
        
        logger.debug(f"Making request to: {url}")
        
        request_options = {
            'headers': self.get_headers(method, url, body)
        }
        
        if 'body' in options:
            request_options['json'] = options['body']
            
        try:
            response = requests.request(
                method,
                f"{self.endpoint}{url}",
                **request_options
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:  # Token expired
                logger.debug("Token expired, refreshing...")
                self.initialize_token()
                request_options['headers'] = self.get_headers(method, url, body)
                response = requests.request(
                    method,
                    f"{self.endpoint}{url}",
                    **request_options
                )
                return response.json()
            raise
    
    def _replace_params_in_url(self, url: str, params: Dict) -> str:
        for key, value in params.items():
            url = url.replace(f'{{{key}}}', str(value))
        return url
    
    def _append_query_to_url(self, url: str, query: Dict) -> str:
        if query:
            sorted_query = dict(sorted(query.items()))
            query_string = '&'.join(f"{k}={v}" for k, v in sorted_query.items())
            url = f"{url}?{query_string}"
        return url
    
    def get_token(self, refresh_token: str = '') -> Dict:
        url = f"/v1.0/token/{refresh_token}" if refresh_token else '/v1.0/token?grant_type=1'
        
        response = requests.get(
            f"{self.endpoint}{url}",
            headers=self.get_headers('GET', url)
        )
        return response.json()
    
    def get_headers(self, method: str, url: str, body: str = '', append_headers: Dict = None) -> Dict:
        if append_headers is None:
            append_headers = {}
            
        access_token = '' if url.startswith('/v1.0/token') else self.cache.get(self.KEY_TU_YA_ACCESS_TOKEN, '')
        
        if not access_token and not url.startswith('/v1.0/token'):
            self.initialize_token()
            access_token = self.cache.get(self.KEY_TU_YA_ACCESS_TOKEN)
            
            if not access_token:
                raise Exception("Access token is not available.")
        
        nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        timestamp = int(time.time() * 1000)
        
        headers = {
            'client_id': self.access_id,
            'sign_method': 'HMAC-SHA256',
            't': str(timestamp),
            'nonce': nonce,
            'sign': self._generate_signature(method, url, body, append_headers, access_token, nonce, timestamp)
        }
        
        headers.update(append_headers)
        
        if access_token:
            headers['access_token'] = access_token
            
        return headers
    
    def _generate_signature(self, method: str, url: str, body: str, append_headers: Dict, 
                          access_token: str, nonce: str, timestamp: int) -> str:
        headers_str = '\n'.join(f"{k}:{v}" for k, v in sorted(append_headers.items()))
        
        string_to_sign = f"{method}\n{hashlib.sha256(body.encode()).hexdigest()}\n{headers_str}\n{url}"
        
        sign_str = f"{self.access_id}{access_token}{timestamp}{nonce}{string_to_sign}"
        signature = hmac.new(
            self.access_secret.encode(),
            sign_str.encode(),
            hashlib.sha256
        ).hexdigest().upper()
        
        return signature 
    
    def get_device_info(self, device_id: str) -> Dict:
        """
        Get device information by device ID
        
        Args:
            device_id (str): The Tuya device ID
            
        Returns:
            Dict: Device information response from Tuya API
        """
        url = f'/v1.0/devices/{device_id}'
        return self.send('GET', url)
    
    def get_device_status(self, device_id: str) -> Dict:
        """
        Get device status by device ID
        
        Args:
            device_id (str): The Tuya device ID
            
        Returns:
            Dict: Device status response from Tuya API
        """
        url = f'/v1.0/devices/{device_id}/status'
        return self.send('GET', url)
    
    def control_device(self, device_id: str, commands: list) -> Dict:
        """
        Control device by sending commands
        
        Args:
            device_id (str): The Tuya device ID
            commands (list): List of commands to send to the device
                           Each command should be a dict with 'code' and 'value'
            
        Returns:
            Dict: Response from Tuya API
        """
        url = f'/v1.0/devices/{device_id}/commands'
        return self.send('POST', url, {
            'body': {
                'commands': commands
            }
        })