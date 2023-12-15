import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import requests
import os
import keyring
import json


class CloudflareAPIGUI:
    def __init__(self, root):
        self.root = root
        root.title("Cloudflare API Interaction Tool")
        root.iconbitmap('cloudflare.ico')  # Set the window icon (favicon)

        # Define the style
        style = ttk.Style()
        style.theme_use('clam')  # Use a theme that's a good starting point

        # Configure the style for ttk widgets
        style.configure('TButton', font=('Helvetica', 10), padding=6)
        style.configure('TLabel', font=('Helvetica', 10), background='white', foreground='black')
        style.configure('TEntry', font=('Helvetica', 10), padding=6)
        style.configure('TCombobox', font=('Helvetica', 10), padding=6)

        self.padding = {'padx': 5, 'pady': 5}  # Padding configuration

        # Cloudflare API configuration
        self.api_prefix = 'https://api.cloudflare.com/client/v4'
        stored_api_token = keyring.get_password("CloudflareAPI", "api_token")
        self.api_token = tk.StringVar(value=stored_api_token if stored_api_token else os.environ.get('CLOUDFLARE_API_TOKEN', ''))
        self.email = tk.StringVar()
        self.id_value = tk.StringVar()
        self.endpoint_suffix = tk.StringVar()
        self.http_method = tk.StringVar(value="GET")
        self.parameters = tk.StringVar()

        # Preset endpoints
        self.preset_endpoints = {
            "List Zones": "/zones",
            "Zone Details": "/zones/{zone_identifier}",
            "List DNS Records": "/zones/{zone_identifier}/dns_records",
            "Create DNS Record": "/zones/{zone_identifier}/dns_records",
            "Zone Analytics": "/zones/{zone_identifier}/analytics/dashboard",
            "Purge Cache": "/zones/{zone_identifier}/purge_cache",
            "List Firewall Rules": "/zones/{zone_identifier}/firewall/rules",
            "List Page Rules": "/zones/{zone_identifier}/pagerules",
            "List Workers Scripts": "/accounts/{account_identifier}/workers/scripts",
        }
        self.selected_preset_endpoint = tk.StringVar()

        # API Token Entry
        tk.Label(root, text="API Token:", **self.padding).grid(row=0, column=0, sticky=tk.W)
        tk.Entry(root, textvariable=self.api_token, show="*", width=50).grid(row=0, column=1, columnspan=2, sticky=tk.W+tk.E)

        # Email Entry
        tk.Label(root, text="Email:", **self.padding).grid(row=1, column=0, sticky=tk.W)
        tk.Entry(root, textvariable=self.email, width=50).grid(row=1, column=1, columnspan=2, sticky=tk.W+tk.E)

        self.id_type = tk.StringVar(value="Account ID")  # Initialize the id_type variable
        id_types = ['Account ID', 'Zone ID']

        # ID Type and ID Entry
        tk.Label(root, text="ID Type:", **self.padding).grid(row=2, column=0, sticky=tk.W)
        ttk.Combobox(root, textvariable=self.id_type, values=['Account ID', 'Zone ID'], state='readonly', width=47).grid(row=2, column=1, columnspan=2, sticky=tk.W+tk.E)
        tk.Label(root, text="ID:", **self.padding).grid(row=3, column=0, sticky=tk.W)
        tk.Entry(root, textvariable=self.id_value, width=50).grid(row=3, column=1, columnspan=2, sticky=tk.W+tk.E)

        # Endpoint Suffix Entry
        tk.Label(root, text="Endpoint Suffix:", **self.padding).grid(row=4, column=0, sticky=tk.W)
        tk.Entry(root, textvariable=self.endpoint_suffix, width=50).grid(row=4, column=1, columnspan=2, sticky=tk.W+tk.E)

        # HTTP Method Selection
        tk.Label(root, text="HTTP Method:", **self.padding).grid(row=5, column=0, sticky=tk.W)
        ttk.Combobox(root, textvariable=self.http_method, values=['GET', 'POST', 'PUT', 'DELETE'], state='readonly', width=47).grid(row=5, column=1, columnspan=2, sticky=tk.W+tk.E)

        # Preset Endpoints Dropdown
        tk.Label(root, text="Preset Endpoints:", **self.padding).grid(row=6, column=0, sticky=tk.W)
        preset_endpoint_menu = ttk.Combobox(root, textvariable=self.selected_preset_endpoint, values=list(self.preset_endpoints.keys()), state='readonly', width=47)
        preset_endpoint_menu.grid(row=6, column=1, columnspan=2, sticky=tk.W+tk.E)
        preset_endpoint_menu.bind('<<ComboboxSelected>>', self.update_endpoint_suffix)

        # Parameters Entry (JSON)
        tk.Label(root, text="Parameters (JSON):", **self.padding).grid(row=7, column=0, sticky=tk.NW)
        tk.Entry(root, textvariable=self.parameters, width=50).grid(row=7, column=1, columnspan=2, sticky=tk.W+tk.E)

        # Make API Call Button
        tk.Button(root, text="Make API Call", command=self.make_api_call).grid(row=8, column=1, sticky=tk.W+tk.E)

        # Response Display
        self.response_display = scrolledtext.ScrolledText(root, height=10, width=70)
        self.response_display.grid(row=9, column=0, columnspan=3, sticky=tk.W+tk.E)

        # Keep track of the next available row in the grid
        self.next_row = 8  # Assuming 7 rows are already used before the dynamic fields

        # Initialize package_id_entry but do not place it yet
        self.package_id_entry = tk.Entry(root, width=50)


        self.use_specific_package = tk.StringVar()

        self.package_id_options = ["No", "Yes"]  # Options for whether to use a specific package ID

        self.specific_package_id = tk.StringVar()  # The specific package ID if "Yes" is selected

        # Initialize package_id_menu and specific_package_id_entry but do not place them yet
        self.package_id_menu = ttk.Combobox(root, textvariable=self.use_specific_package, values=self.package_id_options, state='readonly', width=47)
        self.specific_package_id_entry = tk.Entry(root, textvariable=self.specific_package_id, width=50)

    
    def update_endpoint_suffix(self, event=None):
        """Update the endpoint suffix based on the preset selection."""
        selected_key = self.selected_preset_endpoint.get()  # Get the selected key from the dropdown
        if selected_key in self.preset_endpoints:
            # Get the endpoint template from the preset dictionary
            endpoint_template = self.preset_endpoints[selected_key]

            # Check if the template contains a placeholder for zone_identifier
            if '{zone_identifier}' in endpoint_template:
                # Ensure id_value is not empty and does not already contain '/zones/'
                zone_identifier = self.id_value.get().replace('/zones/', '').strip()
                # Format the template with the actual zone identifier
                filled_endpoint = endpoint_template.format(zone_identifier=zone_identifier)
                self.endpoint_suffix.set(filled_endpoint)
            else:
                self.endpoint_suffix.set(endpoint_template)
        else:
        # Handle the case where the selected key is not found in the presets
            messagebox.showerror("Error", "Selected preset endpoint is not valid.")




    def save_api_token(self, event=None):
        """Save the API token to the system's keyring."""
        keyring.set_password("CloudflareAPI", "api_token", self.api_token.get())
        messagebox.showinfo("Info", "API token saved securely.")

    def add_package_id_field(self):
        # Only ] the fields if they have not been added yet
        if not self.package_id_label:
            self.package_id_label = tk.Label(self.root, text="Use Specific Package ID:", **self.padding)
            self.package_id_label.grid(row=7, column=0, sticky=tk.W)
            self.package_id_menu.grid(row=7, column=1, columnspan=2, sticky=tk.W+tk.E)
            self.package_id_menu.bind('<<ComboboxSelected>>', self.toggle_specific_package_id_entry)
            self.next_row = 9  # Increment the next row count

    def remove_package_id_field(self):
        # Check if the fields have been added and remove them
        if self.package_id_label:
            self.package_id_label.grid_remove()
            self.package_id_label = None
        if self.package_id_menu:
            self.package_id_menu.grid_remove()
        if self.specific_package_id_entry:
            self.specific_package_id_entry.grid_remove()
            self.specific_package_id_entry = None
        self.next_row = 8  # Reset the next row count

    def toggle_specific_package_id_entry(self, event=None):
        if self.use_specific_package.get() == "Yes":
            if not self.specific_package_id_entry:
                self.specific_package_id_entry = tk.Entry(self.root, textvariable=self.specific_package_id, width=50)
            self.specific_package_id_entry.grid(row=8, column=1, columnspan=2, sticky=tk.W+tk.E)
            self.submit_button.grid(row=9, column=1, sticky=tk.W+tk.E)
            self.response_display.grid(row=10, column=0, columnspan=3, sticky=tk.W+tk.E)
        else:
            if self.specific_package_id_entry and self.specific_package_id_entry.winfo_ismapped():
                self.specific_package_id_entry.grid_remove()
                self.submit_button.grid(row=8, column=1, sticky=tk.W+tk.E)
                self.response_display.grid(row=9, column=0, columnspan=3, sticky=tk.W+tk.E)


    def make_api_call(self):
        api_token = self.api_token.get()
        email = self.email.get()
        http_method = self.http_method.get()
        parameters = self.parameters.get()
        id_type = self.id_type.get()
        id_value = self.id_value.get().strip()
        endpoint_suffix = self.endpoint_suffix.get().strip('/')

        if not all([api_token, email, id_value, endpoint_suffix]):
            messagebox.showerror("Error", "API Token, Email, ID, and Endpoint Suffix are required")
            return

        if http_method == 'DELETE':
            confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to perform the DELETE operation?")
            if not confirm:
                return

        # Construct the endpoint
        if 'zone_identifier' in endpoint_suffix:
            endpoint = f"{self.api_prefix}/zones/{id_value}/{endpoint_suffix.replace('{zone_identifier}', '')}"
        elif 'account_identifier' in endpoint_suffix:
            endpoint = f"{self.api_prefix}/accounts/{id_value}/{endpoint_suffix.replace('{account_identifier}', '')}"
        else:
            endpoint = f"{self.api_prefix}/{endpoint_suffix}"

        headers = {
            'X-Auth-Email': email,
            'X-Auth-Key': api_token,
            'Content-Type': 'application/json'
        }

        try:
            if parameters:
                parameters = json.loads(parameters)
            response = requests.request(http_method, endpoint, headers=headers, json=parameters)
            response_data = response.json()
            self.display_response(json.dumps(response_data, indent=4))
            self.export_to_file(endpoint_suffix, response_data)
        except json.JSONDecodeError:
            messagebox.showerror("Invalid JSON", "Parameters must be valid JSON")
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def export_to_file(self, endpoint_suffix, data):
        # Sanitize the endpoint_suffix to create a valid filename
        filename_suffix = endpoint_suffix.strip("/").replace("/", "_")
        filename = f"api_response_{filename_suffix}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Success", f"Response has been saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write to file: {e}")

    def display_response(self, response_text):
        self.response_display.delete('1.0', tk.END)
        self.response_display.insert(tk.END, response_text)

def main():
    root = tk.Tk()
    root.geometry('600x400')

    # Path to the icon image file (make sure to use an absolute path or ensure the file is in the current directory)
    root.iconbitmap('cloudflare.ico')

    app = CloudflareAPIGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()