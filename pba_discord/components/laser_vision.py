import re

from django.core.cache import cache
from interactions import Extension, component_callback

from lazer.models import ViolationReport
from lazer.tasks import submit_violation_report_to_ppa
from lazer.utils import build_embed


class LaserVision(Extension):
    def __init__(self, bot):
        self.bot = bot

    APPROVE_BUTTON_ID_REGEX = re.compile(r"laser_violation_approve_(.*)")

    @component_callback(APPROVE_BUTTON_ID_REGEX)
    async def approve_callback(self, ctx):
        violation_id = ctx.custom_id.replace("laser_violation_approve_", "")
        with cache.lock(f"laser-violation-report-{violation_id}"):
            violation_report = (
                await ViolationReport.objects.filter(id=violation_id)
                .select_related("submission")
                .afirst()
            )
            if violation_report is None:
                await ctx.send("No violation report found!", ephemeral=True)
                await ctx.edit_origin(components=[])
                return

            if violation_report.submitted is not None:
                await ctx.send("Violation report already submitted!", ephemeral=True)
                await ctx.edit_origin(components=[])
                return

            submit_violation_report_to_ppa.delay(violation_report.id)

            embed = build_embed(violation_report)
            embed.description = f"**VIOLATION REPORT APPROVED by {ctx.member}**"
            await ctx.edit_origin(embeds=[embed], components=[])
            await ctx.send("Violation report approved and submitted!", ephemeral=True)

    REJECT_BUTTON_ID_REGEX = re.compile(r"laser_violation_reject_(.*)")

    @component_callback(REJECT_BUTTON_ID_REGEX)
    async def reject_callback(self, ctx):
        violation_id = ctx.custom_id.replace("laser_violation_reject_", "")
        with cache.lock(f"laser-violation-report-{violation_id}"):
            violation_report = (
                await ViolationReport.objects.filter(id=violation_id)
                .select_related("submission")
                .afirst()
            )
            if violation_report is None:
                await ctx.send("No violation report found!", ephemeral=True)
                await ctx.edit_origin(components=[])
                return

            if violation_report.submitted is not None:
                await ctx.send("Violation report already submitted!", ephemeral=True)
                await ctx.edit_origin(components=[])
                return

            embed = build_embed(violation_report)
            embed.description = f"**VIOLATION REPORT REJECTED by {ctx.member}**"
            await ctx.edit_origin(embeds=[embed], components=[])
            await ctx.send("Violation report rejected!", ephemeral=True)


def setup(bot):
    LaserVision(bot)
