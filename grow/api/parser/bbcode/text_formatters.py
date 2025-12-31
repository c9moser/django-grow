# from django_project.settings import STATIC_URL
from django.urls import reverse
# from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from ... import settings
from ... import models


def render_url(tag_name: str, value, options, parent, context) -> str:
    try:
        url = options['url']
    except KeyError:
        url = value

    if not url.startswith('/') and '://' not in url:
        url = "http://" + url

    if settings.USE_BOOTSTRAP:
        if ['noicon in options']:
            return f"<a href=\"{url}\" referrer-policy=\"no-referrer\" rel=\"noreferrer noopener\">{value}</a>"  # noqa: E501
        return f"<a href=\"{url}\" class=\"icon-link icon-link-hover\" referrer-policy=\"no-referrer\" rel=\"noreferrer noopener\">{value}<svg class=\"bi\"><use xlink:href=\"{settings.settings.STATIC_URL + 'tinywiki/icons/bootstrap-icons.svg'}#box-arrow-up-right\"></use></svg></a>"  # noqa: E501
    return f"<a href=\"{url}\" referrer-policy=\"no-referrer\" rel=\"noreferrer noopener\">{value}</a>"  # noqa: E501


def render_wiki_url(tag_name: str, value, options, parent, context) -> str:
    if tag_name in options:
        url = reverse("tinywiki:page", kwargs={'slug': options[tag_name]})
        slug = options[tag_name]
        try:
            page = models.Page.objects.get(slug=slug)
        except models.Page.DoesNotExist:
            page = None

    else:
        url = reverse('tinywiki:home')
        slug = None

    if settings.USE_BOOTSTRAP:
        href = settings.settings.STATIC_URL+"tinywiki/icons/bootstrap-icons.svg"
        if page:
            if page.slug.startswith('tw-'):
                svg = "journal"
            elif page.slug:
                svg = "book"
        else:
            svg = href + "file-earmark-x"
        return f"<a href=\"{url}\" class=\"icon-link icon-link-hover\">{value}<svg class=\"bi\"><use xlink:href=\"{href}#{svg}\"></use></svg></a>"  # noqa: E501
    return f"<a href=\"{url}\">{value}</a>"


def render_wiki_link(tag_name: str, value, options, parent, context):
    if tag_name in options:
        slug = options[tag_name]
        print("slug", slug)
        try:
            page = models.Page.objects.get(slug=slug)
            title = page.title
            if slug.startswith('tw-'):
                svg = "journal"
            else:
                svg = "book"
        except models.Page.DoesNotExist:
            page = None
            title = _("Page not found")
            svg = "file-earmark-x"
        url = reverse("tinywiki:page", kwargs={'slug': slug})
    else:
        slug = None
        title = _("Home")
        url = reverse("tinywiki:home")
        svg = "house"

    if settings.USE_BOOTSTRAP:
        href = settings.settings.STATIC_URL + "tinywiki/icons/bootstrap-icons.svg"
        return f"<a href=\"{url}\" class=\"icon-link icon-link-hover\">{title}<svg class=\"bi\"><use xlink:href=\"{href}#{svg}\"></use></svg></a>"  # noqa: E501
    return f"<a href=\"{url}\">{value}</a>"


def render_codeblock(tag_name: str, value, options, parent, context) -> str:
    if tag_name in options:
        return f"<pre style=\"overflow-x:auto;\"><code class=\"language-{options[tag_name]}\">{value}</code></pre>"  # noqa: E501
    return f"<pre style=\"overflow-x:auto;\"><code>{value}</code></pre>"


def render_ordered_list(tag_name: str, value, options, parent, context) -> str:
    return f"<ol>{value}</ol>"


def render_unordered_list(tag_name: str, value, options, parent, context) -> str:  # noqa: E501
    return f"<ul>{value}</ul>"


def render_list_item(tag_name: str, value, options, parent, context) -> str:
    return f"<li>{value}</li>"


