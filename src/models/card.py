from models import BaseModel


class Card(BaseModel):
   number: str
   cvv: str
   expiry_month: int
   expiry_year: int
