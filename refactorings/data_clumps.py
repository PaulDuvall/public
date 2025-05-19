# Example of the 'Data Clumps' code smell
# Martin Fowler Refactoring Catalog

def print_personal_info(first_name, last_name, phone, email):
    print(f"Name: {first_name} {last_name}")
    print(f"Phone: {phone}")
    print(f"Email: {email}")

def save_personal_info(first_name, last_name, phone, email):
    # Simulate saving info
    print(f"Saving: {first_name} {last_name}, {phone}, {email}")

# Usage example (for demonstration only):
if __name__ == "__main__":
    print_personal_info('Jane', 'Smith', '555-1234', 'jane@example.com')
    save_personal_info('Jane', 'Smith', '555-1234', 'jane@example.com')
