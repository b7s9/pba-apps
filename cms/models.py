from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class HomePage(Page):
    body = RichTextField(blank=True)

    parent_page_types = ["wagtailcore.Page"]
    max_count_per_parent = 1
    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]


class CmsPage(Page):
    body = RichTextField(blank=True)

    parent_page_types = [HomePage]
    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]
