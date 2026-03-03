import json
import logging

from src.service.api_client import (
    list_users,
    get_user_details,
    get_recent_transactions,
    check_fraud_reason,
)

logger = logging.getLogger(__name__)

TOOL_MAP = {
    "list_users": list_users,
    "get_user_details": get_user_details,
    "get_recent_transactions": get_recent_transactions,
    "check_fraud_reason": check_fraud_reason,
}


async def execute_tool(name: str, arguments: dict) -> str:
    fn = TOOL_MAP.get(name)
    if fn is None:
        error_msg = f"Bilinmeyen tool: {name}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)

    try:
        logger.info("Tool çalıştırılıyor: %s | args: %s", name, arguments)
        result = await fn(**arguments)
        logger.info("Tool sonucu: %s | result: %s", name, result)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        error_msg = f"Tool hatası ({name}): {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)
