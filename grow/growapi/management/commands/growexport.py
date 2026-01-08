from django.core.management.base import BaseCommand
from grow.growapi.utils.import_export import export_data


class Command(BaseCommand):
    help = "Import grow content"

    def add_arguments(self, parser):
        parser.add_argument("file", nargs='?', type=str)
        parser.add_argument('--include-images',
                            action='store_true',
                            help='Include images in the export.')

    def handle(self, *args, **options):
        filename = options['file']
        if not filename:
            filename = None
        else:
            filename = filename

        if export_data(filename=filename, include_images=options['include_images']):
            if filename:
                print(f"Successfully exported grow data to \"{filename}\".")
            else:
                print("Successfully exported data to MEDIA_ROOT.")
