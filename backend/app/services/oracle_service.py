class OracleService:
    @staticmethod
    def transform(message: str, ai_response: str) -> str:
        return (
            "[Cipher Oracle]\n"
            f"Question: {message}\n"
            "Verdict:\n"
            f"{ai_response.strip()}"
        )

