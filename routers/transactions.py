from fastapi import APIRouter, Depends, HTTPException
import schemas
from sqlalchemy.orm import Session
import models
from database import get_db
from typing import List
import logging

router = APIRouter(prefix="/trans", tags=["Transactions"])
logger = logging.getLogger(__name__)


@router.get('/balance/{account_number_value}/', status_code=200)
def get_balance(account_number_value: str, db: Session = Depends(get_db)):
    '''To identify the balance of the user!'''
    logger.info(f"Balance check for account='{account_number_value}'")
    try:
        user = db.query(models.User).filter(models.User.account_number == account_number_value).first()
        if not user:
            logger.warning(f"Balance check failed: account='{account_number_value}' not found")
            raise HTTPException(status_code=404, detail="Account not found!")
        logger.info(f"Balance retrieved for account='{account_number_value}': {user.balance}")
        return user.balance
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching balance for {account_number_value}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching balance")


@router.post('/deposit/{account_number_value}/', status_code=200)
def deposit_money(account_number_value: str, user: schemas.DepositWithdraw, db: Session = Depends(get_db)):
    '''To deposit money into their account!'''
    logger.info(f"Deposit attempt for account='{account_number_value}', amount={user.balance}")
    try:
        user_obj = db.query(models.User).filter(models.User.account_number == account_number_value).first()
        if not user_obj:
            logger.warning(f"Deposit failed: account='{account_number_value}' not found")
            raise HTTPException(status_code=400, detail="User not found")
        if user.balance <= 0:
            logger.warning(f"Deposit failed: invalid amount {user.balance} for account='{account_number_value}'")
            raise HTTPException(status_code=400, detail="Deposit amount must be greater than 0")
        user_obj.balance += user.balance
        transaction = models.Transaction(
            sender_id=user_obj.account_number,
            receiver_id=user_obj.account_number,
            amount=user.balance,
            transaction_type=models.TransactionType.DEPOSIT
        )
        db.add(transaction)
        db.commit()
        db.refresh(user_obj)
        db.refresh(transaction)
        logger.info(f"Deposit successful for account='{account_number_value}', new balance={user_obj.balance}")
        return {"message": "Money deposited!", "balance": user_obj.balance}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error depositing money for {account_number_value}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred during deposit")


@router.post('/withdraw/{account_number_value}/', status_code=200)
def withdraw_money(account_number_value: str, user: schemas.DepositWithdraw, db: Session = Depends(get_db)):
    '''To withdraw money from their account!'''
    logger.info(f"Withdrawal attempt for account='{account_number_value}', amount={user.balance}")
    try:
        user_obj = db.query(models.User).filter(models.User.account_number == account_number_value).first()
        if not user_obj:
            logger.warning(f"Withdrawal failed: account='{account_number_value}' not found")
            raise HTTPException(status_code=400, detail="User not found")
        if user.balance <= 0:
            logger.warning(f"Withdrawal failed: invalid amount {user.balance} for account='{account_number_value}'")
            raise HTTPException(status_code=400, detail="Withdrawal amount must be greater than 0")
        if user.balance > 15000:
            logger.warning(f"Withdrawal failed: amount {user.balance} exceeds limit for account='{account_number_value}'")
            raise HTTPException(status_code=403, detail="Cannot withdraw more than 15000 at once")
        if user_obj.balance < user.balance:
            logger.warning(f"Withdrawal failed: insufficient balance for account='{account_number_value}'")
            raise HTTPException(status_code=403, detail="Insufficient balance")
        user_obj.balance -= user.balance
        transaction = models.Transaction(
            sender_id=user_obj.account_number,
            receiver_id=user_obj.account_number,
            amount=user.balance,
            transaction_type=models.TransactionType.WITHDRAWAL
        )
        db.add(transaction)
        db.commit()
        db.refresh(user_obj)
        db.refresh(transaction)
        logger.info(f"Withdrawal successful for account='{account_number_value}', new balance={user_obj.balance}")
        return {"message": "Withdrawal successful", "balance": user_obj.balance}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error withdrawing money for {account_number_value}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred during withdrawal")


@router.post('/transfer/{account_number_value}/{receiver_account_number}', status_code=200, response_model=schemas.TransactionResponse)
def transfer_money(account_number_value: str, receiver_account_number: str, data: schemas.Transaction, db: Session = Depends(get_db)):
    '''To transfer money from my account to another'''
    logger.info(f"Transfer attempt from account='{account_number_value}' to account='{receiver_account_number}', amount={data.amount}")
    try:
        user_obj = db.query(models.User).filter(models.User.account_number == account_number_value).first()
        receiver_obj = db.query(models.User).filter(models.User.account_number == receiver_account_number).first()
        if not user_obj or not receiver_obj:
            logger.warning(f"Transfer failed: one or both accounts not found (sender='{account_number_value}', receiver='{receiver_account_number}')")
            raise HTTPException(status_code=400, detail="Account not found")
        if data.amount <= 0:
            logger.warning(f"Transfer failed: invalid amount {data.amount}")
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")
        if user_obj.balance < data.amount:
            logger.warning(f"Transfer failed: insufficient balance for account='{account_number_value}'")
            raise HTTPException(status_code=403, detail="Insufficient balance")
        user_obj.balance -= data.amount
        receiver_obj.balance += data.amount
        transaction = models.Transaction(
            sender_id=user_obj.account_number,
            receiver_id=receiver_obj.account_number,
            amount=data.amount,
            transaction_type=models.TransactionType.TRANSFER
        )
        db.add(transaction)
        db.commit()
        db.refresh(user_obj)
        db.refresh(receiver_obj)
        db.refresh(transaction)
        logger.info(f"Transfer successful from account='{account_number_value}' to account='{receiver_account_number}', amount={data.amount}")
        return {"message": "Money transferred successfully!", "balance": user_obj.balance}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transferring money from {account_number_value} to {receiver_account_number}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred during transfer")


@router.get('/history/{account_number_value}', status_code=200, response_model=List[schemas.TransactionHistoryItem])
def transaction_history(account_number_value: str, db: Session = Depends(get_db)):
    '''Transaction history'''
    logger.info(f"Transaction history request for account='{account_number_value}'")
    try:
        user = db.query(models.User).filter(models.User.account_number == account_number_value).first()
        if not user:
            logger.warning(f"Transaction history failed: account='{account_number_value}' not found")
            raise HTTPException(status_code=404, detail="User not found")
        transactions = db.query(models.Transaction).filter(
            (models.Transaction.sender_id == user.account_number) |
            (models.Transaction.receiver_id == user.account_number)
        ).order_by(models.Transaction.timestamp.desc()).all()
        logger.info(f"Returning {len(transactions)} transactions for account='{account_number_value}'")
        return transactions
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching transaction history for {account_number_value}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching transaction history")
