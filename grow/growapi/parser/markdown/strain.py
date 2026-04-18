from markdown.inlinepatterns import InlineProcessor
from markdown.extensions import Extension
from xml import etree

from django.urls import reverse
from django.utils.translation import gettext as _
from grow.growapi.models import Breeder, Strain


class BreederInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        from grow.settings import USE_BOOTSTRAP

        css_classes = []
        if USE_BOOTSTRAP:
            css_classes.append('link-info')

        title = m.group(1)
        title = title.strip()
        breeder_slug = m.group(2)
        breeder_slug = breeder_slug.strip()

        breeder: Breeder = Breeder.objects.filter(slug=breeder_slug).first()
        if not breeder:
            el = etree.Element('mark')
            if title:
                el.text = title
            else:
                el.text = _("Breeder: <i>{breeder_slug}</i> not found!").format(breeder_slug=breeder_slug)
        else:
            if not title:
                title = breeder.name

            el = etree.Element(
                'a',
                href=reverse('grow:breeder-detail', kwargs={'slug': breeder.slug}),
                class_=" ".join(css_classes)
            )

        return el, m.start(0), m.end(0)


class StrainInlineProecessor(InlineProcessor):
    def handleMatch(self, m, data):
        from grow.settings import USE_BOOTSTRAP

        css_classes = []
        if USE_BOOTSTRAP:
            css_classes.append('link-info')

        title = m.group(1)
        title = title.strip()
        breeder_slug = m.group(2)
        breeder_slug = breeder_slug.strip()
        strain_slug = m.group(3)
        strain_slug = strain_slug.strip()

        el = etree.ElementTree.Element(
            'span',
        )

        try:
            strain: Strain = Strain.objects.get(breeder__slug=breeder_slug, slug=strain_slug)
        except Strain.DoesNotExist:
            mark = etree.ElementTree.Element('mark')
            mark.text = _("Strain: <i>{breeder_slug}/{strain_slug}</i> not found!").format(
                breeder_slug=breeder_slug,
                strain_slug=strain_slug
            )
            el.append(mark)
            strain = None
            return el, m.start(0), m.end(0)

        strain_link = etree.ElementTree.Element(
            'a',
            {
                'href': reverse(
                    'grow:strain-detail',
                    kwargs={
                        'breeder_slug': breeder_slug,
                        'slug': strain_slug
                    }
                ),
                'class': " ".join(css_classes),
            }
        )
        if title:
            strain_link.text = title
        else:
            strain_link.text = strain.name
        el.append(strain_link)
        by_breeder = etree.ElementTree.Element('span')
        by_breeder.text = _(" by ")
        el.append(by_breeder)
        breeder_link = etree.ElementTree.Element(
            'a',

            {
                'href': reverse(
                'grow:breeder-detail', kwargs={'slug': breeder_slug}),
                'class': " ".join(css_classes),
            },
        )
        breeder_link.text = strain.breeder.name
        el.append(breeder_link)

        return el, m.start(0), m.end(0)


class StrainExtension(Extension):
    def extendMarkdown(self, md):
        BREEDER_RE = r'\[(.*?)\]\s*\(breeder:(.*?)\)'
        STRAIN_RE = r'\[(.*?)\]\s*\(strain:(.*?)[\:/\.](.*?)\)'

        md.inlinePatterns.register(BreederInlineProcessor(BREEDER_RE, md), 'breeder', 175)
        md.inlinePatterns.register(StrainInlineProecessor(STRAIN_RE, md), 'strain', 175)
