from pydantic import Field, BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from models import TransactionType

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr 
    password: str = Field(..., min_length=8, max_length=100)

    @validator('email')
    def validate_email(cls, v):
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email address")
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if not len(v) >= 8:
            raise ValueError("Password must be 8 characters long!")
        return v

class UserLogin(BaseModel):
    account_number: str 
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str]= None

    @validator('email')
    def validate_email(cls, v):
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email address")
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if not len(v) >= 8:
            raise ValueError("Password must be 8 characters long!")
        return v
    
    class Config:
       from_attributes = True

class UserResponse(BaseModel):
    username: str
    email: EmailStr
    account_number: str

class DepositWithdraw(BaseModel):
    balance: float

    class Config:
        from_attributes = True

class Transaction(BaseModel):
    amount: float

    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v


class TransactionResponse(BaseModel):
    message: str
    balance: float

class TransactionHistoryItem(BaseModel):
    sender_id: Optional[str] = None
    receiver_id: Optional[str] = None
    amount: float
    transaction_type: TransactionType
    timestamp: datetime

    class Config:
        from_attributes = True

