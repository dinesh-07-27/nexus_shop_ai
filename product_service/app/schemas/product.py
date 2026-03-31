from pydantic import BaseModel, ConfigDict
from typing import Optional

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category: str

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    ai_summary: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ReviewCreate(BaseModel):
    user_id: int
    rating: int
    text: str

class ReviewResponse(ReviewCreate):
    id: int
    product_id: int

    model_config = ConfigDict(from_attributes=True)
