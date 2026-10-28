"""
Sample Unicode and Special Characters for CodeFlow Studio verification.
Tests emojis, mathematical symbols, Asian typography, quotes, and brackets.
"""

# Mathematical and scientific notation
MATH_SYMBOLS = "∑(x_i) ≥ 0, ∀x ∈ ℝ, α ≠ β, λ → ∞"

# International alphabets
GREETINGS = {
    "en": "Hello, world!",
    "zh": "你好，世界！",
    "ja": "こんにちは、世界！",
    "ru": "Привет, мир!",
    "ar": "مرحبا بالعالم!",
    "es": "¡Hola, mundo! ¿Cómo estás?",
}

# Emoticons and astral plane symbols
EMOJIS = "🚀 💻 ✨ 🎯 ⚙️ 🔍 🛡️ 📊"

# Nested quotes, backticks, and bracket combinations
NESTED_PUNCTUATION = """[ { "key": [ ( 'sub-key', `template-literal` ) ] } ]"""

def verify_all_symbols():
    print("Testing Symbols:", MATH_SYMBOLS)
    print("Testing Astral Plane Emojis:", EMOJIS)
    for lang, text in GREETINGS.items():
        print(f"[{lang}] {text}")

if __name__ == "__main__":
    verify_all_symbols()
