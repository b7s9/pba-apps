from functools import partial

import bleach
import cmarkgfm
from bleach.linkifier import LinkifyFilter
from cmarkgfm.cmark import Options as cmarkgfmOptions
from django import forms
from django.contrib.postgres.fields import ArrayField
from django.dispatch import receiver
from easy_thumbnails.signals import saved_file
from markdownfield.models import MarkdownField as _MarkdownField
from markdownfield.util import blacklist_link, format_link

from pbaabp.tasks import generate_thumbnails


@receiver(saved_file)
def generate_thumbnails_async(sender, fieldfile, **kwargs):
    app_name = sender._meta.app_label
    object_name = sender._meta.object_name
    generate_thumbnails.delay(
        app_name=app_name,
        object_name=object_name,
        pk=fieldfile.instance.pk,
        field=fieldfile.field.name,
    )


class ChoiceArrayField(ArrayField):
    """
    A field that allows us to store an array of choices.

    Uses Django 1.9's postgres ArrayField
    and a MultipleChoiceField for its formfield.

    Usage:

        choices = ChoiceArrayField(models.CharField(max_length=..., choices=(...,)), default=[...])
    """

    def formfield(self, **kwargs):
        defaults = {
            "form_class": forms.MultipleChoiceField,
            "choices": self.base_field.choices,
            "widget": forms.CheckboxSelectMultiple,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)


class MarkdownField(_MarkdownField):

    def pre_save(self, model_instance, add):
        value = super().pre_save(model_instance, add)

        if not self.rendered_field:
            return value

        options = cmarkgfmOptions.CMARK_OPT_UNSAFE | cmarkgfmOptions.CMARK_OPT_GITHUB_PRE_LANG

        dirty = cmarkgfm.github_flavored_markdown_to_html(value, options=options)

        if self.validator.sanitize:
            if self.validator.linkify:
                cleaner = bleach.Cleaner(
                    tags=self.validator.allowed_tags,
                    attributes=self.validator.allowed_attrs,
                    css_sanitizer=self.validator.css_sanitizer,
                    filters=[partial(LinkifyFilter, callbacks=[format_link, blacklist_link])],
                )
            else:
                cleaner = bleach.Cleaner(
                    tags=self.validator.allowed_tags,
                    attributes=self.validator.allowed_attrs,
                    css_sanitizer=self.validator.css_sanitizer,
                )

            clean = cleaner.clean(dirty)
            setattr(model_instance, self.rendered_field, clean)
        else:
            # danger!
            setattr(model_instance, self.rendered_field, dirty)

        return value
