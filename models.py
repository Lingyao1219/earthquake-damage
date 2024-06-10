import time
import base64
import PIL.Image
from openai import OpenAI
import google.generativeai as genai
from prompts import *

SECRET_FILE = 'secrets.txt'

with open('secrets.txt') as f:
    lines = f.readlines()
    for line in lines:
        if line.split(',')[0].strip() == "openai_key":
            openai_key = line.split(',')[1].strip()
        elif line.split(',')[0].strip() == "gemini_key":
            gemini_key = line.split(',')[1].strip()


openai_client = OpenAI(api_key=openai_key)

def encode_image64(image_path):
    """Encode an image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def call_gpt4o_text(message):
    """Call the GPT-4o model for text information and return the response."""
    response = openai_client.chat.completions.create(
        model = "gpt-4o", 
        messages=[{"role": "user", 
                   "content": message}],
        temperature=0.0,
        max_tokens=1000
    )
    return response.choices[0].message.content


def call_gpt4o_image(message, image):
    """Call the GPT-4o model for image information and return the response."""
    base64_image = encode_image64(image)
    response = openai_client.chat.completions.create(
        model = "gpt-4o", 
        messages=[{"role": "user", 
                   "content": [
                    {"type": "text", "text": message},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}]
                    }],
        temperature=0.0,
        max_tokens=1000
    )
    return response.choices[0].message.content


def call_gemini_text(message):
    """Call the Gemini model for text information and return the response."""
    retries = 20
    while retries > 0:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(message)
            return response.text
        except Exception as e:
            retries -= 1
            time.sleep(0.1)


def call_gemini_image(message, image):
    """Call the Gemini model for image information and return the response."""
    retries = 20
    while retries > 0:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            img = PIL.Image.open(image)
            response = model.generate_content([message, img], stream=True)
            response.resolve()
            return response.text
        except Exception as e:
            retries -= 1
            time.sleep(0.1)


def call_model(model, input, message, image=None):
    """Call the model based on the input and model type."""
    if model == 'gpt4' and input == 'text':
        result = call_gpt4o_text(message)
    elif model == 'gpt4' and input == 'image':
        result = call_gpt4o_image(message, image)
    elif model == 'gemini' and input == 'text':
        result = call_gemini_text(message)
    elif model == 'gemini' and input == 'image':
        result = call_gemini_image(message, image)
    return result


if __name__ == "__main__":
    text_message = "how are you?"
    image_message = "Identify the earthquake-related damage based on the Modified Mercalli Intensity (MMI) Scale."
    image_url = "images/test1.png"
    print(call_model('gemini', 'image', image_message, image_url))
    print(call_model('gemini', 'text', text_message))