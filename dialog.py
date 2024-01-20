import tkinter as tk

class CreateRecordDialog:
    def __init__(self, parent, record_type):
        self.top = tk.Toplevel(parent)
        self.record_type = record_type
        self.top.title(f"Create {self.record_type} Record")

        # Dictionary to hold different fields for different record types
        self.fields = {
            "DNS": {"type": "Type", "name": "Name", "content": "Content", "ttl": "TTL"},
            "PageRule": {"targets": "Targets", "actions": "Actions", "priority": "Priority"},
            "FirewallRule": {"filter": "Filter", "action": "Action"}
        }

        # Use the fields specific to the record type
        self.record_fields = self.fields[self.record_type]

        self.entries = {}
        self.create_fields()

        self.submit_button = tk.Button(self.top, text="Submit", command=self.submit)
        self.submit_button.grid(row=len(self.record_fields), columnspan=2)

        self.result = {}

    def create_fields(self):
        for i, (var_name, label_text) in enumerate(self.record_fields.items()):
            tk.Label(self.top, text=f"{label_text}:").grid(row=i, column=0)
            entry = tk.Entry(self.top)
            entry.grid(row=i, column=1)
            self.entries[var_name] = entry

    def submit(self):
        for var_name in self.record_fields:
            self.result[var_name] = self.entries[var_name].get()

        # Perform specific validation based on record type if needed
        if self.record_type == "DNS" and not self.result.get('type'):
            tk.messagebox.showwarning("Validation Error", "Type is required for DNS record.")
            return

        self.top.destroy()
