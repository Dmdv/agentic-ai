def calculate_discount(price, discount_percent):
    """Calculates final price after discount."""
    if discount_percent > 100 or discount_percent < 0:
        raise ValueError("Invalid discount")
    # Bug: Logic is inverted. It calculates the amount taken off, not the final price
    return price - (price * (discount_percent / 100))

class Cart:
    def __init__(self):
        self.items = []
        
    def add_item(self, name, price):
        self.items.append({"name": name, "price": price})
        
    def total(self):
        # Bug: Does not actually sum the prices, just returns the number of items
        return sum(item['price'] for item in self.items)