# /path/to/CloudflareAPIGUI.py
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import json
import keyring
import threading
from tooltip import Tooltip #Import tooltip class
from CloudflareAPIHandler import CloudflareAPIHandler  # Import the new handler class
from dialog import CreateDNSRecordDialog

class CloudflareAPIGUI:
    # ... existing code ...

    def __init__(self, root):
        try:
            self.root = root
            self.initialize_fields() 
                # Load API prefix from config file
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)
                self.api_prefix = config.get('api_prefix', "https://api.cloudflare.com/client/v4")
            self.api_handler = CloudflareAPIHandler(self.api_prefix, self.email.get())
            root.title("Cloudflare API Interaction Tool")
            self.create_widgets()
            self.response_window = None
            self.loading = tk.BooleanVar(value=False)
            self.configure_ui()
            # Check if the API key is set in the keyring at startup
            api_key = keyring.get_password("CloudflareAPI", "api_key")
            if api_key and api_key.strip():  # Check if API key is not just empty spaces
                self.api_key_status_label.config(text="API Key Status: Set", fg="green")
            else:
                self.api_key_status_label.config(text="API Key Status: Not set", fg="red")
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize: {e}")
        

    def configure_ui(self):
        icon_path = "cloudflare.ico"
        self.root.iconbitmap(icon_path)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Helvetica', 10), padding=6)
        style.configure('TLabel', font=('Helvetica', 10), background='white', foreground='black')
        style.configure('TEntry', font=('Helvetica', 10), padding=6)
        style.configure('TCombobox', font=('Helvetica', 10), padding=6)
        self.root.option_add('*Font', ('Helvetica', 10))
        self.loading_label = tk.Label(self.root, text="Loading...", fg="blue")
        self.loading_label.grid(row=9, column=0, columnspan=3)
        self.loading_label.grid_remove()  # Hide it initially

    def update_loading_indicator(self):
        if self.loading.get():
            self.loading_label.grid()
        else:
            self.loading_label.grid_remove()

    def initialize_fields(self):
        # Initialize your variables here
        self.api_key = tk.StringVar()
        self.email = tk.StringVar()
        self.id_type = tk.StringVar(value="Account ID")
        self.http_method = tk.StringVar(value="GET")
        self.parameters = tk.StringVar()
        self.dns_record_identifier = tk.StringVar()
        self.id_value = tk.StringVar()
        self.endpoint_suffix = tk.StringVar()
        self.package_id_options = ["No", "Yes"]
        self.use_specific_package = tk.StringVar()
        self.specific_package_id = tk.StringVar()
        self.endpoint_mapping = {
        "List Zones": "/zones",
        "Zone Details": "/zones/:zone_identifier",
        "List DNS Records": "/zones/:zone_identifier/dns_records",
        "Create DNS Record": "/zones/:zone_identifier/dns_records",
        "Edit DNS Record": "/zones/:zone_identifier/dns_records/:identifier",
        "Delete DNS Record": "/zones/:zone_identifier/dns_records/:identifier",
        "Purge Cache": "/zones/:zone_identifier/purge_cache",
        "List Page Rules": "/zones/:zone_identifier/pagerules",
        "Create Page Rule": "/zones/:zone_identifier/pagerules",
        "Edit Page Rule": "/zones/:zone_identifier/pagerules/:identifier",
        "Delete Page Rule": "/zones/:zone_identifier/pagerules/:identifier",
        "Analytics Dashboard": "/zones/:zone_identifier/analytics/dashboard",
        "List Rate Limits": "/zones/:zone_identifier/rate_limits",
        "Create Rate Limit": "/zones/:zone_identifier/rate_limits",
        "Edit Rate Limit": "/zones/:zone_identifier/rate_limits/:identifier",
        "Delete Rate Limit": "/zones/:zone_identifier/rate_limits/:identifier",
        "List Firewall Rules": "/zones/:zone_identifier/firewall/rules",
        "Create Firewall Rule": "/zones/:zone_identifier/firewall/rules",
        "Edit Firewall Rule": "/zones/:zone_identifier/firewall/rules/:identifier",
        "Delete Firewall Rule": "/zones/:zone_identifier/firewall/rules/:identifier",
        "List Access Rules": "/zones/:zone_identifier/firewall/access_rules/rules",
        "Create Access Rule": "/zones/:zone_identifier/firewall/access_rules/rules",
        "Edit Access Rule": "/zones/:zone_identifier/firewall/access_rules/rules/:identifier",
        "Delete Access Rule": "/zones/:zone_identifier/firewall/access_rules/rules/:identifier",
        "List Workers Routes": "/zones/:zone_identifier/workers/routes",
        "Create Worker Route": "/zones/:zone_identifier/workers/routes",
        "Edit Worker Route": "/zones/:zone_identifier/workers/routes/:identifier",
        "Delete Worker Route": "/zones/:zone_identifier/workers/routes/:identifier",
        }

        # And when initializing the Combobox values:
        self.common_endpoints = list(self.endpoint_mapping.keys())


    def create_widgets(self):
        # Create and place UI elements here
        self.create_api_key_entry()
        self.create_email_entry()
        self.create_id_type_menu()
        self.create_http_method_menu()
        self.create_parameters_entry()
        self.create_id_entry()
        self.create_endpoint_entry()
        self.create_submit_button()
        self.create_dns_record_identifier_entry()
        self.hide_additional_fields()
        self.create_api_key_status_label()
        self.endpoint_suffix_combo.bind('<<ComboboxSelected>>', self.on_combobox_select)
        
        #self.create_response_display()

    def create_api_key_entry(self):
        tk.Label(self.root, text="API key:", padx=5, pady=5).grid(row=0, column=0, sticky=tk.W)
        self.api_key_entry = tk.Entry(self.root, textvariable=self.api_key, show="*", width=50)
        self.api_key_entry.bind("<FocusOut>", self.save_api_key)
        self.api_key_entry.grid(row=0, column=1, columnspan=2, sticky=tk.W + tk.E)
        # Add tooltip
        Tooltip(self.api_key_entry, "Enter your Cloudflare API key here.")

    
    def create_api_key_status_label(self):
        self.api_key_status_label = tk.Label(self.root, text="API Key Status: Not set", fg="red")
        self.api_key_status_label.grid(row=8, column=0, columnspan=3, sticky=tk.W)


    def create_email_entry(self):
        tk.Label(self.root, text="Email:", padx=5, pady=5).grid(row=1, column=0, sticky=tk.W)
        self.email_entry = tk.Entry(self.root, textvariable=self.email, width=50)
        self.email_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W + tk.E)

    def create_id_type_menu(self):
        tk.Label(self.root, text="ID Type:", padx=5, pady=5).grid(row=2, column=0, sticky=tk.W)
        id_types = ['Account ID', 'Zone ID']
        self.id_type_menu = ttk.Combobox(self.root, textvariable=self.id_type, values=id_types, state='readonly', width=47)
        self.id_type_menu.grid(row=2, column=1, columnspan=2, sticky=tk.W + tk.E)

    def create_http_method_menu(self):
        tk.Label(self.root, text="HTTP Method:", padx=5, pady=5).grid(row=3, column=0, sticky=tk.W)
        http_methods = ['GET', 'POST', 'PUT', 'DELETE']
        self.method_menu = ttk.Combobox(self.root, textvariable=self.http_method, values=http_methods, state='readonly', width=47)
        self.method_menu.grid(row=3, column=1, columnspan=2, sticky=tk.W + tk.E)

    def create_parameters_entry(self):
        tk.Label(self.root, text="Parameters (JSON):", padx=5, pady=5).grid(row=4, column=0, sticky=tk.W)
        self.parameters_entry = tk.Entry(self.root, textvariable=self.parameters, width=50)
        self.parameters_entry.grid(row=4, column=1, columnspan=2, sticky=tk.W + tk.E)

    def create_id_entry(self):
        tk.Label(self.root, text="ID:", padx=5, pady=5).grid(row=5, column=0, sticky=tk.W)
        self.id_entry = tk.Entry(self.root, textvariable=self.id_value, width=50)
        self.id_entry.grid(row=5, column=1, columnspan=2, sticky=tk.W + tk.E)

    def create_endpoint_entry(self):
        tk.Label(self.root, text="Endpoint Suffix:", padx=5, pady=5).grid(row=6, column=0, sticky=tk.W)
        self.endpoint_suffix_combo = ttk.Combobox(self.root, textvariable=self.endpoint_suffix, values=self.common_endpoints, state='readonly', width=47)
        self.endpoint_suffix_combo.grid(row=6, column=1, columnspan=2, sticky=tk.W + tk.E)
        self.endpoint_suffix_combo.current(0)  # Set the current value to the first item in the list

    def on_combobox_select(self, event):
        selected_endpoint = self.endpoint_suffix_combo.get()
        self.show_fields_for_endpoint(selected_endpoint)
    
        # Update HTTP method based on the selected endpoint
        if "Create" in selected_endpoint:
            self.http_method.set("POST")
        elif "Edit" in selected_endpoint or "Update" in selected_endpoint:
            self.http_method.set("PUT")
        elif "Delete" in selected_endpoint:
            self.http_method.set("DELETE")
        else:
            self.http_method.set("GET")  # Default to GET for listing and details endpoints
    
    # If the selected endpoint is to create a DNS record, open the dialog to enter details
        if selected_endpoint == "Create DNS Record":
            self.open_create_dns_record_dialog()
    
        self.method_menu.config(state='readonly')  # Optional: Make the method menu read-only if you don't want it to be changeable

    
    def create_dns_record_identifier_entry(self):
        self.dns_record_identifier_label = tk.Label(self.root, text="DNS Record ID:", padx=5, pady=5)
        self.dns_record_identifier_label.grid(row=10, column=0, sticky=tk.W, columnspan=2)
        self.dns_record_identifier_entry = tk.Entry(self.root, textvariable=self.dns_record_identifier, width=50)
        self.dns_record_identifier_entry.grid(row=10, column=1, columnspan=2, sticky=tk.W + tk.E)

    def open_create_dns_record_dialog(self):
        dialog = CreateDNSRecordDialog(self.root)
        self.root.wait_window(dialog.top)  # This waits until the dialog is closed
        # Now you can access dialog.result to get the data entered by the user
        if dialog.result:
            # Use dialog.result['type'], dialog.result['name'], etc. to make your API call
            self.parameters.set(json.dumps(dialog.result))  # You can set this to a StringVar linked to a hidden Entry if you wish


    def hide_additional_fields(self):
        self.dns_record_identifier_label.grid_remove()
        self.dns_record_identifier_entry.grid_remove()
        # Hide other fields similarly

    def show_fields_for_endpoint(self, endpoint):
        self.hide_additional_fields()
        if endpoint in ["Create DNS Record", "Edit DNS Record", "Delete DNS Record"]:
            self.dns_record_identifier_label.grid()
            self.dns_record_identifier_entry.grid()

    def create_submit_button(self):
        self.submit_button = tk.Button(self.root, text="Make API Call", command=self.make_api_call)
        self.submit_button.grid(row=7, column=1, sticky=tk.W + tk.E)

    def create_response_display(self):
        self.response_display = scrolledtext.ScrolledText(self.root, height=5, width=70)  # Adjusted height here
        self.response_display.grid(row=8, column=0, columnspan=3, sticky=tk.W + tk.E)

    def validate_inputs(self):
        # Example validation for email and TTL
        if not self.validate_email(self.email.get()):
            messagebox.showerror("Invalid Input", "Please enter a valid email address.")
            return False
        # Add additional validations as needed
        return True

    @staticmethod
    def validate_email(email):
        # Simple email validation logic
        return "@" in email  # Replace with a more robust validation
    
    def update_status(self, message, is_loading=False):
        # Implement logic to update a status bar or show a loading indicator
        pass


    def display_response_in_new_window(self, response_data):
        # Create a new top-level window
        new_window = tk.Toplevel(self.root)
        new_window.title("API Response")

        # Create a scrolled text widget in the new window
        response_text = scrolledtext.ScrolledText(new_window, wrap=tk.WORD)
        response_text.insert(tk.END, response_data)
        response_text.pack(fill=tk.BOTH, expand=True)


    def save_api_key(self, event=None):
        # Save the API key and update the status label
        if self.api_key.get().strip():  # Make sure the API key field is not empty
            keyring.set_password("CloudflareAPI", "api_key", self.api_key.get())
            self.api_key_status_label.config(text="API Key Status: Set", fg="green")
            messagebox.showinfo("Info", "API key saved securely.")
        else:
            messagebox.showerror("Error", "API key cannot be empty.")


    def make_api_call(self):
        print("API Call button clicked.")
        self.loading.set(True)
        self.update_loading_indicator()

        # Start the API call in a new thread
        api_call_thread = threading.Thread(target=self.threaded_api_call)
        api_call_thread.start()



    def threaded_api_call(self):
            # Gather input values
            api_key = self.api_key.get().strip()
            email = self.email.get().strip()
            http_method = self.http_method.get()
            id_value = self.id_value.get().strip()
            dns_record_id = self.dns_record_identifier.get().strip()

            # Validate inputs
            if not self.validate_inputs():
                self.loading.set(False)
                self.update_loading_indicator()
                return

            # Prepare the endpoint suffix from the selected endpoint
            friendly_endpoint = self.endpoint_suffix_combo.get()
            selected_endpoint = self.endpoint_mapping[friendly_endpoint]

            # Make the API call
            try:
                response_data = self.api_handler.make_api_call_sync(
                    http_method, selected_endpoint, email,
                    json.loads(self.parameters.get()) if self.parameters.get() else None,
                    zone_id=id_value, dns_record_id=dns_record_id
                )

                # Schedule the response to be displayed in the GUI
                self.root.after(0, self.display_response_in_new_window, json.dumps(response_data, indent=4))
            except Exception as e:
                self.root.after(0, messagebox.showerror, "API Call Failed", str(e))

            # Update loading state
            self.root.after(0, self.update_loading_state)

    def update_loading_state(self):
        self.loading.set(False)
        self.update_loading_indicator()

def main():
    root = tk.Tk()
    app = CloudflareAPIGUI(root)
    # We don't need to call run_forever here, it's being called inside the thread
    root.mainloop()

if __name__ == "__main__":
    main()
