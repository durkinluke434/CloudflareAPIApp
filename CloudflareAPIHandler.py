# /path/to/CloudflareAPIHandler.py
import requests
import json
from tkinter import messagebox
import logging
import keyring
import urllib.parse


logging.basicConfig(filename='cloudflare_api_errors.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class CloudflareAPIHandler:
    def __init__(self, api_prefix, email):
        self.api_prefix = api_prefix.strip()
        self.email = email.strip()
        self.retrieve_api_key()

    def retrieve_api_key(self):
        # Retrieve API key from keyring
        api_key = keyring.get_password("CloudflareAPI", "api_key")
        if api_key:
            self.api_key = api_key.strip()
        else:
            # Set self.api_key to None and handle this situation in other methods
            self.api_key = None



    def make_api_call_sync(self, http_method, endpoint_suffix, email, parameters=None, zone_id=None, dns_record_id=None):
            # Check if API key is set
        if self.api_key is None:
            # Handle the situation where the API key is not set
            logging.error("API key not set. Please set the API key.")
            messagebox.showerror("Error", "API key not set. Please enter the API key.")
            return  # Exit the method as the API key is required for further processing

        headers = {
            'X-Auth-Email': email,
            'X-Auth-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        endpoint = self.format_endpoint(endpoint_suffix, zone_id, dns_record_id)
        print(f"Making API call with headers: {headers}")
        print(f"Email being used for API call: {email}")
        print(f"Endpoint being called: {endpoint}")
        response = requests.request(http_method, endpoint, headers=headers, json=parameters)
        
        # Check for a successful request
        if response.ok:
            return response.json()
        else:
            # Log and raise an exception for any unsuccessful requests
            error_message = f"HTTP Error {response.status_code}: {response.text}"
            logging.error(error_message)
            messagebox.showerror("Error", error_message)
            response.raise_for_status()
        


    def format_endpoint(self, endpoint_suffix, zone_id=None, dns_record_id=None):
        # Replace placeholders with actual values
        if zone_id:
            endpoint_suffix = endpoint_suffix.replace(':zone_identifier', zone_id)
        if dns_record_id:
            endpoint_suffix = endpoint_suffix.replace(':identifier', dns_record_id)

        # URL encode the endpoint to ensure spaces and other special characters are properly encoded
        endpoint_suffix = urllib.parse.quote(endpoint_suffix)

        # Construct the full URL
        full_url = f"{self.api_prefix.rstrip('/')}/{endpoint_suffix.lstrip('/')}"

        return full_url


    def export_to_file(self, endpoint_suffix, data):
        filename_suffix = endpoint_suffix.strip("/").replace("/", "_")
        filename = f"api_response_{filename_suffix}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Success", f"Response has been saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write to file: {e}")
