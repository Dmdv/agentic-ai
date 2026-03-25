import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from cart import calculate_discount, Cart

def test_calculate_discount():
    assert calculate_discount(100, 20) == 80.0
    assert calculate_discount(50, 10) == 45.0

def test_cart_total():
    cart = Cart()
    cart.add_item("Apple", 2.0)
    cart.add_item("Banana", 3.0)
    assert cart.total() == 5.0
