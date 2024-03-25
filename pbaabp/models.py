from functools import partial

import bleach
import cmarkgfm
from bleach.linkifier import LinkifyFilter
from cmarkgfm.cmark import Options as cmarkgfmOptions
from markdownfield.models import MarkdownField as _MarkdownField
from markdownfield.util import blacklist_link, format_link


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
