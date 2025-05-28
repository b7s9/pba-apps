from django.conf import settings
from interactions import Extension, SlashContext, slash_command

from projects.tasks import add_new_project_voting_message_and_thread


class ProjectApplications(Extension):
    SELECTION_CHANNEL = settings.NEIGHBORHOOD_SELECTION_DISCORD_CHANNEL_ID

    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="project",
        description="Project Application related commands",
        sub_cmd_name="vote",
        sub_cmd_description="Send project to board for vote",
    )
    async def project_vote(self, ctx: SlashContext):
        from projects.models import ProjectApplication

        project_application = await ProjectApplication.objects.filter(
            thread_id=ctx.channel_id
        ).afirst()
        if project_application is None:
            msg = "Sorry, cannot find an associated project in the current channel/thread."
        elif project_application.voting_thread_id:
            msg = "Project application already sent for vote."
        elif project_application.archived:
            msg = "Project already archived."
        elif project_application.approved:
            msg = "Project already approved."
        else:
            msg = "On it!"
            add_new_project_voting_message_and_thread.delay(project_application.id)
        await ctx.send(msg, ephemeral=True)

    @slash_command(
        name="project",
        description="Project Application related commands",
        sub_cmd_name="approve",
        sub_cmd_description="Approve a project after board vote",
    )
    async def project_approve(self, ctx: SlashContext):
        from projects.models import ProjectApplication

        project_application = await ProjectApplication.objects.filter(
            voting_thread_id=ctx.channel_id
        ).afirst()
        if project_application is None:
            msg = (
                "Sorry, cannot find an associated project application vote "
                "in the current channel/thread."
            )
        elif project_application.archived:
            msg = "Project already archived."
        elif project_application.approved:
            msg = "Project already approved."
        else:
            msg = "On it!"
        await ctx.send(msg, ephemeral=True)


def setup(bot):
    ProjectApplications(bot)
