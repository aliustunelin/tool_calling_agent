import logging
from datetime import datetime

from pymongo import MongoClient, DESCENDING
from src.utils.config import settings

logger = logging.getLogger(__name__)

_client: MongoClient | None = None
_db = None


def get_db():
    global _client, _db
    if _db is None:
        _client = MongoClient(settings.MONGO_URI)
        _db = _client[settings.MONGO_DB_NAME]
        logger.info("MongoDB bağlantısı kuruldu: %s", settings.MONGO_DB_NAME)
    return _db


def check_connection() -> bool:
    try:
        db = get_db()
        db.command("ping")
        return True
    except Exception as e:
        logger.error("MongoDB bağlantı hatası: %s", e)
        return False


def get_user_details(email: str) -> dict:
    db = get_db()
    user = db.users.find_one({"email": email})
    if not user:
        raise ValueError(f"Kullanıcı bulunamadı: {email}")
    return {
        "user_id": user["_id"],
        "email": user["email"],
        "account_status": user["account_status"],
        "created_at": user["created_at"].isoformat() if isinstance(user["created_at"], datetime) else str(user["created_at"]),
    }


def get_recent_transactions(user_id: str, limit: int = 5) -> list[dict]:
    db = get_db()
    cursor = (
        db.transactions.find({"user_id": user_id})
        .sort("created_at", DESCENDING)
        .limit(limit)
    )
    transactions = []
    for tx in cursor:
        transactions.append({
            "id": tx["_id"],
            "amount": tx["amount"],
            "currency": tx.get("currency", "TRY"),
            "status": tx["status"],
            "created_at": tx["created_at"].isoformat() if isinstance(tx["created_at"], datetime) else str(tx["created_at"]),
        })
    if not transactions:
        raise ValueError(f"İşlem bulunamadı: user_id={user_id}")
    return transactions


def list_users() -> list[dict]:
    db = get_db()
    cursor = db.users.find()
    users = []
    for user in cursor:
        users.append({
            "user_id": user["_id"],
            "email": user["email"],
            "account_status": user["account_status"],
            "created_at": user["created_at"].isoformat() if isinstance(user["created_at"], datetime) else str(user["created_at"]),
        })
    return users


def check_fraud_reason(transaction_id: str) -> dict:
    db = get_db()
    fraud = db.fraud_logs.find_one({"_id": transaction_id})
    if not fraud:
        raise ValueError(f"Fraud kaydı bulunamadı: transaction_id={transaction_id}")
    return {
        "transaction_id": fraud["_id"],
        "reason_code": fraud["reason_code"],
        "reason_message": fraud["reason_message"],
        "checked_at": fraud["checked_at"].isoformat() if isinstance(fraud["checked_at"], datetime) else str(fraud["checked_at"]),
    }