def render_paragraph(tag_name: str, value, options, parent, context) -> str:
    if settings.USE_BOOTSTRAP:
        return f"<p style=\"text-align:justify;\">{value}</p>"
    return f"<p>{value}</p>"


def render_image(tag_name: str, value, options, parent, context) -> str:
    if tag_name not in options:
        return ""

    if 'alt' in options:
        alt = options['alt']
    else:
        alt = ""

    if settings.USE_BOOTSTRAP:
        classes = ["img-fluid", "figure-img", "rounded"]
        fig_classes = ["figure", "my-1"]
        styles = []
        fig_styles = []
    else:
        styles = ["max-width:100%;"]
        classes = []
        fig_classes = []
        fig_styles = []

    if 'width' in options:
        _w = options['width']
        if _w.endswith('px') or _w.endswith('em') or _w.endswith('rem'):
            fig_styles.append(f"width:{_w};")
        else:
            if _w.endswith('%'):
                _w = _w[:-1]
            if _w.isdigit():
                _w = int(_w)
                if _w > 100:
                    _w = 100
                if settings.USE_BOOTSTRAP:
                    if 1 < int(_w) <= 25:
                        width = 25
                    else:
                        width = ((_w // 25) * 25)
                    fig_classes.append(f'w-{width}')
                else:
                    fig_styles.append(f"width:{_w}%;")
    if 'height' in options:
        _h = options['width']
        if _h.endswith('px') or _h.endswith('em') or _h.endswith('rem'):
            fig_styles.append(f"height:{_h};")
        else:
            if _h.endswith('%'):
                _h = _h[:-1]
            if _h.isdigit():
                _h = int(_w)
                if _h > 100:
                    _h = 100
                if settings.USE_BOOTSTRAP:
                    if 1 < int(_h) <= 25:
                        height = 25
                    else:
                        height = ((_h // 25) * 25)
                        if height > 100:
                            height = 100

                    fig_classes.append(f'h-{height}')
                else:
                    fig_styles.append(f"height:{_h}%;")

    if "position" in options:
        pos = options['position']
        if settings.USE_BOOTSTRAP:
            if pos == "left" or pos == "start":
                fig_classes += ["float-start", "me-2"]
                classes += ["float-start", "me-2"]
            elif pos == "right" or pos == "end":
                fig_classes += ["float-end", "ms-2"]
                classes += ["float-end", "ms-2"]
            elif pos == "center":
                fig_classes += ["mx-auto", "d-block"]
                classes += ["mx-auto", "d-block"]

    if styles:
        style = f'style=\"{" ".join(styles)}\"'
    else:
        style = ""

    if fig_styles:
        fig_style = f'style="{" ".join(fig_styles)}"'
    else:
        fig_style = ""
    if settings.USE_BOOTSTRAP:
        return f'<figure class="{" ".join(fig_classes)} {fig_style}"><img src="{options[tag_name]}" class="{" ".join(classes)}" alt="{alt}" {style}><figcaption class="figure-caption text-end">{value}</figcaption></figure>'  # noqa: E501
    else:
        return f'<figure {fig_style}><img src="{options[tag_name]}" {style}><figcaption>{value}</figcaption></figure>'  # noqa: E501


def render_wiki_image(tag_name: str, value, options, parent, context):
    if tag_name not in options:
        return ""

    try:
        image = models.Image.objects.get(slug=options[tag_name])
    except models.Image.DoesNotExist:
        return ""

    if settings.USE_BOOTSTRAP:
        classes = ["img-fluid", "figure-img", "rounded"]
        fig_classes = ["figure", "my-1"]
        styles = []
        fig_styles = []
    else:
        styles = ["max-width:100%;"]
        classes = []
        fig_classes = []
        fig_styles = []

    if 'width' in options:
        _w = options['width']
        if _w.endswith('px') or _w.endswith('em') or _w.endswith('rem'):
            fig_styles.append(f"width:{_w};")
        else:
            if _w.endswith('%'):
                _w = _w[:-1]
            if _w.isdigit():
                _w = int(_w)
                if _w > 100:
                    _w = 100
                if settings.USE_BOOTSTRAP:
                    if 1 < int(_w) <= 25:
                        width = 25
                    else:
                        width = ((_w // 25) * 25)
                    fig_classes.append(f'w-{width}')
                else:
                    fig_styles.append(f"width:{_w}%;")
    if 'height' in options:
        _h = options['width']
        if _h.endswith('px') or _h.endswith('em') or _h.endswith('rem'):
            fig_styles.append(f"height:{_h};")
        else:
            if _h.endswith('%'):
                _h = _h[:-1]
            if _h.isdigit():
                _h = int(_w)
                if _h > 100:
                    _h = 100
                if settings.USE_BOOTSTRAP:
                    if 1 < int(_h) <= 25:
                        height = 25
                    else:
                        height = ((_h // 25) * 25)
                        if height > 100:
                            height = 100

                    fig_classes.append(f'h-{height}')
                else:
                    fig_styles.append(f"height:{_h}%;")

    if "position" in options:
        pos = options['position']
        if settings.USE_BOOTSTRAP:
            if pos == "left" or pos == "start":
                fig_classes += ["float-start", "me-2"]
            elif pos == "right" or pos == "end":
                fig_classes += ["float-end", "ms-2"]
            elif pos == "center":
                fig_classes += ["mx-auto", "d-block"]

    if styles:
        style = f"style=\"{' '.join(styles)}\""
    else:
        style = ""

    if fig_styles:
        fig_style = f'style="{" ".join(fig_styles)}"'
    else:
        fig_style = ""

    if settings.USE_BOOTSTRAP:
        return f'<figure class="{" ".join(fig_classes)}" {fig_style}><img src="{image.image.url}" alt="{image.alt}" class="{" ".join(classes)}" {style}><figcaption class="figure-caption text-end">{image.description_html}</figcaption></figure>'  # noqa: E501
    else:
        return f'<figure {fig_style}><img src="{image.image.url}" alt="{image.alt}" {style}><figcaption>{image.description}</figcaption></figure>'  # noqa: E501


def render_table(tag_name: str, value, options, parent, context) -> str:
    if settings.USE_BOOTSTRAP:
        classes = ["table"]
        if "bordered" in options:
            if options["bordered"] not in ("0", "n", "no", "false", "off"):
                classes.append("table-bordered")
            if options["bordered"] in (
                        "primary",
                        "secondary",
                        "info",
                        "warning",
                        "danger",
                        "success",
                        "light",
                        "dark"
                    ):
                classes.append(f"border-{options['bordered']}")

        if tag_name in options:
            if options[tag_name] in (
                        "primary",
                        "secondary",
                        "info",
                        "warning",
                        "danger",
                        "success",
                        "light",
                        "dark"
                    ):
                classes.append(f"table-{options[tag_name]}")

        return f"<table class=\"{' '.join(classes)}\">{value}</table>"

    return f"<table>{value}</table>"


def render_table_row(tag_name: str, value, options, parent, context) -> str:
    classes = []
    if settings.USE_BOOTSTRAP:
        if tag_name in options:
            if options[tag_name] in (
                        "primary",
                        "secondary",
                        "info",
                        "warning",
                        "danger",
                        "success",
                        "light",
                        "dark"
                    ):
                classes.append(f"table-{options[tag_name]}")
    class_attr = f"class=\"{' '.join(classes)}\"" if classes else ""
    return f"<tr {class_attr}>{value}</tr>"


def render_table_header(tag_name: str, value, options, parent, context) -> str:
    extra_attributes = []
    classes = []
    if "colspan" in options:
        extra_attributes.append(f"colspan=\"{options['colspan']}\"")
    if "rowspan" in options:
        extra_attributes.append(f"rowspan=\"{options['rowspan']}\"")
    if settings.USE_BOOTSTRAP:
        if tag_name in options:
            if options[tag_name] in (
                        "primary",
                        "secondary",
                        "info",
                        "warning",
                        "danger",
                        "success",
                        "light",
                        "dark"
                    ):
                classes.append(f"table-{options[tag_name]}")
    class_attr = f"class=\"{' '.join(classes)}\"" if classes else ""
    return f"<th {class_attr} {' '.join(extra_attributes)}>{value}</th>"


def render_table_data(tag_name: str, value, options, parent, context) -> str:
    extra_attributes = []
    classes = []
    if "colspan" in options:
        extra_attributes.append(f"colspan=\"{options['colspan']}\"")
    if "rowspan" in options:
        extra_attributes.append(f"rowspan=\"{options['rowspan']}\"")
    if settings.USE_BOOTSTRAP:
        if tag_name in options:
            if options[tag_name] in (
                        "primary",
                        "secondary",
                        "info",
                        "warning",
                        "danger",
                        "success",
                        "light",
                        "dark"
                    ):
                classes.append(f"table-{options[tag_name]}")
    class_attr = f"class=\"{' '.join(classes)}\"" if classes else ""
    return f"<td {class_attr} {' '.join(extra_attributes)}>{value}</td>"


def render_youtube_video(tag_name: str, value, options, parent, context):
    if tag_name not in options:
        return ""

    if settings.USE_BOOTSTRAP:
        styles = []
        classes = ["embed-responsive-item", "w-100"]
        div_classes = [
            "embed-responsive",
            "my-1",
        ]
        div_styles = []
    else:
        styles = ["max-width:100%;"]
        classes = []
        div_classes = []
        div_styles = []

    if 'width' in options:
        _w = options['width']
        if _w.endswith('px') or _w.endswith('em') or _w.endswith('rem'):
            if settings.USE_BOOTSTRAP:
                div_styles.append(f"width:{_w};")
                styles.append(f"width:{_w};")
        else:
            if _w.endswith('%'):
                _w = _w[:-1]
            if _w.isdigit():
                _w = int(_w)
                if _w > 100:
                    _w = 100
                if settings.USE_BOOTSTRAP:
                    if 1 < int(_w) <= 25:
                        width = 25
                    else:
                        width = ((_w // 25) * 25)
                    div_classes.append(f'w-{width}')
                else:
                    styles.append(f"width:{_w}%;")
    if 'height' in options:
        _h = options['width']
        if _h.endswith('px') or _h.endswith('em') or _h.endswith('rem'):
            if settings.USE_BOOTSTRAP:
                div_styles.append(f"height:{_h};")
            else:
                styles.append(f"height:{_h};")
        else:
            if _h.endswith('%'):
                _h = _h[:-1]
            if _h.isdigit():
                _h = int(_w)
                if _h > 100:
                    _h = 100
                if settings.USE_BOOTSTRAP:
                    if 1 < int(_h) <= 25:
                        height = 25
                    else:
                        height = ((_h // 25) * 25)
                        if height > 100:
                            height = 100

                    div_classes.append(f'h-{height}')
                else:
                    styles.append(f"height:{_h}%;")

    if "position" in options:
        pos = options['position']
        if settings.USE_BOOTSTRAP:
            if pos == "left" or pos == "start":
                div_classes += ["float-start", "me-2"]
                # classes += ["float-start","me-2"]
            elif pos == "right" or pos == "end":
                div_classes += ["float-end", "ms-2"]
                # classes += ["float-end", "ms-2"]
            elif pos == "center":
                div_classes += ["mx-auto", "d-block"]
                # classes += ["mx-auto", "d-block"]

    # if styles:
    #    style = f"style=\"{' '.join(styles)}\""
    # else:
    #    style = ""

    if div_styles:
        div_style = f'style="{"".join(div_styles)}"'
    else:
        div_style = ""
    if settings.USE_BOOTSTRAP:
        return f"""<div class=""{' '.join(div_classes)}" {div_style}>
    <iframe class="{' '.join(classes)}" src="https://www.youtube.com/embgit ed/{options[tag_name]}?rel=0" allowfullscreen></iframe>
</div>"""  # noqa: E501
    else:
        return f'<div {div_style}><iframe src="https://www.youtube.com/embed/{options[tag_name]}?rel=0" allowfullscreen></iframe></div>'  # noqa: E501
