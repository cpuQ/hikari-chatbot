# installation
```bash
git clone https://github.com/cpuQ/hikari-chatbot.git
```
```bash
cd hikari-chatbot
```
```Pip Requirements
python -m pip install -r requirements.txt
```
> [!note]
> i only tested it with python 3.11 on windows lol

# setup
open the `.env` file and put in your openai api key and discord bot token
```
OPENAI_API_KEY = put api key here
DISCORD_BOT_TOKEN = pur token here 
```
> [!important]
> **DO NOT** put quotes around them "like this"

# configuration
open the `config.json` file in `chat/plugins/` in any text editor and configure stuff there :P
```json
{
  "openai": {
    "base_url": "", <- this is only for inferencing with local models using something like LMStudio
    "model": "gpt-4o-mini",
    "temperature": 1.0,
    "presence_penalty": 1.0,
    "frequency_penalty": 1.0,
    "top_p": 0.5,
    "max_tokens": 1024
  },
  "bot": {
    "max_chat_history": 21,
    "channels": []
  }
}
```
