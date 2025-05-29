from asgiref.sync import async_to_sync, sync_to_async
from celery import shared_task
from django.conf import settings
from django.urls import reverse
from interactions.models.discord.enums import AutoArchiveDuration

from pba_discord.bot import bot
from projects.models import ProjectApplication


async def _add_new_project_message_and_thread(project_application_id):
    application = await ProjectApplication.objects.filter(id=project_application_id).afirst()
    if application is None or application.draft or application.thread_id:
        return

    await bot.login(settings.DISCORD_BOT_TOKEN)
    guild = await bot.fetch_guild(settings.NEW_PROJECT_REVIEW_DISCORD_GUILD_ID)
    channel = await guild.fetch_channel(settings.NEW_PROJECT_REVIEW_DISCORD_CHANNEL_ID)
    mention_role = await guild.fetch_role(settings.NEW_PROJECT_REVIEW_DISCORD_ROLE_MENTION_ID)
    submitter = await sync_to_async(lambda: application.submitter)()
    profile = await sync_to_async(lambda: submitter.profile)()
    discord = await sync_to_async(lambda: profile.discord)()
    discord_username = discord.extra_data["username"]
    thread = await channel.create_thread(
        name=f"{application.data['shortname']['value']}",
        reason=f"Project Application submitted by {discord_username}",
        auto_archive_duration=AutoArchiveDuration.ONE_WEEK,
    )
    if not application.markdown:
        await sync_to_async(application.render_markdown)()
    msg = ""
    in_response = False
    for line in application.markdown.split("\n"):
        if line == "```":
            if in_response:
                in_response = False
            else:
                in_response = True
        if len(msg) + len(line) >= 1990:
            if in_response:
                msg += "```\n"
            await thread.send(msg)
            msg = ""
            if in_response:
                msg += "```\n"
        msg += line + "\n"
    await thread.send(msg)
    link = reverse("project_application_view", kwargs={"pk": application.id})
    link = f"https://apps.bikeaction.org{link}"
    await thread.send(
        f"{mention_role.mention} please review and vote with :white_check_mark: or :x:.\n\n"
        f"You can view the application online [here]({link}) after logging in."
    )
    application.thread_id = thread.id
    await application.asave()


async def _add_new_project_voting_message_and_thread(project_application_id):
    application = await ProjectApplication.objects.filter(id=project_application_id).afirst()
    if application is None or application.approved or application.voting_thread_id:
        return

    await bot.login(settings.DISCORD_BOT_TOKEN)
    guild = await bot.fetch_guild(settings.NEW_PROJECT_REVIEW_DISCORD_GUILD_ID)
    discussion_thread = await guild.fetch_channel(application.thread_id)
    channel = await guild.fetch_channel(settings.NEW_PROJECT_REVIEW_DISCORD_VOTE_CHANNEL_ID)
    mention_role = await guild.fetch_role(settings.NEW_PROJECT_REVIEW_DISCORD_ROLE_VOTE_MENTION_ID)
    submitter = await sync_to_async(lambda: application.submitter)()
    profile = await sync_to_async(lambda: submitter.profile)()
    discord = await sync_to_async(lambda: profile.discord)()
    discord_username = discord.extra_data["username"]
    thread = await channel.create_thread(
        name=f"Vote: Project - {application.data['shortname']['value']}",
        reason=f"Project Application by {discord_username}",
        auto_archive_duration=AutoArchiveDuration.ONE_WEEK,
    )
    link = reverse("project_application_view", kwargs={"pk": application.id})
    link = f"https://apps.bikeaction.org{link}"
    message = await thread.send(
        f"{mention_role.mention} please review and vote with :white_check_mark: or :x:.\n\n"
        f"See discussion at https://discord.com/channels/{guild.id}/{discussion_thread.id}\n\n"
        f"You can also view the application online [here]({link}) after logging in."
    )
    await message.add_reaction(":white_check_mark:")
    await message.add_reaction(":x:")
    await discussion_thread.send("Project application has been sent for vote!")
    application.voting_thread_id = thread.id
    await application.asave()


async def _approve_new_project(
    project_application_id,
    project_channel_name,
    project_mentor_id,
    add_project_lead_role,
    project_lead_id,
):
    application = await ProjectApplication.objects.filter(id=project_application_id).afirst()

    await bot.login(settings.DISCORD_BOT_TOKEN)
    guild = await bot.fetch_guild(settings.NEW_PROJECT_REVIEW_DISCORD_GUILD_ID)
    discussion_thread = await guild.fetch_channel(application.thread_id)
    voting_thread = await guild.fetch_channel(application.voting_thread_id)

    actions = []

    if project_channel_name is not None:
        channel = await guild.create_text_channel(
            project_channel_name, category=settings.ACTIVE_PROJECT_CATEGORY_ID
        )
        application.channel_id = channel.id
        actions.append(f"Created channel `{project_channel_name}`")

    if project_mentor_id is not None:
        application.mentor_id = project_mentor_id
        mentor = await guild.fetch_member(project_mentor_id)
        actions.append(f"Assigned Mentor `{mentor}`")

    if add_project_lead_role:
        role = await guild.fetch_role(settings.ACTIVE_PROJECT_LEAD_ROLE_ID)
        project_lead = await guild.fetch_member(project_lead_id)
        await project_lead.add_role(role)
        actions.append(f"Assigned `{role.name}` role to `{project_lead}`")

    msg = f"Project \"{application.data['shortname']['value']}\" Approved!"
    if actions:
        msg += "\n\nActions Taken:\n"
    for action in actions:
        msg += f"- {action}\n"

    await discussion_thread.send(msg)
    await voting_thread.send(msg)

    application.approved = True
    await application.asave()


@shared_task
def add_new_project_message_and_thread(project_application_id):
    async_to_sync(_add_new_project_message_and_thread)(project_application_id)


@shared_task
def add_new_project_voting_message_and_thread(project_application_id):
    async_to_sync(_add_new_project_voting_message_and_thread)(project_application_id)


@shared_task
def approve_new_project(
    project_application_id,
    project_channel_name,
    project_mentor_id,
    add_project_lead_role,
    project_lead_id,
):
    async_to_sync(_approve_new_project)(
        project_application_id,
        project_channel_name,
        project_mentor_id,
        add_project_lead_role,
        project_lead_id,
    )
