from celery import shared_task
from django.conf import settings

from lib.wordpress import WordPressAPI


@shared_task
def sync_to_wordpress(campaign_id):
    from campaigns.models import Campaign

    wordpress = WordPressAPI()
    wordpress.auth()

    campaign = Campaign.objects.get(id=campaign_id)

    if campaign.wordpress_id:
        print("updating...")
        _page = wordpress.update_page(
            page_id=campaign.wordpress_id,
            slug=campaign.slug,
            parent_id=settings.WP_CAMPAIGN_PAGE_ID,
            title=campaign.title,
            content=campaign.content_rendered,
            excerpt=campaign.description,
            status="publish" if campaign.status == Campaign.Status.ACTIVE else "draft",
        )
    else:
        print("creating...")
        _page = wordpress.create_page(
            slug=campaign.slug,
            parent_id=settings.WP_CAMPAIGN_PAGE_ID,
            title=campaign.title,
            content=campaign.content_rendered,
            excerpt=campaign.description,
            status="publish" if campaign.status == Campaign.Status.ACTIVE else "draft",
        )
        campaign.wordpress_id = _page["id"]
        campaign.save()
