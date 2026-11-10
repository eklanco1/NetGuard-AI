import re
import os
import json
import logging
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
import psycopg
from pydantic import BaseModel, Field

load_dotenv()

logger = logging.getLogger(__name__)
router = APIRouter()

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

SYSTEM_PROMPT = """
You are NetGuard AI Security Assistant.

You help users understand cybersecurity, network
traffic, DDoS attacks, and defensive security.

NetGuard AI currently uses a binary MLP classifier
trained to distinguish BENIGN and DDoS traffic.

Important rules:
- Explain cybersecurity concepts clearly.
- Respond in the same language as the user.
- Give practical defensive security recommendations.
- Do not claim to access live network traffic.
- Do not invent prediction results or statistics.
- Do not claim the MLP model detects other attacks.
- If asked about a specific prediction, explain
  that actual prediction data is required.
- Distinguish model predictions from confirmed attacks.
- Keep responses concise and helpful.
"""


class ChatMessage(BaseModel):
    role: str
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[ChatMessage] = Field(
        default_factory=list,
        max_length=10
    )


@router.post("/chat")
def chat_with_assistant(request: ChatRequest):

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="Chatbot API key is not configured."
        )

    
    try:
        statistics = get_security_statistics()

    except psycopg.Error:
        logger.exception(
            "Unable to load security statistics"
        )

        statistics = None

    if statistics is not None:
        statistics_context = json.dumps(statistics)
    else:
        statistics_context = (
            "Statistics are currently unavailable."
        )

    # Prepoznajemo zahtjev za konkretnu predikciju
    prediction_match = re.search(
        r"(?:prediction|predikcij[aeiu]|predikciju)"
        r"\s*#?\s*(\d+)\b",
        request.message,
        re.IGNORECASE
    )

    prediction_context = ""

    if prediction_match:
        prediction_id = int(prediction_match.group(1))

        try:
            prediction_data = get_prediction_by_id(
                prediction_id
            )

        except psycopg.Error:
            logger.exception(
                "Unable to load prediction %s",
                prediction_id
            )

            prediction_data = None
            prediction_context = (
                f"Prediction lookup for ID {prediction_id} "
                "failed because the database is unavailable."
            )

        if not prediction_context:
            if prediction_data is None:
                prediction_context = (
                    f"Prediction ID {prediction_id} "
                    "was not found in the database."
                )
            else:
                prediction_context = json.dumps(
                    prediction_data
                )

    
    messages = [
        {
            "role": "system",
            "content": (
                SYSTEM_PROMPT

                + "\n\nCURRENT NETGUARD AI STATISTICS:\n"
                + statistics_context

                + "\n\nIMPORTANT STATISTICS RULES:\n"
                + "Use these statistics only when relevant. "
                + "Do not invent additional numbers. "
                + "Individual and batch statistics are separate. "
                + "Batch analyses may include repeated uploads. "
                + "These counts represent model classifications, "
                + "not independently confirmed attacks."

                + "\n\nREQUESTED PREDICTION DETAILS:\n"
                + (
                    prediction_context
                    if prediction_context
                    else "No specific prediction was requested."
                )

                + "\n\nPREDICTION EXPLANATION RULES:\n"
                + "Only discuss a prediction as a stored result "
                + "if its data was successfully retrieved. "
                + "If the prediction was not found or the lookup "
                + "failed, explicitly tell the user. "
                + "Do not invent prediction details. "
                + "The DDoS probability is a model output, "
                + "not proof of an attack. "
                + "Do not claim to know which features caused "
                + "the prediction without an explanation method."
            )
        }
    ]



    for item in request.history:
        if item.role in ("user", "assistant"):
            messages.append({
                "role": item.role,
                "content": item.content
            })

    messages.append({
        "role": "user",
        "content": request.message
    })

    payload = {
    "model": os.getenv(
        "OPENROUTER_MODEL",
        "openrouter/free"
    ),
    "messages": messages,
    "max_tokens": 1500
}

    http_request = Request(
        OPENROUTER_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-Title": "NetGuard AI"
        },
        method="POST"
    )

    try:
        with urlopen(http_request, timeout=40) as response:
            result = json.load(response)

    except HTTPError as exc:
        logger.warning(
            "OpenRouter returned HTTP %s",
            exc.code
        )

        if exc.code == 429:
            raise HTTPException(
                status_code=429,
                detail="Free API limit reached. Try again later."
            )

        raise HTTPException(
            status_code=502,
            detail="AI provider rejected the request."
        )

    except (URLError, TimeoutError):
        logger.exception("AI provider unavailable")

        raise HTTPException(
            status_code=503,
            detail="AI service is temporarily unavailable."
        )

    
    # Provjera odgovora OpenRouter API-ja

    if "error" in result:
        provider_error = result["error"]

        logger.error(
            "OpenRouter API error: %s",
            provider_error.get("message", "Unknown error")
        )

        raise HTTPException(
            status_code=502,
            detail="OpenRouter provider returned an error."
        )

    choices = result.get("choices", [])

    if not choices:
        logger.error(
            "OpenRouter returned no choices. Model: %s",
            result.get("model")
        )

        raise HTTPException(
            status_code=502,
            detail="AI provider returned no response choices."
        )

    choice = choices[0]

    if choice.get("error"):
        logger.error(
            "OpenRouter generation error: %s",
            choice["error"].get("message", "Unknown error")
        )

        raise HTTPException(
            status_code=502,
            detail="AI model failed during response generation."
        )

    message = choice.get("message") or {}
    answer = message.get("content")

    if not isinstance(answer, str) or not answer.strip():

        finish_reason = choice.get("finish_reason")
        model_name = result.get("model", "unknown")

        logger.error(
            "Empty AI response. Model=%s, finish_reason=%s",
            model_name,
            finish_reason
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "AI model returned an empty response. "
                "Check the backend terminal for details."
            )
        )
    
    return {
        "reply": answer,
        "model": result.get("model", "unknown")
    }



