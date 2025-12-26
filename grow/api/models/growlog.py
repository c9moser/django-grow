"""
Growlog models
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings


from ..enums import (
    TextType,
    TEXT_CHOICES,
    PermissionType,
    PERMISSION_CHOICES,
)

from .strain import Strain
from .location import Location


GROWLOG_PERMISSION_TYPE = _("This determines who can view the grow log.")


class Growlog(models.Model):
    #: The key(slug) for the growlog
    #: The growlog is looked up by ${BASE_URL}/userid/slug
    key = models.SlugField(
        _("key"),
        max_length=255,
    )

    #: The name of the growlog
    name = models.CharField(
        _("name"),
        max_length=255
    )

    #: The desctiption of the growlog
    description = models.TextField(
        _("description"),
        default=""
    )

    #: The TextType of the growlog (default: Markdown).
    description_type_data = models.CharField(
        _("description type"),
        max_length=50,
        default="markdown",
        choices=TEXT_CHOICES,
        db_column="description_type")

    #: Personal Notes
    #:
    #: Personal notes are only displayed to the Grower himself/herself.
    notes = models.TextField(_("notes"),
                             blank=True,
                             null=True)
    #: The TextType of the personal notes (default: Markdown)
    notes_type_data = models.CharField(
        _("notes type"),
        max_length=50,
        default="markdown",
        choices=TEXT_CHOICES,
        db_column="notes_type"
    )

    #: The grower (creator) of the growlog.
    grower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='grow_logs',
        verbose_name=_("grower"),
    )
    #: The timestamp, when the growlog was started. (automatically created)
    started_at = models.DateTimeField(
        _("started at"),
        auto_now_add=True
    )

    #: When the seeds germinated
    germinated_at = models.DateField(
        _("germinated at"),
        blank=True,
        null=True
    )

    #: When cuttings where cut.
    cutted_at = models.DateField(
        _("Cutted at"),
        blank=True,
        null=True
    )

    #: When the flowering period was started
    flowering_at = models.DateField(
        _("flowering at"),
        blank=True,
        null=True
    )

    #: When the plants were hearvested.
    harvested_at = models.DateField(
        _("harvested at"),
        blank=True,
        null=True
    )

    #: When the grow was finished.
    #:
    #: When the growlog is finished, only the description can be edited.
    finished_at = models.DateTimeField(
        _("finished at"),
        blank=True,
        null=True
    )

    #: The permission data
    #:
    #: Use the `permission` property to set permissions.
    permission_data = models.CharField(
        _("permission"),
        max_length=50,
        default="private",
        choices=PERMISSION_CHOICES,
        db_column="permission")

    @property
    def description_type(self) -> TextType:
        """
        Get the TextType enum for the description type.
        """
        return TextType.from_string(self.description_type_data)

    @description_type.setter
    def description_type(self, text_type: TextType) -> None:
        """
        Set the description type using a TextType enum.
        """
        self.description_type_data = text_type.value

    @property
    def notes_type(self) -> TextType:
        """
        Get the TextType enum for the notes type.
        """
        return TextType.from_string(self.notes_type_data)

    @notes_type.setter
    def notes_type(self, text_type: TextType) -> None:
        """
        Set the notes type using a TextType enum.
        """
        self.notes_type_data = text_type.value

    @property
    def permission(self) -> PermissionType:
        """
        Get the GrowPermissionType enum for the grow log's permission.
        """
        return PermissionType.from_string(self.permission_data)

    @permission.setter
    def permission(self, permission: PermissionType) -> None:
        """
        Set the grow log's permission using a GrowPermissionType enum.
        """
        self.permission_data = permission.value

    @property
    def is_private(self) -> bool:
        """
        Check if the grow log is private.
        """
        return self.permission == PermissionType.PRIVATE

    @property
    def is_public(self) -> bool:
        """
        Check if the grow log is public.
        """
        return self.permission == PermissionType.PUBLIC

    @property
    def is_members_only(self) -> bool:
        """
        Check if the grow log is members only.
        """
        return self.permission == PermissionType.MEMBERS_ONLY

    @property
    def is_friends_only(self) -> bool:
        """
        Check if the grow log is friends only.
        """
        return self.permission == PermissionType.FRIENDS_ONLY

    @property
    def is_active(self) -> bool:
        """
        Check if the grow log is currently active (not finished).
        """
        return self.finished_at is None

    @property
    def is_harvested(self) -> bool:
        """
        Check if the grow log has been harvested.
        """
        return self.harvested_at is not None

    @property
    def is_germinated(self) -> bool:
        """
        Check if the grow log has been germinated.
        """
        return self.germinated_at is not None

    @property
    def is_cutted(self) -> bool:
        return self.cutted_at is not None

    @property
    def is_finished(self) -> bool:
        """
        Check if the grow log is finished.
        """
        return self.finished_at is not None

    @property
    def is_flowering(self) -> bool:
        """
        Check if the grow log is currently in flowering stage.
        """
        return self.flowering_at is not None and self.harvested_at is None

    @property
    def age_days(self) -> int:
        """
        Calculate the age of the grow log in days since germination.
        Returns 0 if germination date and cutted date is not set.
        """
        if not self.is_germinated and not self.is_cutted:
            return 0

        if self.is_cutted:
            delta = timezone.now().date() - self.germinated_at
        else:
            delta = timezone.now().date() - self.cutted_at

        return delta.days

    @property
    def age_weeks(self) -> int | None:
        """
        Calculate the age of the grow log in weeks since germination.
        Returns 0 if germination date is not set.
        """
        if not self.is_germinated:
            return None

        if self.age_days % 7 > 3:
            return (self.age_days // 7) + 1
        return self.age_days // 7

    @property
    def age_weeks_days(self) -> tuple[int, int] | None:
        """
        Calculate the age of the grow log in weeks and days since germination.
        Returns (0, 0) if germination date is not set.
        """
        if not self.is_germinated:
            return None

        weeks = self.age_days // 7
        days = self.age_days % 7
        return (weeks, days)

    @property
    def flowering_days(self) -> int:
        """
        Calculate the number of days since flowering started.
        Returns 0 if flowering date is not set.
        """
        if not self.is_flowering:
            return 0
        delta = timezone.now().date() - self.flowering_at
        return delta.days

    @property
    def flowering_weeks(self) -> int:
        """
        Calculate the number of weeks since flowering started.
        Returns 0 if flowering date is not set.
        """
        if not self.is_flowering:
            return 0
        if self.flowering_days % 7 > 3:
            return (self.flowering_days // 7) + 1
        return self.flowering_days // 7

    @property
    def flowering_weeks_days(self) -> tuple[int, int] | None:
        """
        Calculate the number of weeks and days since flowering started.
        Returns (0, 0) if flowering date is not set.
        """
        if not self.is_flowering:
            return None

        if not self.is_harvested:
            weeks = self.flowering_days // 7
            days = self.flowering_days % 7
        else:
            delta = self.harvested_at - self.flowering_at
            total_days = delta.days
            weeks = total_days // 7
            days = total_days % 7

        return (weeks, days)

    @property
    def days_grown(self) -> int:
        """
        Calculate the total number of days the grow log has been active.
        Returns 0 if germination date is not set.
        """
        if not self.is_germinated:
            return 0

        if not self.is_germinated:
            return 0

        end_date = self.harvested_at.date() if self.is_harvested else timezone.now().date()
        delta = end_date - self.germinated_at

        return delta.days

    @property
    def weeks_grown(self) -> int:
        """
        Calculate the total number of weeks the grow log has been active.
        Returns 0 if germination date is not set.
        """
        if not self.is_germinated:
            return 0

        if self.days_grown % 7 > 3:
            return (self.days_grown // 7) + 1
        return self.days_grown // 7

    @property
    def weeks_days_grown(self) -> tuple[int, int] | None:
        """
        Calculate the total number of weeks and days the grow log has been active.
        Returns (0, 0) if germination date is not set.
        """
        if not self.is_germinated:
            return None

        weeks = self.days_grown // 7
        days = self.days_grown % 7
        return (weeks, days)

    @property
    def strains(self) -> list[Strain]:
        """
        Get a list of strains associated with this grow log.
        """
        return [gs.strain for gs in self.growlog_strains.all()]

    @property
    def strain_count(self) -> int:
        """
        Get the number of different strains associated with this grow log.
        """
        return self.growlog_strains.count()

    @property
    def total_plants(self) -> int:
        """
        Get the total number of plants in this grow log.
        """
        return sum(*[gs.quantity for gs in self.growlog_strains.all()])

    @property
    def total_strains(self) -> int:
        """
        Get the total number of different strains in this grow log.
        """
        return self.growlog_strains.count()

    @property
    def total_entries(self) -> int:
        """
        Get the total number of entries in this grow log.
        """
        return self.entries.count()

    @property
    def total_images(self) -> int:
        """
        Get the total number of images in this grow log.
        """
        return sum(*[entry.images.count() for entry in self.entries.all()])

    @property
    def images(self) -> list['GrowlogEntryImage']:
        """
        Get a list of all images in this grow log.
        """
        images = []
        for entry in self.entries.all():
            images.extend(entry.images.all())
        return images

    @property
    def has_images(self) -> bool:
        """
        Check if the grow log has any images.
        """
        return self.total_images > 0

    @property
    def has_strains(self) -> bool:
        """
        Check if the grow log has any strains.
        """
        return self.strain_count > 0

    @property
    def has_entries(self) -> bool:
        """
        Check if the grow log has any entries.
        """
        return self.total_entries > 0

    @property
    def has_locations(self) -> bool:
        """
        Check if the grow log has any associated locations.
        """
        for entry in self.entries.all():
            if entry.location is not None:
                return True
        return False

    @property
    def locations(self) -> list[Location]:
        """
        Get a list of locations associated with this grow log.
        """
        if not self.has_locations:
            return []

        return list(set(entry.location for entry in self.entries.all()
                        if entry.location is not None))

    @property
    def last_location(self) -> Location | None:
        """
        Get the most recent location associated with this grow log.
        """
        entries_with_location = self.entries.filter(location__isnull=False).order_by('-timestamp')
        if not entries_with_location.exists():
            return None
        return entries_with_location.first().location

    class Meta:
        db_table = "grow_growlog"
        unique_together = [
            ('grower', 'key')
        ]


class GrowlogStrain(models.Model):
    #: The growlog for this strain
    grow_log = models.ForeignKey(
        Growlog,
        on_delete=models.CASCADE,
        related_name='growlog_strains',
        verbose_name=_("grow log")
    )

    #: The strain itself
    strain = models.ForeignKey(
        Strain,
        on_delete=models.CASCADE,
        related_name='growlog_strains',
        verbose_name=_("strain")
    )

    #: `True` if the strain is grown from seed.
    is_grown_from_seed = models.BooleanField(
        _("grown from seed"),
        default=True)

    #: Ǹumber of plants in this grow
    quantity = models.PositiveIntegerField(
        _("quantity"),
        default=1
    )

    class Meta:
        db_table = "grow_growlog_strains"
        unique_together = [
            ('grow_log', 'strain')
        ]


class GrowlogEntry(models.Model):
    #: The growlog this entry belongs to
    grow_log = models.ForeignKey(Growlog,
                                 on_delete=models.CASCADE,
                                 related_name='entries',
                                 verbose_name=_("grow log"))
    #: The timestamp of this entry
    timestamp = models.DateTimeField(_("timestamp"),
                                     auto_now_add=True)

    #: The content of the entry
    #:
    #: **Note:** Must contain a text
    content = models.TextField(_("content"))

    #: The text type of the content
    #:
    #: Use the `content_type` property to get/set the text type.
    content_type_data = models.CharField(
        _("content type"),
        max_length=50,
        default="markdown",
        choices=TEXT_CHOICES,
        db_column="content_type"
    )

    #: The location of the plants
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        related_name="growlog_entries",
        verbose_name=_("location"),
        blank=True,
        null=True
    )

    @property
    def content_type(self) -> TextType:
        """
        Get the TextType enum for the content type.
        """
        return TextType.from_string(self.content_type_data)

    @content_type.setter
    def content_type(self, text_type: TextType) -> None:
        """
        Set the content type using a TextType enum.
        """
        self.content_type_data = text_type.value

    @property
    def age_days(self) -> int:
        """
        Calculate the age of the grow log entry in days since the grow log's germination.
        Returns 0 if germination date is not set.
        """
        if not self.grow_log.is_germinated and not self.grow_log.is_cutted:
            return 0

        if self.grow_log.is_germinated:
            delta = self.timestamp.date() - self.grow_log.germinated_at
        else:
            delta = self.timestamp.date() - self.grow_log.is_cutted

        return delta.days

    @property
    def age_weeks(self) -> int | None:
        """
        Calculate the age of the grow log entry in weeks since the grow log's germination.
        Returns None if germination date is not set.
        """
        if not self.grow_log.is_germinated:
            return None

        if self.age_days % 7 > 3:
            return (self.age_days // 7) + 1
        return self.age_days // 7

    @property
    def age_weeks_days(self) -> tuple[int, int] | None:
        """
        Calculate the age of the grow log entry in weeks and days since the grow log's germination.
        Returns None if germination date is not set.
        """
        if not self.grow_log.is_germinated:
            return None

        weeks = self.age_days // 7
        days = self.age_days % 7
        return (weeks, days)

    @property
    def flowering_days(self) -> int:
        """
        Calculate the number of days since flowering started for the grow log entry.
        Returns 0 if flowering date is not set.
        """
        if not self.grow_log.is_flowering:
            return 0
        delta = self.timestamp.date() - self.grow_log.flowering_at
        return delta.days

    @property
    def flowering_weeks(self) -> int:
        """
        Calculate the number of weeks since flowering started for the grow log entry.
        Returns 0 if flowering date is not set.
        """
        if not self.grow_log.is_flowering:
            return 0
        if self.flowering_days % 7 > 3:
            return (self.flowering_days // 7) + 1
        return self.flowering_days // 7

    @property
    def flowering_weeks_days(self) -> tuple[int, int] | None:
        """
        Calculate the number of weeks and days since flowering started for the grow log entry.
        Returns None if flowering date is not set.
        """
        if not self.grow_log.is_flowering:
            return None

        if not self.grow_log.is_harvested:
            weeks = self.flowering_days // 7
            days = self.flowering_days % 7
        else:
            delta = self.grow_log.harvested_at - self.grow_log.flowering_at
            total_days = delta.days
            weeks = total_days // 7
            days = total_days % 7

        return (weeks, days)

    class Meta:
        db_table = "grow_growlogentry"
        ordering = ['-timestamp']


class GrowlogEntryImage(models.Model):
    """Images that are added to the growlog"""

    #: The entry
    growlog_entry = models.ForeignKey(
        GrowlogEntry,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("growlog entry")
    )

    # The image itself.
    image = models.ImageField(
        _("image"),
        upload_to='grow/growlog/entry_images/'
    )

    #: The description of the image
    description = models.CharField(
        _("description"),
        max_length=255,
        default=""
    )

    #: The description type
    description_type = models.CharField(
        _("description type"),
        max_length=50,
        default="markdown",
        choices=TEXT_CHOICES
    )

    #: `True` if it is a plant image
    is_plant_image = models.BooleanField(
        _("is plant image"),
        default=True
    )

    @property
    def age_days(self) -> int:
        """
        Calculate the age of the grow log entry image in days since the grow log's germination.
        Returns 0 if germination date is not set.
        """
        return self.growlog_entry.age_days

    @property
    def age_weeks(self) -> int | None:
        """
        Calculate the age of the grow log entry image in weeks since the grow log's germination.
        Returns None if germination date is not set.
        """
        return self.growlog_entry.age_weeks

    @property
    def age_weeks_days(self) -> tuple[int, int] | None:
        """
        Calculate the age of the grow log entry image in weeks and days since the grow log's germination.
        Returns None if germination date is not set.
        """
        return self.growlog_entry.age_weeks_days

    @property
    def flowering_days(self) -> int:
        """
        Calculate the number of days since flowering started for the grow log entry image.
        Returns 0 if flowering date is not set.
        """
        return self.growlog_entry.flowering_days

    @property
    def flowering_weeks(self) -> int:
        """
        Calculate the number of weeks since flowering started for the grow log entry image.
        Returns 0 if flowering date is not set.
        """
        return self.growlog_entry.flowering_weeks

    @property
    def flowering_weeks_days(self) -> tuple[int, int] | None:
        """
        Calculate the number of weeks and days since flowering started for the grow log entry image.
        Returns None if flowering date is not set.
        """
        return self.growlog_entry.flowering_weeks_days

    class Meta:
        db_table = "grow_growlogentry_image"
