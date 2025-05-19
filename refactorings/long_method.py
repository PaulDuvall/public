# Example of the 'Long Method' code smell
# Martin Fowler Refactoring Catalog

def process_customer_order(order):
    # This method does too much: validation, calculation, and notification
    if not order.get('customer_id'):
        raise ValueError('Missing customer ID')
    if not order.get('items'):
        raise ValueError('No items in order')
    for item in order['items']:
        if item['quantity'] <= 0:
            raise ValueError(f"Invalid quantity for item {item['id']}")
    subtotal = 0
    for item in order['items']:
        subtotal += item['price'] * item['quantity']
    tax = subtotal * 0.07
    total = subtotal + tax
    print(f"Subtotal: ${subtotal:.2f}")
    print(f"Tax: ${tax:.2f}")
    print(f"Total: ${total:.2f}")
    if total > 1000:
        print("High value order! Notifying sales team...")
    print(f"Order for customer {order['customer_id']} processed successfully.")

# Usage example (for demonstration only):
if __name__ == "__main__":
    order = {
        'customer_id': 123,
        'items': [
            {'id': 'A', 'price': 100, 'quantity': 5},
            {'id': 'B', 'price': 50, 'quantity': 10}
        ]
    }
    process_customer_order(order)
