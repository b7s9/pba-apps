from asgiref.sync import async_to_sync
from celery import shared_task
from django.conf import settings
from django.contrib.gis.geos import Point
from mailchimp3 import MailChimp, helpers

from facets.utils import geocode_address
from pba_discord.bot import bot


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


@shared_task
def geocode_profile(profile_id):
    from profiles.models import Profile

    profile = Profile.objects.get(id=profile_id)

    if profile.street_address is not None:
        print(f"Geocoding {profile}")
        address = async_to_sync(geocode_address)(profile.street_address + " " + profile.zip_code)
        if address.address is not None and not address.address.startswith("Philadelphia"):
            print(f"Address found {address}")
            Profile.objects.filter(id=profile_id).update(
                location=Point(address.longitude, address.latitude)
            )
        else:
            print(f"No address found for {profile.street_address} {profile.zip_code}")
            Profile.objects.filter(id=profile_id).update(location=None)


@shared_task
def sync_to_mailchimp(profile_id):
    from profiles.models import Profile

    profile = Profile.objects.get(id=profile_id)

    status = "subscribed" if profile.newsletter_opt_in else "unsubscribed"

    mailchimp = MailChimp(mc_api=settings.MAILCHIMP_API_KEY)
    print("updating contact...")
    response = mailchimp.lists.members.create_or_update(
        settings.MAILCHIMP_AUDIENCE_ID,
        helpers.get_subscriber_hash(profile.user.email),
        {
            "email_address": profile.user.email,
            "status": status,
            "status_if_new": status,
            "merge_fields": {
                "FNAME": profile.user.first_name,
                "LNAME": profile.user.last_name,
            },
        },
    )
    Profile.objects.filter(id=profile_id).update(mailchimp_contact_id=response["id"])

    print("updating tags...")
    mailchimp.lists.members.tags.update(
        settings.MAILCHIMP_AUDIENCE_ID,
        helpers.get_subscriber_hash(profile.user.email),
        data={
            "tags": [
                {"name": "apps", "status": "active"},
            ]
        },
    )
