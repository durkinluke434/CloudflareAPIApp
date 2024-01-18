import tkinter as tk

class CreateDNSRecordDialog:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Create DNS Record")

        # Define fields
        self.fields = {
            "type": "Type",
            "name": "Name",
            "content": "Content",
            "ttl": "TTL"
        }
        
        # Dictionary to hold the entry widgets
        self.entries = {}

        # Create fields
        self.create_fields()

        # Add submit button
        self.submit_button = tk.Button(self.top, text="Submit", command=self.submit)
        self.submit_button.grid(row=len(self.fields), columnspan=2)

        # Dictionary to hold the results
        self.result = {}

    def create_fields(self):
        for i, (var_name, label_text) in enumerate(self.fields.items()):
            # Create label
            tk.Label(self.top, text=f"{label_text}:").grid(row=i, column=0)

            # Create entry and store it in the entries dictionary
            entry = tk.Entry(self.top)
            entry.grid(row=i, column=1)
            self.entries[var_name] = entry

    def submit(self):
        for var_name in self.fields:
            # You can add specific validation for each field here if needed
            self.result[var_name] = self.entries[var_name].get()

        # Example: Validate the TTL field
        try:
            self.result['ttl'] = int(self.result['ttl'])
        except ValueError:
            tk.messagebox.showwarning("Validation Error", "TTL must be an integer.")
            return

        # Close the dialog
        self.top.destroy()

