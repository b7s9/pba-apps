import datetime
import pathlib
import pkgutil

from interactions import Client, Intents, listen
from interactions.api.events import (
    GuildScheduledEventCreate,
    GuildScheduledEventDelete,
    GuildScheduledEventUpdate,
)
from interactions.ext import prefixed_commands

from discord.handlers import OnMessage
from events.models import ScheduledEvent


class PBADiscordBot(Client):
    @listen()
    async def on_ready(self):
        print(f"Logged on as {self.user}!")
        print(f"Joined guilds: {', '.join([str(g) for g in self.guilds])}")

        self.handlers = [
            handler() for handler in sorted(OnMessage.__subclasses__(), key=lambda x: x.priority)
        ]
        print("Loaded handlers:")
        for handler in self.handlers:
            print(handler.priority, handler)

    @listen()
    async def on_message_create(self, event):
        # Our bot should not pay attention to its own messages
        if event.message.author.id == self.user.id:
            return

        for handler in self.handlers:
            if await handler.condition(event.message):
                await handler.on_message(event.message)
                if handler.terminal:
                    break

    @listen(GuildScheduledEventCreate)
    async def on_scheduled_event_create(self, event):
        obj, created = await ScheduledEvent.objects.aupdate_or_create(
            discord_id=event.scheduled_event.id,
            defaults={
                "title": event.scheduled_event.name,
                "description": event.scheduled_event.description,
                "start_datetime": datetime.datetime.fromtimestamp(
                    event.scheduled_event.start_time.timestamp(),
                    tz=datetime.timezone.utc,
                ),
                "end_datetime": (
                    datetime.datetime.fromtimestamp(
                        event.scheduled_event.end_time.timestamp(),
                        tz=datetime.timezone.utc,
                    )
                    if event.scheduled_event.end_time
                    else datetime.datetime.fromtimestamp(
                        event.scheduled_event.start_time.timestamp(),
                        tz=datetime.timezone.utc,
                    )
                ),
                "location": (
                    event.scheduled_event.location
                    if event.scheduled_event.location
                    else f"Discord: #{event.scheduled_event.get_channel().name}"
                ),
                "cover": event.scheduled_event.cover.url if event.scheduled_event.cover else None,
                "status": ScheduledEvent.get_status(event.scheduled_event.status),
            },
        )

    @listen(GuildScheduledEventUpdate)
    async def on_scheduled_event_update(self, event):
        obj, created = await ScheduledEvent.objects.aupdate_or_create(
            discord_id=event.after.id,
            defaults={
                "title": event.after.name,
                "description": event.after.description,
                "start_datetime": datetime.datetime.fromtimestamp(
                    event.after.start_time.timestamp(),
                    tz=datetime.timezone.utc,
                ),
                "end_datetime": (
                    datetime.datetime.fromtimestamp(
                        event.after.end_time.timestamp(),
                        tz=datetime.timezone.utc,
                    )
                    if event.after.end_time
                    else datetime.datetime.fromtimestamp(
                        event.scheduled_event.start_time.timestamp(),
                        tz=datetime.timezone.utc,
                    )
                ),
                "location": (
                    event.after.location
                    if event.after.location
                    else f"Discord: #{event.after.get_channel().name}"
                ),
                "cover": event.after.cover.url if event.after.cover else None,
                "status": ScheduledEvent.get_status(event.after.status),
            },
        )

    @listen(GuildScheduledEventDelete)
    async def on_scheduled_event_delete(self, event):
        await ScheduledEvent.objects.filter(discord_id=event.scheduled_event.id).aupdate(
            status=ScheduledEvent.Status.DELETED,
        )

    def run(self, token):
        self.start(token)


bot = PBADiscordBot(
    description="I'm doing my part!",
    intents=Intents.ALL,
)

prefixed_commands.setup(bot, default_prefix="!")

for _, name, _ in pkgutil.walk_packages(
    [pathlib.Path(__file__).parent.resolve() / pathlib.Path("/commands")],
    prefix=__name__ + ".commands.",
):
    bot.load_extension(name)

for _, name, _ in pkgutil.walk_packages(
    [pathlib.Path(__file__).parent.resolve() / pathlib.Path("/components")],
    prefix=__name__ + ".components.",
):
    bot.load_extension(name)
