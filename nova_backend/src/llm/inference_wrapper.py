# src/llm/inference_wrapper.py

"""
This file contains the actual low‑level inference call.
It is kept separate so that changes to surrounding logic (logging, metrics, etc.)
do not affect the model version hash.
"""

from typing import List, Dict, Any


def run_inference(
    model,
    messages: List[Dict[str, str]],
    temperature: float,
    max_tokens: int,
) -> str:
    """
    Execute the model and return the generated text.
    This function should contain only the direct call to the model.
    """
    # Example for a HuggingFace model:
    # inputs = tokenizer.apply_chat_template(messages, return_tensors="pt")
    # outputs = model.generate(inputs, temperature=temperature, max_new_tokens=max_tokens)
    # return tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Placeholder implementation (replace with actual model call):
    return "Simulated inference output."