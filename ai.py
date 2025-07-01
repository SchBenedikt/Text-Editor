import ollama
import os

# --- Configuration ---
# Load Ollama settings from environment variables, with defaults.
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

def get_ollama_response(prompt: str, model: str = OLLAMA_MODEL) -> str:
    """
    Sends a prompt to the Ollama API using the official Python client.

    Args:
        prompt: The full prompt to send to the language model.
        model: The name of the Ollama model to use (e.g., 'llama3').

    Returns:
        The AI-generated text as a string, or an error message if something went wrong.
    """
    try:
        # The client automatically uses the OLLAMA_HOST environment variable if set.
        client = ollama.Client(host=OLLAMA_HOST)
        
        response = client.generate(
            model=model,
            prompt=prompt,
            stream=False
        )
        
        return response.get("response", "Error: No 'response' field in Ollama output.").strip()

    except Exception as e:
        # The ollama library's exceptions are not very specific yet,
        # so we catch a broad exception.
        return f"Error: An error occurred while communicating with Ollama. Is it running? Details: {e}"

# --- Pre-defined Prompts ---
# A dictionary of prompts for various editing tasks.
PROMPTS = {
    "improve": "You are an expert editor. Improve the following text, making it clearer, more concise, and more professional. Only return the improved text, without any explanation or preamble.",
    "autocorrect": "You are an expert editor. Correct all spelling and grammar mistakes in the following text. Only return the corrected text, without any explanation or preamble.",
    "summarize": "You are an expert summarizer. Provide a concise summary of the following text. Only return the summary, without any explanation or preamble.",
    "translate": "You are an expert translator. Translate the following text to {language}. Only return the translated text, without any explanation or preamble."
} 