from django.contrib.auth.models import Group


def make_user_groups(user):
    """
    Create groups for the user if they don't exist and add the user to those groups.

    :param user: The user for whom to create groups
    :type user: User
    """
    if not user.is_authenticated:
        return

    group_names = [
        'grow-member',
        f'grow-u{user.id}-grower',
        f'grow-u{user.id}-friends',
    ]

    for group_name in group_names:
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            print(f"Group '{group_name}' created.")
        else:
            print(f"Group '{group_name}' already exists.")
        user.groups.add(group)
