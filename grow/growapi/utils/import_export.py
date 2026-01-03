from pathlib import Path
import os
import re
import json
import zipfile

from django.utils.timezone import now
from django.conf import settings as django_settings
from django.core.files.images import ImageFile
from django.contrib.auth import get_user_model
from ..exceptions import NotFileError, FileFormatError
from .. import settings
from ..models import Breeder, Strain, StrainImage
from ..enums import TextType, StrainType


_breeder_logo_archname_format = "breeder/logos/{basename}"
_strain_logo_archname_format = "breeder/strains/{breeder_slug}/{strain_slug}/logos/{basename}"
_strain_image_archname_format = "breeder/strains/{breeder_slug}/{strain_slug}/images/{basename}"


def export_data(filename: str | Path | None) -> bool:
    def export_strain(zfile: zipfile.ZipFile, strain: Strain) -> str:
        data = {
            'name': strain.name,
            'creator_name': (
                strain.creator_name
                if strain.creator_name
                else (
                    strain.created_by.username
                    if strain.created_by
                    else "GROW"
                )
            ),
            'strain_url': strain.strain_url,
            'seedfinder_url': strain.seedfinder_url,
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

        for strain_image in strain.images.all():
            if not os.path.exists(strain_image.image.path):
                continue

            si_data = {
                'description_type': strain_image.description_type.value,
                'description': strain_image.description,
                'image': os.path.basename(strain_image.image.path),
                'uploader_name': (
                    strain_image.uplaoder_name
                    if strain_image.uploader_name
                    else strain_image.uploaded_by.username
                )
            }
            si_archname = _strain_image_archname_format.format(
                breeder_slug=strain.breeder.slug(),
                strain_slug=strain.slug,
                basename=os.path.basename(strain_image.image.path),
            )
            zf.write(strain_image.image.path, si_archname)

            if not data['images']:
                data['images'] = [si_data]
            else:
                data['images'].append(si_data)

        return data
    # ## END export_strain()

    if not settings.GROW_EXPORTS_DIR.exists():
        os.makedirs(settings.GROW_EXPORTS_DIR)

    include_wiki = getattr(django_settings, "INCLUDE_WIKI", False)
    if include_wiki:
        from tinywiki.utils import export_wiki_content

    timestamp = now()

    if filename:
        exports_version = False
        if not isinstance(filename, Path):
            exports_file = Path(filename).resolve()
        else:
            exports_file = filename

    else:
        exports_version = True
        exports_file = Path(settings.GROW_EXPORTS_FILE_FORMAT.format(
            date=timestamp.strftime("%Y%m%d%H%M%S")
        )).resolve()

    if include_wiki:
        export_wiki_content("grow", exports_file, prefix="grow-")

    with zipfile.ZipFile(exports_file, "a",
                         compression=zipfile.ZIP_DEFLATED,
                         compresslevel=9) as zf:
        for breeder in Breeder.objects.all().order_by('slug'):
            breeder_data = {
                'slug': breeder.slug,
                'name': breeder.name,
                'creator_name': (
                    breeder.creator_name
                    if breeder.creator_name
                    else breeder.created_by.username
                ),
                'breeder_url': breeder.breeder_url,
                'seedfinder_url': breeder.seedfinder_url,
                'description_type': breeder.description_type.value,
                'description': breeder.description,
                'logo_url': breeder.logo_url,
            }
            if breeder.logo_image and os.path.exists(breeder.logo_image.path):
                logo_arch_name = _breeder_logo_archname_format.format(
                    basename=os.path.basename(breeder.logo_image.path)
                )
                zf.write(breeder.logo_image.path, logo_arch_name)
                breeder_data['logo_image'] = logo_arch_name

            if breeder.strain_count > 0:
                breeder_data['strains'] = dict(
                    (
                        (strain.slug, export_strain(zf, strain))
                        for strain in breeder.strains.all().order_by('slug')
                    )
                )

            zf.writestr(f"breeder/{breeder.slug}.json",
                        json.dumps(breeder_data, ensure_ascii=False, indent=4))

    if exports_version:
        if os.path.isfile(settings.GROW_EXPORTS_VERSIONS_FILE):
            with open(settings.GROW_EXPORTS_VERSIONS_FILE, 'rt', encoding="utf-8") as vifile:
                exports = vifile.readlines()
        else:
            exports = []

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


def import_data(filename: str | Path, user=None) -> bool:
    def get_creator_user(user, name: str | None):
        if not name:
            return user
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(username=name)
        except UserModel.DoesNotExist:
            return user

    def import_breeder(zarchive: zipfile.ZipFile, arcname: str):
        try:
            data = json.loads(zarchive.read(arcname).decode("utf-8"))
        except Exception:
            return False

        try:
            breeder = Breeder.objects.get(slug=data['slug'])
            breeder.name = data['name']
            breeder.description_type = TextType.from_string(data['description_type'])
            breeder.description = data['description']
            breeder.breeder_url = data['breeder_url']
            breeder.seedfinder_url = data['seedfinder_url']
            breeder.logo_url = data['logo_url']
            breeder.save()

        except Breeder.DoesNotExist:
            breeder = Breeder.objects.create(
                slug=data['slug'],
                name=data['name'],
                description_type_data=TextType.from_string(data['description_type']).value,
                description=data['description'],
                breeder_url=data['breeder_url'],
                seedfinder_url=data['seedfinder_url'],
                logo_url=data['logo_url'],
                created_by=get_creator_user(user, data['creator_name'])
            )

        if 'logo_image' in data:

            if (not breeder.logo_image
                    or os.path.basename(breeder.logo_image.path) != data['logo_image']):
                zimage = _breeder_logo_archname_format.format(basename=data['logo_image'])
                try:
                    zfile = zarchive.open(zimage)
                    img_file = ImageFile(zfile, data['logo_image'])
                    breeder.logo_image = img_file
                    breeder.save()
                except Exception as ex:
                    print(f"Unable to import breeder.logo_image! ({str(ex)})")

        if 'strains' in data:
            for strain_slug, strain_data in data['strains'].items():
                import_strain(zarchive, breeder, strain_slug, strain_data)
    # ## END import_breeder()

    def import_strain(zarchive: zipfile.ZipFile, breeder: Breeder, slug: str, data: dict):
        print(data['name'])
        try:
            strain = breeder.strains.get(slug=slug)
            strain.name = data['name']
            strain.creator_name = data['creator_name']
            strain.description = data['description']
            strain.description_type = TextType.from_string(data['description_type'])
            strain.genetics = StrainType.from_string(data['genetics'])
            strain.logo_url = data['logo_url']
            strain.strain_url = data['strain_url']
            strain.seedfinder_url = data['seedfinder_url']
            strain.is_automatic = data['is_automatic']
            strain.is_feminized = data['is_feminized']
            strain.is_regular = data['is_regular']
            strain.flowering_time_days = data['flowering_time_days']
            strain.save()
        except Strain.DoesNotExist:
            strain = Strain.objects.create(
                breeder=breeder,
                created_by=get_creator_user(user, data['creator_name']),
                creator_name=data['creator_name'],
                description=data['description'],
                description_type_data=TextType.from_string(data['description_type']).value,
                flowering_time_days=data['flowering_time_days'],
                genetics=StrainType.from_string(data['genetics']),
                is_automatic=data['is_automatic'],
                is_feminized=data['is_feminized'],
                is_regular=data['is_regular'],
                logo_url=data['logo_url'],
                name=data['name'],
                seedfinder_url=data['seedfinder_url'],
                slug=slug,
                strain_url=data['strain_url'],
            )

        if 'logo_image' in data:
            if (not strain.logo_image
                    or os.path.basename(strain.logo_image) != data['logo_image']):
                try:
                    img_zpath = _strain_logo_archname_format.format(
                        breeder_slug=breeder.slug,
                        strain_slug=slug,
                        basename=['logo_image'],
                    )
                    img_file = ImageFile(zarchive.open(img_zpath), data['logo_image'])
                    strain.logo_image = img_file
                    strain.save()
                except Exception as ex:
                    print(f"Unable to import strain.logo_image! ({str(ex)})")

        # import StrainImage
        if 'strain_images' in data:
            strain_images = list(strain.images.all())
            for image in data['strain_images']:
                image_found = False
                for db_image in strain_images:
                    if os.path.basename(db_image.image.path) == image['image']:
                        image_found = True
                        break
                if image_found:
                    continue
                img_file = ImageFile(
                    _strain_image_archname_format.format(
                        breeder_slug=breeder.slug,
                        strain_slug=slug,
                        basename=image['image']
                    )
                )
                db_image = StrainImage.objects.create(
                    strain=strain,
                    uploader_name=data['uploader_name'],
                    uploaded_by=get_creator_user(user, data['uploader_name']),
                    description=data['description'],
                    description_type_data=TextType.from_string(data['description_type']).value,
                    image=img_file,
                )
                strain_images.append(db_image)
    # ## END import_strain()

    if not isinstance(str, Path):
        filename = Path(filename)

    if not filename.exists():
        raise FileNotFoundError(f"File \"{filename}\" not found!")
    if not filename.is_file():
        raise NotFileError(f"\"{filename}\" os not a file!")
    if not zipfile.is_zipfile(filename):
        raise FileFormatError(f"\"{filename}\" if not a zip file!")

    with zipfile.ZipFile(filename, "r") as zf:
        zcontent = zf.namelist()

    include_wiki = getattr(django_settings, "INCLUDE_WIKI", False)
    if include_wiki:
        from tinywiki.utils import (
            import_builtin_pages_from_zip,
            import_builtin_images_from_zip,
        )
        if "pages.json" in zcontent:
            import_builtin_pages_from_zip(filename, user)
        if "images.json" in zcontent:
            import_builtin_images_from_zip(filename, user)

    breeder_pattern = re.compile("^breeder/[a-zA-Z0-9][-_a-zA-Z0-9]*.json$")
    with zipfile.ZipFile(filename, "r") as zf:
        for zfile in zcontent:
            if re.match(breeder_pattern, zfile):
                import_breeder(zf, zfile)
