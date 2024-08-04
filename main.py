import hikari, lightbulb, colorlog
import os

# create a logger
logger = colorlog.getLogger()

# file directories
script_dir = os.path.dirname(__file__)
plugins_dir = os.path.join(script_dir, 'plugins')

# hikari bot
intents = hikari.Intents.ALL
token = os.getenv('DISCORD_BOT_TOKEN')
bot = lightbulb.BotApp(intents=intents, token=token)

# load plugins
def load_active_plugins():

    # read active plugins
    with open(os.path.join(plugins_dir, 'active.cfg'), 'r', encoding='utf-8') as active:
        active_plugins = active.read().splitlines()

    # reads every directory in the plugins directory
    for plugin in os.listdir(plugins_dir):

        # check if its a directory or not
        plugin_path = os.path.join(plugins_dir, plugin)
        plugin_name = os.path.basename(plugin_path)
        if not os.path.isdir(plugin_path):
            continue

        # checks if plugin is active
        if plugin_name not in active_plugins:
            continue

        # try to load the plugin
        try:
            bot.load_extensions(f'{os.path.basename(plugins_dir)}.{plugin_name}.plugin')
        except Exception as e:
            logger.error(f'error loading plugin "{plugin_name}": {e}')

    # just separator
    print()

# run the bot
if __name__ == '__main__':
    load_active_plugins()
    bot.run()