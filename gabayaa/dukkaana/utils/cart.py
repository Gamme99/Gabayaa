from decimal import Decimal
from ..constants import TRANSACTION_FEE_PERCENTAGE


class CartSummary:
    def __init__(self, items):
        self.items = items
        self._calculate_totals()

    def _calculate_totals(self):
        """Calculate all cart totals"""
        self.subtotal = self._calculate_subtotal()
        self.transaction_fee = self._calculate_transaction_fee()
        self.total = self._calculate_total()
        self.item_count = self._calculate_item_count()

    def _calculate_subtotal(self):
        """Calculate the subtotal of all items"""
        if not self.items:
            return Decimal('0')

        if hasattr(self.items[0], 'unit_price'):  # CartItem objects
            return sum(item.unit_price * item.quantity for item in self.items)
        else:  # Dictionary items
            return sum(Decimal(str(item['price'])) * item['quantity'] for item in self.items)

    def _calculate_transaction_fee(self):
        """Calculate the transaction fee (3%)"""
        return self.subtotal * TRANSACTION_FEE_PERCENTAGE

    def _calculate_total(self):
        """Calculate the total including transaction fee"""
        return self.subtotal + self.transaction_fee

    def _calculate_item_count(self):
        """Calculate the total number of items"""
        if not self.items:
            return 0

        if hasattr(self.items[0], 'quantity'):  # CartItem objects
            return sum(item.quantity for item in self.items)
        else:  # Dictionary items
            return sum(item['quantity'] for item in self.items)

    def to_dict(self):
        """Convert summary to dictionary format"""
        return {
            'subtotal': round(self.subtotal, 2),
            'transaction_fee': round(self.transaction_fee, 2),
            'total': round(self.total, 2),
            'item_count': self.item_count
        }
