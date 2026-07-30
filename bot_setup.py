from commands.notif_stream import setup as setup_notif_stream
from commands.roles_link import setup as setup_riot_link
from commands.temp_voice import setup as setup_temp_voice
from commands.clear import setup as setup_clear
from commands.help import setup as setup_help
from commands.update_rank import setup as setup_update_rank
from commands.delete_rank import setup as setup_delete_rank
from monnaie.commands.give_command import setup as setup_give

async def bot_setup(bot):
    setup_notif_stream(bot, bot.twitch_bot)
    setup_riot_link(bot, bot.discord_api, bot.twitch_linker)
    setup_clear(bot)
    setup_help(bot)
    setup_update_rank(bot)
    setup_delete_rank(bot)
    await setup_temp_voice(bot)

    #setup_give(bot)