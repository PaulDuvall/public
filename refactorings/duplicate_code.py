# Example of the 'Duplicate Code' code smell
# Martin Fowler Refactoring Catalog

def calculate_area_rectangle(width, height):
    # Duplicate logic for area calculation
    if width <= 0 or height <= 0:
        raise ValueError('Invalid dimensions')
    return width * height

def calculate_area_triangle(base, height):
    # Duplicate validation logic
    if base <= 0 or height <= 0:
        raise ValueError('Invalid dimensions')
    return 0.5 * base * height

# Usage example (for demonstration only):
if __name__ == "__main__":
    print(calculate_area_rectangle(5, 10))
    print(calculate_area_triangle(5, 10))
