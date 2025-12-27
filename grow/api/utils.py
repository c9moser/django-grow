from pathlib import Path
import os
import json
import zipfile

from django.utils.timezone import now
from django.conf import settings as django_settings

from . import settings
from .models import Breeder, Strain, StrainImage

_strain_logo_archname_format = "breeder/strains/{breeder_slug}/{strain_slug}/logos/{basename}"
_strain_image_archname_format = "breeder/strains/{breeder_slug}/{strain_slug}/images/{basename}"


def export_data() -> bool:
    def export_strain(zfile: zipfile.ZipFile, strain: Strain) -> str:
        data = {
            'name': strain.name,
            'flowering_time_days': strain.flowering_time_days,
            'is_automatic': strain.is_automatic,
            'is_feminized': strain.is_feminized,
            'is_regular': strain.is_regular,
            'genetics': strain.genetics.value,
            'description_type': strain.description_type.value,
            'description': strain.description,
            'logo_url': strain.logo_url,
        }
        if strain.logo_image and os.path.exists(strain.logo_image.path):
            logo_arch_name = _strain_logo_archname_format.format(
                breeder_slug=strain.breeder.slug,
                strain_slug=strain.slug,
                basename=os.path.basename(strain.logo_image)
            )
            zf.write(strain.logo_image.path, logo_arch_name)
            data['logo_image'] = os.path.basename(strain.logo_image)

        for strain_image in strain.strain_images.all():
            strain_image = StrainImage()

            if not os.path.exists(strain_image.image.path):
                continue

            si_data = {
                'description_type': strain_image.description_type.value,
                'description': strain_image.description,
                'image': os.path.basename(strain_image.image.path),
            }
            si_archname = _strain_image_archname_format.format(
                breeder_slug=strain.breeder.slug(),
                strain_slug=strain.slug,
                basename=os.path.basename(strain_image.image.path),
            )
            zf.write(strain_image.image.path, si_archname)

            if not data['strain_images']:
                data['strain_images'] = [si_data]
            else:
                data['strain_images'].append(si_data)

        return data


    if not settings.GROW_EXPORTS_DIR.exists():
        os.makedirs(settings.GROW_EXPORTS_DIR)

    include_wiki = settings.getattr(django_settings, "INCLUDE_WIKI", False):
    if include_wiki:
        from tinywiki.utils import export_wiki_content

    timestamp = now()
    exports_file = Path(settings.GROW_EXPORTS_FILE_FORMAT.format(
        timestamp.strftime("%Y%m%d%H%M%S")
    )).resolve()

    if include_wiki:
        export_wiki_content("grow", exports_file, prefix="grow-")


    with zipfile.ZipFile(exports_file, "a") as zf:
        for breeder in Breeder.objects.all().order_by('slug'):
            breeder_data = {
                'slug': breeder.slug,
                'name': breeder.name,
                'breeder_url': breeder.breeder_url,
                'seedfinder_url': breeder.seedfinder_url,
                'description_type': breeder.description_type.value,
                'description': breeder.description,
                'logo_url': breeder.logo_url,
            }
            if breeder.logo_image and os.path.exists(breeder.logo_image.path):
                logo_arch_name = f"breeder/logos/{os.path.basename(breeder.logo_image.path)}"
                zf.write(breeder.logo_image.path, logo_arch_name)
                breeder_data['logo_image'] = logo_arch_name


            if breeder.strain_count > 0:
                if breeder_data['strains'] = dict(
                    (
                        (strain.slug, export_strain(strain))
                        for strain in breeder.strains.all().order_by('slug')
                    )
                )

            zf.writestr(f"breeder/{breeder.slug}.json",
                        json.dumps(breeder_data, ensure_ascii=False, indent=4))

    with open(settings.GROW_EXPORTS_VERSIONS_FILE, 'rt', encoding="utf-8") as vifile:
        exports = vifile.readlines()

    if len(exports) > (settings.GROW_EXPORTS_VERSIONS - 1):
        for ef_basename in exports[settings.GROW_EXPORTS_VERSIONS - 1:]:
            ef = settings.GROW_EXPORTS_DIR / ef_basename
            if os.path.isfile(ef):
                os.unlink(ef)

    exports = exports[settings.GROW_EXPORTS_VERSIONS - 1:]
    exports.insert(0, os.path.basename(exports_file))

    with open(settings.GROW_EXPORTS_VERSIONS_FILE, "wt", encoding="utf-8") as vofile:
        vofile.write('\n'.join(exports))

    return True


def import_data(filename: str | Path) -> bool:
    pass
