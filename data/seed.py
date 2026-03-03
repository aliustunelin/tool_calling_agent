import os
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "tool_agent_demo")

if not MONGO_URI:
    print("MONGO_URI ortam değişkeni bulunamadı. .env dosyasını kontrol edin.")
    sys.exit(1)

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

# --- Mevcut veriyi temizle (idempotent) ---
db.users.drop()
db.transactions.drop()
db.fraud_logs.drop()
print("Mevcut koleksiyonlar temizlendi.")

# --- Users ---
users = [
    {
        "_id": "u_1001",
        "email": "ali@sirket.com",
        "account_status": "active",
        "created_at": datetime(2026, 3, 3, 15, 0, 0, tzinfo=timezone.utc),
    },
    {
        "_id": "u_1002",
        "email": "ayse@sirket.com",
        "account_status": "suspended",
        "created_at": datetime(2026, 3, 3, 15, 0, 0, tzinfo=timezone.utc),
    },
    {
        "_id": "u_1003",
        "email": "mehmet@sirket.com",
        "account_status": "active",
        "created_at": datetime(2026, 3, 3, 15, 0, 0, tzinfo=timezone.utc),
    },
]
db.users.insert_many(users)
db.users.create_index("email", unique=True)
print(f"{len(users)} kullanıcı eklendi.")

# --- Transactions ---
transactions = [
    {
        "_id": "tx_9001",
        "user_id": "u_1001",
        "amount": 1250.50,
        "currency": "TRY",
        "status": "failed",
        "created_at": datetime(2026, 3, 2, 14, 32, 0, tzinfo=timezone.utc),
    },
    {
        "_id": "tx_9002",
        "user_id": "u_1001",
        "amount": 500.00,
        "currency": "TRY",
        "status": "success",
        "created_at": datetime(2026, 3, 1, 10, 0, 0, tzinfo=timezone.utc),
    },
    {
        "_id": "tx_9003",
        "user_id": "u_1002",
        "amount": 220.00,
        "currency": "TRY",
        "status": "failed",
        "created_at": datetime(2026, 3, 2, 16, 45, 0, tzinfo=timezone.utc),
    },
    {
        "_id": "tx_9004",
        "user_id": "u_1003",
        "amount": 780.00,
        "currency": "TRY",
        "status": "pending",
        "created_at": datetime(2026, 3, 2, 18, 0, 0, tzinfo=timezone.utc),
    },
]
db.transactions.insert_many(transactions)
db.transactions.create_index("user_id")
db.transactions.create_index("created_at")
print(f"{len(transactions)} işlem eklendi.")

# --- Fraud Logs ---
fraud_logs = [
    {
        "_id": "tx_9001",
        "reason_code": "INSUFFICIENT_FUNDS",
        "reason_message": "Yetersiz bakiye nedeniyle işlem reddedildi.",
        "checked_at": datetime(2026, 3, 2, 14, 32, 5, tzinfo=timezone.utc),
    },
    {
        "_id": "tx_9003",
        "reason_code": "SUSPICIOUS_ACTIVITY",
        "reason_message": "Şüpheli işlem tespit edildi, işlem reddedildi.",
        "checked_at": datetime(2026, 3, 2, 16, 45, 5, tzinfo=timezone.utc),
    },
]
db.fraud_logs.insert_many(fraud_logs)
print(f"{len(fraud_logs)} fraud kaydı eklendi.")

print("\nSeed tamamlandı!")
client.close()
