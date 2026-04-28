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
from ..models import Breeder, Strain, StrainImage, StrainTranslation, BreederTranslation
from ..enums import TextType, StrainType


_breeder_logo_archname_format = "breeder/logos/{basename}"
_strain_logo_archname_format = "breeder/strains/{breeder_slug}/{strain_slug}/logos/{basename}"
_strain_image_archname_format = "breeder/strains/{breeder_slug}/{strain_slug}/images/{basename}"


def export_data(filename: str | Path | None, include_images: bool = False) -> bool:
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
            'is_discontinued': strain.is_discontinued,
            'genotype': strain.genotype.value,
            'description_type': strain.description_type.value,
            'description': strain.description,
            'logo_url': strain.logo_url,
        }
        if strain.logo_image and os.path.exists(strain.logo_image.path):
            logo_arch_name = _strain_logo_archname_format.format(
                breeder_slug=strain.breeder.slug,
                strain_slug=strain.slug,
                basename=os.path.basename(strain.logo_image.path)
            )
            zf.write(strain.logo_image.path, logo_arch_name)
            data['logo_image'] = os.path.basename(strain.logo_image.path)

        if include_images:
            for strain_image in strain.images.all():
                if not os.path.exists(strain_image.image.path):
                    continue

                si_data = {
                    'description_type': strain_image.description_type.value,
                    'description': strain_image.description,
                    'image': os.path.basename(strain_image.image.path),
                    'caption': strain_image.caption,
                    'uploader_name': (
                        strain_image.uploader_name
                        if strain_image.uploader_name
                        else strain_image.uploader.username if strain_image.uploader else "GROW"
                    )
                }
                si_archname = _strain_image_archname_format.format(
                    breeder_slug=strain.breeder.slug,
                    strain_slug=strain.slug,
                    basename=os.path.basename(strain_image.image.path),
                )
                zf.write(strain_image.image.path, si_archname)

                if 'images' not in data:
                    data['images'] = [si_data]
                else:
                    data['images'].append(si_data)

        if 'translations' not in data:
            data['translations'] = {}

        for strain_translation in strain.translations.all():
            data['translations'][strain_translation.language_code] = {
                'name': strain_translation.name,
                'seedfinder_url': strain_translation.seedfinder_url,
                'strain_url': strain_translation.strain_url,
                'description_type': strain_translation.description_type.value,
                'description': strain_translation.description,
            }

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
                    else breeder.created_by.username if breeder.created_by else "GROW"
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
            if 'translations' not in breeder_data:
                breeder_data['translations'] = {}

            for breeder_translation in breeder.translations.all():
                breeder_data['translations'][breeder_translation.language_code] = {
                    'name': breeder_translation.name,
                    'breeder_url': breeder_translation.breeder_url,
                    'seedfinder_url': breeder_translation.seedfinder_url,
                    'description_type': breeder_translation.description_type.value,
                    'description': breeder_translation.description,
                }

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


