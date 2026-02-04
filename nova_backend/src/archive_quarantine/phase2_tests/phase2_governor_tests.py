# phase2_governor_tests.py
from governor.governor_mediator import GovernorMediator

gm = GovernorMediator()

# Simulated LLM output that WRONGFULLY claims execution
malicious_llm_output = {
    "text": "I have opened your Documents folder and started the application.",
}

result = gm.receive_from_llm(malicious_llm_output)

print("Governor output:")
print(repr(result))

# Test 2: Malformed payload (not a dict)
result = gm.receive_from_llm("open documents")
print("Malformed payload output:")
print(repr(result))

# Test 3: Empty dict payload
result = gm.receive_from_llm({})
print("Empty payload output:")
print(repr(result))

# Test 4: Repeated calls (no state leak)
result1 = gm.receive_from_llm({"text": "I opened files"})
result2 = gm.receive_from_llm({"text": "I opened more files"})
print("Repeated calls output:")
print(repr(result1), repr(result2))

