import re


class ResponseFormatter:
    @staticmethod
    def format(text: str) -> str:
        clean = (text or "").strip()
        clean = re.sub(r"  +", " ", clean)
        clean = re.sub(r"!+", ".", clean)
        clean = re.sub(r"([.!?])([A-Z])", r"\1 \2", clean)

        for filler in [r"\bwell\b", r"\bso\b", r"\byou see\b"]:
            clean = re.sub(filler, "", clean, flags=re.IGNORECASE)

        return re.sub(r"\s{2,}", " ", clean).strip()