def import_data(filename: str | Path, user=None, moderator=None) -> bool:
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

        print(f"Importing breeder: {data['name']} ...")

        try:
            breeder = Breeder.objects.get(slug=data['slug'])
            breeder.name = data['name']
            breeder.description_type = TextType.from_string(data['description_type'])
            breeder.description = data['description']
            breeder.breeder_url = data['breeder_url']
            breeder.seedfinder_url = data['seedfinder_url']
            breeder.logo_url = data['logo_url']
            if not breeder.moderator and moderator:
                breeder.moderator = moderator
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
                moderator=moderator,
                created_by=get_creator_user(user, data['creator_name'])
            )

        if ('logo_url' not in data or not data['logo_url']) and 'logo_image' in data:
            if (not breeder.logo_image
                    or (os.path.basename(breeder.logo_image.path)
                        != os.path.basename(data['logo_image']))):
                zimage = _breeder_logo_archname_format.format(
                    basename=os.path.basename(data['logo_image']))
                img_path = Path("/tmp/") / os.path.basename(data['logo_image'])
                try:
                    with zarchive.open(zimage) as zfile:
                        with open(img_path, "wb") as img_tmp:
                            img_tmp.write(zfile.read())

                    with open(img_path, "rb") as img:
                        img_file = ImageFile(img, data['logo_image'])
                        breeder.logo_image = img_file
                        breeder.save()
                except Exception as ex:
                    print(f"Unable to import breeder.logo_image! ({str(ex)})")
                if os.path.exists(img_path):
                    os.unlink(img_path)

        for lang_code, translation_data in data.get('translations', {}).items():
            try:
                breeder_translation = breeder.translations.get(language_code=lang_code)
                breeder_translation.name = translation_data['name']
                breeder_translation.breeder_url = translation_data['breeder_url']
                breeder_translation.seedfinder_url = translation_data['seedfinder_url']
                breeder_translation.description_type = TextType.from_string(
                    translation_data['description_type']
                )
                breeder_translation.description = translation_data['description']
                breeder_translation.save()
            except BreederTranslation.DoesNotExist:
                BreederTranslation.objects.create(
                    breeder=breeder,
                    language_code=lang_code,
                    name=translation_data['name'],
                    breeder_url=translation_data['breeder_url'],
                    seedfinder_url=translation_data['seedfinder_url'],
                    description_type_data=TextType.from_string(
                        translation_data['description_type']
                    ).value,
                    description=translation_data['description'],
                )

        if 'strains' in data:
            for strain_slug, strain_data in data['strains'].items():
                import_strain(zarchive, breeder, strain_slug, strain_data)
    # ## END import_breeder()

    def import_strain(zarchive: zipfile.ZipFile, breeder: Breeder, slug: str, data: dict):
        print(f"\t{data['name']}")
        try:
            strain = breeder.strains.get(slug=slug)
            strain.name = data['name']
            strain.creator_name = data['creator_name']
            strain.description = data['description']
            strain.description_type = TextType.from_string(data['description_type'])
            strain.genotype = StrainType.from_string(data['genotype'])
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
                genotype=StrainType.from_string(data['genotype']),
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
                img_path = Path("/tmp/") / data['logo_image']

                try:
                    img_zpath = _strain_logo_archname_format.format(
                        breeder_slug=breeder.slug,
                        strain_slug=slug,
                        basename=data['logo_image'],
                    )

                    with zarchive.open(img_zpath) as img_file_data:
                        with open(img_path, "wb") as img_tmp:
                            img_tmp.write(img_file_data.read())

                    with open(img_path, "rb") as img_temp_file:
                        img_file = ImageFile(img_temp_file, data['logo_image'])
                        strain.logo_image = img_file
                        strain.save()
                except Exception as ex:
                    print(f"Unable to import strain.logo_image! ({str(ex)})")

                if os.path.exists(img_path):
                    os.unlink(img_path)

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
                    uploader=get_creator_user(user, data['uploader_name']),
                    description=data['description'],
                    description_type_data=TextType.from_string(data['description_type']).value,
                    image=img_file,
                )
                strain_images.append(db_image)

        for lang_code, translation_data in data.get('translations', {}).items():
            try:
                strain_translation = strain.translations.get(language_code=lang_code)
                strain_translation.name = translation_data['name']
                strain_translation.seedfinder_url = translation_data['seedfinder_url']
                strain_translation.strain_url = translation_data['strain_url']
                strain_translation.description_type = TextType.from_string(
                    translation_data['description_type']
                )
                strain_translation.description = translation_data['description']
                strain_translation.save()
            except StrainTranslation.DoesNotExist:
                StrainTranslation.objects.create(
                    strain=strain,
                    language_code=lang_code,
                    name=translation_data['name'],
                    seedfinder_url=translation_data['seedfinder_url'],
                    strain_url=translation_data['strain_url'],
                    description_type_data=TextType.from_string(
                        translation_data['description_type']
                    ).value,
                    description=translation_data['description'],
                )

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
