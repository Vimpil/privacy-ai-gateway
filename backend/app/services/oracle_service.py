import random
import re


class OracleService:
    _OPENINGS = (
        "The Cipher Oracle reveals...",
        "The system whispers...",
        "Signs indicate...",
    )

    @staticmethod
    def transform(ai_response: str) -> str:
        # Keep the style compact and readable for encrypted transport payloads.
        cleaned = re.sub(r"\s+", " ", ai_response).strip()
        if not cleaned:
            cleaned = "silence moves through the circuit."

        opening = random.choice(OracleService._OPENINGS)
        return f"{opening} {cleaned}"

