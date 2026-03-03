import json
import logging

from openai import AsyncOpenAI
from src.utils.config import settings
from src.tools.definitions import TOOLS
from src.tools.executor import execute_tool

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Sen bir müşteri destek asistanısın. Kullanıcının sorusunu yanıtlamak için sana verilen araçları kullan.

Adım adım düşün:
1. Hangi bilgiye ihtiyacın var?
2. Bu bilgiyi hangi araçla alabilirsin?
3. Aldığın bilgi yeterli mi, yoksa başka bir araç daha mı çağırmalısın?

Kurallar:
- Eksik bilgi varsa (örneğin e-posta adresi verilmemişse) kullanıcıdan iste, rastgele araç çağırma.
- Hata durumlarını kullanıcıya nazik ve anlaşılır bir dille açıkla.
- Yanıtlarını Türkçe ver.
"""

MAX_ITERATIONS = 10


def _get_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        base_url=settings.LLM_BASE_URL,
        api_key=settings.LLM_API_KEY,
    )


async def run_agent(user_message: str) -> dict:
    client = _get_client()
    tool_calls_log = []

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    for iteration in range(MAX_ITERATIONS):
        logger.info("=== Agent iterasyon %d ===", iteration + 1)

        response = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        choice = response.choices[0]
        assistant_message = choice.message

        messages.append(assistant_message.model_dump())

        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)

                logger.info("Tool çağrısı: %s(%s)", fn_name, fn_args)

                result_str = await execute_tool(fn_name, fn_args)

                tool_calls_log.append({
                    "tool": fn_name,
                    "args": fn_args,
                    "result": json.loads(result_str),
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result_str,
                })
        else:
            final_response = assistant_message.content or ""
            logger.info("Agent yanıtı: %s", final_response)
            return {
                "response": final_response,
                "tool_calls_log": tool_calls_log,
            }

    logger.warning("Max iterasyona ulaşıldı (%d)", MAX_ITERATIONS)
    return {
        "response": "Üzgünüm, isteğinizi işlerken çok fazla adım gerekti. Lütfen sorunuzu daha spesifik hale getirin.",
        "tool_calls_log": tool_calls_log,
    }
