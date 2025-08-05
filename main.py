import ollama
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils.logger import get_logger
from utils.masking import mask_ip_in_text
import os
import requests

# Set the Ollama API URL from environment variable or default to localhost
ollama_api_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
ollama_model = os.getenv("OLLAMA_MODEL", "llama3")

app = FastAPI()
logger = get_logger(__name__)

ollama_client = ollama.Client(host=ollama_api_url)

@app.get("/health")
def health_check():
    logger.info("Health check endpoint called.")
    # Call the Ollama API to check if it's running
    try:
        logger.info(f"Checking health of Ollama API at {ollama_api_url}")
        response = requests.get(f"{ollama_api_url}")
        response.raise_for_status()
        logger.info("Ollama API is reachable.")
    except requests.RequestException as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Ollama API is not reachable")

    # Return health status including dependencies
    return {
        "status": "ok",
        "message": "API is running smoothly",
        "dependencies": {
            "ollama": "reachable"
        }
    }


class NLPRequest(BaseModel):
    message: str

@app.post("/interpret")
def get_intent(data: NLPRequest):
    """
    Endpoint to interpret natural language instructions and return JSON commands. It tries 3 times to interpret the request using Ollama's chat model.
    """
    for _ in range(3):
        try:
            return interpret_and_execute(data)
        except HTTPException as e:
            if e.status_code != 500:
                raise
            logger.error(f"Error interpreting request: {str(e)}. Retrying...")
    logger.error("Failed to interpret the request after 3 attempts.")
    raise HTTPException(status_code=500, detail="Unable to interpret the request after multiple attempts.")

def interpret_and_execute(data: NLPRequest):
    """
    This function uses Ollama's chat model to convert natural language instructions into structured JSON commands.
    It handles specific actions like adding an IP to a security list or providing instructions on how to find an IP address.
    """
    logger.info(f"Interpreting message: {mask_ip_in_text(data.message)}")
    try:
        
        prompt = f"""
        You are a Discord Bot that converts natural language instructions into JSON commands.

        All the responses should be in Spanish and formatted as JSON objects with the following structure:
        {{
            "action": "<action_name>",
            "response": "<response>"
        }}

        If the input is not clear or does not match any known action, respond with an error message in JSON format in Spanish like this one:
        {{
            "action": "error",
            "response": "Lo siento, no entiendo la instrucción. Contacta a Julio si crees que esto es un error."
        }}

        Notes: 
        - Only respond with the JSON object, no additional text.
        - Always use a proper JSON format.
        - Do not create any new actions, only use the ones provided in the examples below.

        Action 1: Adding an IP:
        Context: You are managing a security list in a cloud environment. The users want to access a Minecraft server. They need to add their IP addresses to the security list.
        Input: "Agrega mi IP 203.0.113.42"
        Output: {{
            "action": "add_ip",
            "response": "203.0.113.42"
        }}
        Notes: 
        - If the user mentions that they cannot access the server, you will add their IP to the security list. 
        - Do not try to guess the old or new IP, it must be provided by the user. -
        - Avoid adding new information that is not in the input.
        - If the user provides an IP address, the action needs to be "add_ip" and you will return it in the response.
        - If the user does not provide an IP address, DO NOT use this action. Instead, use the "get_ip" action to guide them on how to find their IP address.
        - Always validate that the provided IP address is in a correct format (e.g., IPv4).
        - The response should only contain the IP address in the "response" field, nothing else

        Action 2: Asking how to get IP:
        Context: You are an assistant that helps users find their IP addresses.
        Input: "¿Cómo puedo saber mi IP? Usuario: Alex."
        Output: {{
            "action": "get_ip",
            "response": "Puedes encontrar tu IP en https://whatismyipaddress.com/. La IP que debes agregar es la que dice 'IPv4 Address'. Una vez que la tengas, mandame un mensaje con tu IP y te ayudaré a agregarla al servidor de Minecraft."
        }}
        Notes: 
        - This action is just for providing instructions on how to find the IP address. 
        - The response should guide the user to find their IP and inform them to send it back for further action. 
        - This is made for non-technical users, so the instructions should be clear and simple.

        Action 3: Small talk:
        Context: You are a friendly assistant that responds to the users if they engage in small talk.
        Input: "Hola, soy Julio."
        Output: {{
            "action": "small_talk",
            "response": "<friendly message in Spanish>"
        }}
        Notes: 
        - This is a fallback action for when the user engages in small talk or provides a message that does not require any specific action.
        - The response should be a friendly message in Spanish, acknowledging the user's message.
        - Only use this action if the input does not match any of the previous actions.
        - This action is just for chatting and does not require any additional information. You can respond with any friendly message in Spanish.


        Now interpret this input:
        {data.message}
        """
        try:
            response = ollama_client.chat(
                model=ollama_model,
                messages=[{"role": "user", "content": prompt}]
            )
            logger.info(f"Response obtained from Ollama: {mask_ip_in_text(str(response))}")
        except Exception as e:
            logger.error(f"Error calling Ollama chat model: {str(e)}")
            raise HTTPException(status_code=500, detail="Error processing request with Ollama.")
        try:
            command_json = response["message"]["content"]
        except KeyError:
            logger.error("Invalid response format from Ollama.")
            raise HTTPException(status_code=500, detail="Invalid response format from Ollama.")
        
        import json
        command = json.loads(command_json)

        logger.info(f"Interpreted command: {mask_ip_in_text(str(command))}")
        return command
    except Exception as e:
        logger.error(f"Error interpreting request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
