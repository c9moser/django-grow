from django.core.management.base import BaseCommand
from grow.api.utils.import_export import export_data


class Command(BaseCommand):
    help = "Import grow content"

    def add_arguments(self, parser):
        parser.add_argument("file", nargs=1, type=str)

    def handle(self, *args, **options):
        filename = options['file']
        if not filename:
            filename = None
        else:
            filename = filename[0]

        if export_data(filename=filename):
            if filename:
                print(f"Successfully exported grow data to \"{filename}\".")
            else:
                print("Successfully exported data to MEDIA_ROOT.")
