from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
    RawHTMLBlock,
    RichTextBlock,
    StructBlock,
)
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.images.fields import WagtailImageField
from wagtail.images.blocks import ImageBlock
from wagtail.models import Page


class AlignedParagraphBlock(StructBlock):
    """
    RichTextBlock that can be aligned.
    """

    alignment = ChoiceBlock(
        choices=[("left", "Left"), ("center", "Center"), ("right", "Right")],
        default="left",
    )
    paragraph = RichTextBlock()

    class Meta:
        template = "blocks/aligned_paragraph.html"


class CardBlock(StructBlock):
    """
    A card with a header, text, and image
    """

    image = ImageBlock()
    image_side = ChoiceBlock(
        choices=[("left", "Left"), ("right", "Right")],
        default="left",
    )
    header = CharBlock(required=False)
    text = RichTextBlock()

    class Meta:
        template = "blocks/card.html"


class HomepageCardBlock(StructBlock):
    """
    A card with a title, subtitle, and text
    """

    text_side = ChoiceBlock(
        choices=[("left", "Left"), ("right", "Right")],
        default="right",
    )
    title = CharBlock()
    subtitle = CharBlock()
    text = RichTextBlock()

    class Meta:
        template = "blocks/homepage_card.html"


_features = [
    "anchor-identifier",
    "h2",
    "h3",
    "h4",
    "bold",
    "italic",
    "ol",
    "ul",
    "hr",
    "link",
    "document-link",
    "image",
    "embed",
    "code",
    "blockquote",
]

table_options = {
    "editor": "text",
    "renderer": "html",
    "contextMenu": [
        "row_above",
        "row_below",
        "---------",
        "col_left",
        "col_right",
        "---------",
        "remove_row",
        "remove_col",
        "---------",
        "undo",
        "redo",
        "---------",
        "copy",
        "cut",
        "---------",
        "alignment",
    ],
}


class CmsStreamPage(Page):

    body = StreamField(
        [
            ("card", CardBlock(features=_features)),
            ("paragraph", AlignedParagraphBlock(features=_features)),
            ("html", RawHTMLBlock()),
            ("table", TableBlock(table_options=table_options)),
        ],
        use_json_field=True,
    )

    subpage_types = ["NavigationContainerPage", "CmsStreamPage"]

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]


class NavigationContainerPage(Page):
    """
    This page doesn't have HTML, and it works only to support hierarchical
    structure of the site.
    """

    class Meta:
        verbose_name = "Navigation Container Page"

    subpage_types = ["NavigationContainerPage", "CmsStreamPage"]


class HomePage(Page):

    body_background = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    body = StreamField(
      [
        ("homepagecard", HomepageCardBlock(features=_features)),
        ("paragraph", AlignedParagraphBlock(features=_features)),
        ("html", RawHTMLBlock()),
      ]
    )

    subpage_types = ["NavigationContainerPage", "CmsStreamPage"]
    max_count_per_parent = 1
    content_panels = Page.content_panels + [
        FieldPanel("body"),
        FieldPanel('body_background'),
    ]
