import hikari, lightbulb, colorlog
import openai
import os
import json
import time

# init stuffs
logger = colorlog.getLogger()
config_dir = os.path.dirname(os.path.realpath(__file__))
api_key = os.environ['OPENAI_API_KEY']

# plugin thing
plugin = lightbulb.Plugin('chat')

# server message listener
@plugin.listener(hikari.MessageCreateEvent)
async def on_message(event: hikari.MessageCreateEvent):

    # read config everytime so you dont have to restart your bot after changing config lol
    config = read_config(config_dir)

    # if guild channel is not in list but let dms through
    if event.channel_id not in config['channels'] and event.message.guild_id is not None:
        return

    # this is the actual code to gather information, process the system prompt, and send the request to openai
    async with event.app.rest.trigger_typing(event.channel_id):
        
        # bot self object
        bot_self = await event.app.rest.fetch_my_user()

        # fetch message history
        print()
        logger.info(f'fetching last {config["max_chat_history"]} messages in channel {event.channel_id}')
        get_messages = await event.app.rest.fetch_messages(event.channel_id).limit(config['max_chat_history'])

        # the message to send
        logger.info('formatting messages')
        send_messages = await construct_message(get_messages, bot_self, config['system_prompt'])

        # send request
        logger.info(f'sending request to server')
        response = await send_request(api_key, config['base_url'], config['model'], config['temperature'], config['presence_penalty'], config['frequency_penalty'], config['top_p'], config['max_tokens'], send_messages)

    # send message
    if response:
        await event.app.rest.create_message(event.channel_id, response)

# construct the chat dialogue for openai api
async def construct_message(messages, bot_self, system_prompt):

    # put system message first
    formatted = [{'role': 'system', 'content': system_prompt}]

    # reverse the message list so it stays in chronological order
    for message in reversed(messages):
        content = message.content

        # wont send attatchements because... ya
        if message.attachments:
            attachment_desc = ', '.join(att.filename for att in message.attachments)
            content += f'\nAttachment(s): {attachment_desc}'

        # set role
        role = 'assistant' if message.author.id == bot_self.id else 'user'
        formatted.append({'role': role, 'content': content})

    return formatted

# send request to api
async def send_request(api_key, base_url, model, temperature, presence_penalty, frequency_penalty, top_p, max_tokens, messages):

    # timer start
    start_time = time.time()

    # base url is used for openai api compatible local inference servers (LMStudio, LMDeploy), otherwise it will use default
    client = openai.OpenAI(base_url=base_url, api_key=api_key) if base_url else openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model = model,
        temperature=temperature,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty,
        top_p=top_p,
        max_tokens=max_tokens,
        messages = messages
    )

    # timer end
    elapsed_time = time.time() - start_time
    logger.info(f'finished in {elapsed_time:.2f} seconds')
    if base_url:
        file_name = response.model.split("\\")[-1]
        model_name = file_name.split(".")[0]
        logger.info(f'model: {model_name}')
    logger.info(f'temperature: {temperature}')
    logger.info(f'fingerprint: {response.system_fingerprint}')
    logger.warning(f'prompt: {response.usage.prompt_tokens} tokens, completion: {response.usage.completion_tokens} tokens')
    return response

# load configs
def read_config(config_dir):

    # config file
    with open(os.path.join(config_dir, 'config.json'), 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)

    # system prompt
    with open(os.path.join(config_dir, 'system.txt'), 'r', encoding='utf-8') as system_file:
        system_prompt = system_file.read().strip()

    # return all of it XD
    return {
        'base_url': config['openai']['model'],
        'model': config['openai']['model'],
        'temperature': config['openai']['temperature'],
        'presence_penalty': config['openai']['presence_penalty'],
        'frequency_penalty': config['openai']['frequency_penalty'],
        'top_p': config['openai']['top_p'],
        'max_tokens': config['openai']['max_tokens'],
        'max_chat_history': config['bot']['max_chat_history'],
        'channels': config['bot']['channels'],
        'system_prompt': system_prompt
    }

# load plugin
def load(bot):
    bot.add_plugin(plugin)

# unload plugin
def unload(bot):
    bot.remove_plugin(plugin)