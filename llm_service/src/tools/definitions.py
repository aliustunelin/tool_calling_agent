TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_users",
            "description": "Sistemdeki tüm kayıtlı kullanıcıları listeler. Her kullanıcının ID, e-posta, hesap durumu ve kayıt tarihi bilgisini döner. Kullanıcı sayısını da içerir.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_details",
            "description": "E-posta adresinden kullanıcı ID'si ve hesap durumunu getirir. Sistemde olmayan e-posta için hata döner.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "Kullanıcının e-posta adresi (örn: ali@sirket.com)",
                    }
                },
                "required": ["email"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_recent_transactions",
            "description": "Kullanıcının son işlemlerini getirir. İşlem numarası, tutar, para birimi, durum ve tarih bilgisi döner.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Kullanıcı ID'si (örn: u_1001)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Kaç işlem getirileceği (varsayılan: 5)",
                        "default": 5,
                    },
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_fraud_reason",
            "description": "Başarısız (failed) bir işlemin neden reddedildiğini sorgular. Sadece fraud kaydı olan işlemler için sonuç döner.",
            "parameters": {
                "type": "object",
                "properties": {
                    "transaction_id": {
                        "type": "string",
                        "description": "İşlem numarası (örn: tx_9001)",
                    }
                },
                "required": ["transaction_id"],
            },
        },
    },
]
