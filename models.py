from database import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from datetime import datetime
from sqlalchemy.orm import relationship
import enum

class TransactionType(str, enum.Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER = "TRANSFER"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, unique=True, index= True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    balance = Column(Float, default=0.0)
    account_number = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    sent_transaction = relationship("Transaction", back_populates="sender", foreign_keys="Transaction.sender_id")
    receive_transaction = relationship("Transaction", back_populates="receiver", foreign_keys="Transaction.receiver_id")


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, unique=True, primary_key=True, index=True)
    sender_id = Column(String, ForeignKey("users.account_number"), nullable=True)
    receiver_id = Column(String, ForeignKey("users.account_number"), nullable=True)
    amount = Column(Float)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    sender = relationship("User", back_populates="sent_transaction", foreign_keys=[sender_id])
    receiver = relationship("User", back_populates="receive_transaction", foreign_keys=[receiver_id])

