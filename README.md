Project Title: Cloudflare API GUI Tool
Description
This tool is a graphical user interface (GUI) application built to interact with Cloudflare's API. It allows users to easily perform operations such as listing zones, managing DNS records, and accessing other Cloudflare services without the need for direct API calls through command-line tools.

Features
User-friendly interface for interacting with Cloudflare's API.
Preset endpoints for quick access to common API functions.
Secure API token storage using system keyring.
Response display and export capabilities.
Installation
Prerequisites
Python 3.x
pip (Python package manager)
Dependencies
Before running the application, install the required Python packages:

bash
Copy code
pip install requests keyring tkinter
Running the Application
To run the application, navigate to the application directory and execute:

bash
Copy code
python cloudflare_gui.py
Usage
API Token: Enter your Cloudflare API token.
Email: Enter your Cloudflare account email.
ID Type and ID: Select the ID type (Account ID or Zone ID) and enter the corresponding ID.
Endpoint Suffix: Select a preset endpoint or enter a custom endpoint suffix.
HTTP Method: Select the HTTP method for your API request.
Parameters (JSON): If required, enter the JSON parameters for your API request.
Click on Make API Call to send the request.
View the response in the response display section or export it as a JSON file.
Contributing
Contributions to the project are welcome! Please refer to the CONTRIBUTING.md for guidelines.
