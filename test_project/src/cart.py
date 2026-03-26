from typing import List, Dict

def calculate_discount(price: float, discount: float) -> float:
    """Calculate the final price after applying a discount.

    Args:
        price (float): The original price of the item.
        discount (float): The discount percentage (0-100).

    Returns:
        float: The final price after the discount.

    Raises:
        ValueError: If the discount is outside the range 0-100.
    """
    if not (0 <= discount <= 100):
        raise ValueError("Discount must be between 0 and 100")
    return price * (1 - discount / 100)


class Cart:
    """A simple shopping cart that can add items and calculate the total price."""

    def __init__(self):
        """Initialize an empty cart."""
        self.items: List[Dict[str, float]] = []

    def add_item(self, item: str, price: float) -> None:
        """Add an item to the cart.

        Args:
            item (str): The name of the item.
            price (float): The price of the item.
        """
        self.items.append({'item': item, 'price': price})

    def total(self) -> float:
        """Calculate the total price of all items in the cart.

        Returns:
            float: The total price.
        """
        return sum(item['price'] for item in self.items)
