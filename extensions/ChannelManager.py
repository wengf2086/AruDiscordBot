import hikari
import lightbulb

plugin = lightbulb.Plugin('ChannelManager')

def load(bot):
    bot.add_plugin(plugin)