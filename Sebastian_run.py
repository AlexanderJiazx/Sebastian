import os
import google.generativeai as genai
from gtts import gTTS
import re
from PIL import Image
from PIL import ImageGrab
import clipboard


genai.configure(api_key="YOUR_API_KEY")


user_input = input("User: ")

myscreen = ImageGrab.grab()
myscreen.save("screenshot.png")

# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
  "temperature": 1,
  "top_p": 0.5,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}
safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_NONE",
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_NONE",
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_NONE",
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_NONE",
  },
]

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  safety_settings=safety_settings,
  generation_config=generation_config,
  system_instruction="Your name is Sebastian, You are a digital assistant to help user control computer, use tool to control user's computer.\n\nHere's some tool:\nIn output, you can use the XML tag <terminal_command></terminal_command> to control macOS terminal, every command with this tag will be send to terminal\nremember macOS terminal grammar.\n\n\nIf you have to use terminal, then use terminal first, after that you can output normal text\n\nexample:\n\nUser: \nHelp me open google\nYou:\n<terminal_command>open google.com</terminal_command>\nIt's opened.\nAnd you can also use Google search by terminal,\n\nExample:\nSearch \"space\"\nopen https://www.google.com/search?q=Space",
)

def upload_to_gemini(path, mime_type=None):

  file = genai.upload_file(path, mime_type=mime_type)
  return file
current_screen = upload_to_gemini("screenshot.png", mime_type="image/png")


chat_session = model.start_chat(
  history=[
 {
      "role": "user",
      "parts": [
        current_screen,
        "SYSTEM: [This image is a screenshot from user's Mac just now]",
      ],
    }
  ]
)

response = chat_session.send_message(user_input)

response_text = response.text

output_modified = re.sub(r'[*#]', '', response_text)

print(output_modified)

##speech = gTTS(text=speech_text, lang="en", slow=False)

# Saving the converted audio to a file
#speech.save("output.mp3")
# os.system("afplay output.mp3")

extract = response.text

commands = re.findall(r'<terminal_command>(.*?)</terminal_command>', extract)
commands_string = "\n".join(commands)

os.system(commands_string)
