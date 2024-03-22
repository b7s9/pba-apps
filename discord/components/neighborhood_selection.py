import re

from asgiref.sync import sync_to_async
from django.conf import settings
from interactions import (
    Button,
    ButtonStyle,
    Embed,
    Extension,
    OptionType,
    SlashContext,
    component_callback,
    listen,
    slash_command,
    slash_option,
    spread_to_rows,
)
from interactions.api.events import Startup

EMBED_TITLE = "Neighborhood Selection"
EMBED_DESCRIPTION = """
Use the buttons below to join or leave neighborhood channels!

To request a neighborhood, use the `/neighborhood` command!
"""


class NeighborhoodSelection(Extension):
    SELECTION_CHANNEL = settings.NEIGHBORHOOD_SELECTION_DISCORD_CHANNEL_ID

    def __init__(self, bot):
        self.bot = bot
        self.components = None
        self.NEIGHBORHOODS = {}

    @slash_command(name="neighborhood", description="Request a neighborhood channel")
    @slash_option(
        name="neighborhood_name",
        description="The name of the neighborhood you are requesting",
        required=True,
        opt_type=OptionType.STRING,
    )
    async def request_neighborhood(self, ctx: SlashContext, neighborhood_name: str):
        from neighborhood_selection.models import Neighborhood

        neighborhood, _ = await Neighborhood.objects.aget_or_create(
            defaults={"name": neighborhood_name},
            name__iexact=neighborhood_name,
        )
        if neighborhood.approved:
            await ctx.send(
                (
                    f"{neighborhood.name} channel already exists, "
                    "use the button in #neighborhood-selection to join!"
                ),
                ephemeral=True,
            )
            return
        neighborhood.requests += 1
        await neighborhood.asave()
        msg = f"Neighborhood request for {neighborhood_name} recorded!"
        if neighborhood.requests > 1:
            msg += f" You and {neighborhood.requests - 1} users are waiting for it to be approved."
        await ctx.send(msg, ephemeral=True)

    @staticmethod
    async def update_buttons(bot, selection_channel, components):
        from neighborhood_selection.models import Neighborhood

        if not selection_channel:
            print("No selection channel, bailing!")

        guild = await bot.fetch_guild(settings.NEIGHBORHOOD_SELECTION_DISCORD_GUILD_ID)
        BUTTONS = []
        for neighborhood in await sync_to_async(list)(Neighborhood.objects.all()):
            role = await guild.fetch_role(neighborhood.discord_role_id, force=True)
            label = neighborhood.name
            if len(role.members) == 1:
                label = f"{neighborhood.name} ({len(role.members)} 👤)"
            elif len(role.members) > 1:
                label = f"{neighborhood.name} ({len(role.members)} 👥)"
            BUTTONS.append(
                Button(
                    style=ButtonStyle.PRIMARY,
                    label=label,
                    custom_id=f"neighborhood_selection_{neighborhood.id}",
                )
            )
        if BUTTONS:
            components = spread_to_rows(*BUTTONS)

        embed = Embed(
            title=EMBED_TITLE,
            description=EMBED_DESCRIPTION,
        )
        channel = await bot.fetch_channel(selection_channel)
        async for message in channel.history():
            if len(message.embeds) == 1 and message.embeds[0].title == EMBED_TITLE:
                print("updating embed...")
                await message.edit(content=None, embeds=[embed], components=components)
                return
        await bot.get_channel(selection_channel).send(None, embeds=[embed], components=components)

    @listen(Startup)
    async def startup(self):
        await self.update_buttons(self.bot, self.SELECTION_CHANNEL, self.components)

    BUTTON_ID_REGEX = re.compile(r"neighborhood_selection_(.*)")

    @component_callback(BUTTON_ID_REGEX)
    async def callback(self, ctx):
        from neighborhood_selection.models import Neighborhood

        neighborhood_id = ctx.custom_id.replace("neighborhood_selection_", "")
        neighborhood = await Neighborhood.objects.filter(id=neighborhood_id).afirst()
        if neighborhood is None:
            await ctx.send("No neighborhood found!", ephemeral=True)
            return

        guild = await self.bot.fetch_guild(settings.NEIGHBORHOOD_SELECTION_DISCORD_GUILD_ID)
        role = await guild.fetch_role(neighborhood.discord_role_id)
        if role not in ctx.member.roles:
            await ctx.member.add_role(neighborhood.discord_role_id)
            await ctx.send(f"Added {neighborhood.name} role!", ephemeral=True)
            await self.update_buttons(self.bot, self.SELECTION_CHANNEL, self.components)
            return
        else:
            await ctx.member.remove_role(neighborhood.discord_role_id)
            await ctx.send(f"Removed {neighborhood.name} role.", ephemeral=True)
            await self.update_buttons(self.bot, self.SELECTION_CHANNEL, self.components)
            return


def setup(bot):
    NeighborhoodSelection(bot)
