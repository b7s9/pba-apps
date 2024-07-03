from asgiref.sync import async_to_sync
from celery import shared_task
from django.conf import settings

from discord.bot import bot


async def _add_user_to_connected_role(uid):
    await bot.login(settings.DISCORD_BOT_TOKEN)
    guild = await bot.fetch_guild(settings.DISCORD_CONNECTED_GUILD_ID)
    role = await guild.fetch_role(settings.DISCORD_CONNECTED_ROLE_ID)
    member = await guild.fetch_member(uid)
    await member.add_role(role.id)


@shared_task
def add_user_to_connected_role(uid):
    async_to_sync(_add_user_to_connected_role)(uid)


async def _remove_user_from_connected_role(uid):
    await bot.login(settings.DISCORD_BOT_TOKEN)
    guild = await bot.fetch_guild(settings.DISCORD_CONNECTED_GUILD_ID)
    role = await guild.fetch_role(settings.DISCORD_CONNECTED_ROLE_ID)
    member = await guild.fetch_member(uid)
    await member.remove_role(role.id)


@shared_task
def remove_user_from_connected_role(uid):
    async_to_sync(_remove_user_from_connected_role)(uid)
