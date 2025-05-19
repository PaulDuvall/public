# Example of the 'Feature Envy' code smell
# Martin Fowler Refactoring Catalog

class Address:
    def __init__(self, street, city, zip_code):
        self.street = street
        self.city = city
        self.zip_code = zip_code

class Customer:
    def __init__(self, name, address):
        self.name = name
        self.address = address

    def display_full_address(self):
        # This method is more interested in Address fields than Customer fields
        addr = self.address
        return f"{addr.street}, {addr.city}, {addr.zip_code}"

# Usage example (for demonstration only):
if __name__ == "__main__":
    addr = Address('123 Main St', 'Springfield', '12345')
    cust = Customer('John Doe', addr)
    print(cust.display_full_address())
