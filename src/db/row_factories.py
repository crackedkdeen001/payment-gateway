from abc import ABC, abstractmethod
from typing import Any
from collections.abc import Sequence

from psycopg import Cursor

from ..models import BankReference, Card, Receipt, IdempotencyKeys


class BaseRowFactory(ABC):
    def __init__(self, cursor: Cursor[Any]):
        if cursor.description is not None:
            self.fields = [c.name for c in cursor.description]
            
    @abstractmethod
    def make_row(self, values: Sequence[Any]):
        pass

    def __call__(self, values: Sequence[Any]) -> Any:
        return self.make_row(values)
        
            
class ReceiptRowFactory(BaseRowFactory):
    def make_row(self, values: Sequence[Any]):
        card_params = {}
        bank_ref_params = {}
        receipt_params = {}
        receipt_idx = {0, 1, 2, 3, 4, 9, 10}
        card_idx = {5, 6, 7, 8}
        bank_ref_idx = {11, 12, 13, 14, 15, 16, 17, 18}
        
        for i in range(len(self.fields)):
            column = self.fields[i]
            
            if i in receipt_idx:
                receipt_params[column] = values[i]
            elif i in card_idx:
                # truncate the "card" in the card column's name 
                card_column = column[5:]
                card_params[card_column] = values[i]
            elif i in bank_ref_idx:
                bank_ref_params[column] = values[i]
        
        receipt_params["card"] = Card(**card_params)
        receipt_params["bank_reference"] = BankReference(**bank_ref_params)
        
        return Receipt(**receipt_params)


class IdempotencyRowFactory(BaseRowFactory):
    def make_row(self, values: Sequence[Any]) -> IdempotencyKeys:
        idem_params = dict(zip(self.fields, values))
        return IdempotencyKeys(**idem_params)
         