def get_prediction_by_id(prediction_id: int):

    with psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=5
    ) as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT
                    id,
                    prediction,
                    ddos_probability_percent,
                    created_at
                FROM public.ai_prediction_history
                WHERE id = %s;
            """, (prediction_id,))

            row = cursor.fetchone()

    if row is None:
        return None

    return {
        "prediction_id": row[0],
        "prediction": row[1],
        "ddos_probability_percent": float(row[2]),
        "created_at": row[3].isoformat()
    }


def get_security_statistics():

    with psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=5
    ) as connection:

        with connection.cursor() as cursor:

            # Pojedinacne AI predikcije
            cursor.execute("""
                SELECT
                    COUNT(*),
                    COUNT(*) FILTER (
                        WHERE prediction = 'BENIGN'
                    ),
                    COUNT(*) FILTER (
                        WHERE prediction = 'DDoS'
                    )
                FROM public.ai_prediction_history;
            """)

            individual = cursor.fetchone()

            # Batch analize
            cursor.execute("""
                SELECT
                    COUNT(*),
                    COALESCE(SUM(total_analyzed), 0),
                    COALESCE(SUM(benign_count), 0),
                    COALESCE(SUM(ddos_count), 0)
                FROM public.batch_analyses;
            """)

            batch = cursor.fetchone()

    individual_total = individual[0]
    individual_ddos = individual[2]

    individual_ddos_percentage = (
        individual_ddos / individual_total * 100
        if individual_total > 0 else 0
    )

    batch_total = batch[1]
    batch_ddos = batch[3]

    batch_ddos_percentage = (
        batch_ddos / batch_total * 100
        if batch_total > 0 else 0
    )

    return {
        "individual_predictions": {
            "total": individual_total,
            "benign": individual[1],
            "ddos": individual_ddos,
            "ddos_percentage": round(
                individual_ddos_percentage, 2
            )
        },
        "batch_analyses": {
            "total_batches": batch[0],
            "total_records": batch_total,
            "benign": batch[2],
            "ddos": batch_ddos,
            "ddos_percentage": round(
                batch_ddos_percentage, 2
            )
        }
    }
