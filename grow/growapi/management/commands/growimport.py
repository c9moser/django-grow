from pathlib import Path
from django.core.management.base import BaseCommand, CommandError  # noqa
from django.contrib.auth import get_user_model

from grow.growapi.utils.import_export import import_data


class Command(BaseCommand):
    help = "Import grow content"

    def add_arguments(self, parser):
        parser.add_argument("file", nargs=1, type=str)
        parser.add_argument("--username", type=str)
        parser.add_argument("--email", type=str)
        parser.add_argument("--moderator-username", type=str)
        parser.add_argument("--moderator-email", type=str)

    def handle(self, *args, **options):
        if not options['file']:
            raise CommandError("No file to import specified")

        filename = Path(options['file'][0]).resolve()
        if not filename:
            raise CommandError("No file given")
        if not filename.exists():
            raise CommandError("File \"{filename}\" does not exist!")

        UserModel = get_user_model()
        user = None
        if options['username']:
            try:
                user = UserModel.objects.get(username=options['username'])
            except UserModel.DoesNotExist:
                raise CommandError(f"No user with username \"{options['username']}\" exists!")
        elif options['email']:
            try:
                user = UserModel.objects.get(email=options['email'])
            except UserModel.DoesNotExist:
                raise CommandError(f"No user with email \"{options['email']}\" exists!")

        moderator = None
        if options['moderator_username']:
            try:
                moderator = UserModel.objects.get(username=options['moderator_username'])
            except UserModel.DoesNotExist:
                raise CommandError(
                    f"No user with username \"{options['moderator_username']}\" exists!"
                )
        elif options['moderator_email']:
            try:
                moderator = UserModel.objects.get(email=options['moderator_email'])
            except UserModel.DoesNotExist:
                raise CommandError(f"No user with email \"{options['moderator_email']}\" exists!")
        print(f"Importing from {filename} ...")

        import_data(filename=filename, user=user, moderator=moderator)
