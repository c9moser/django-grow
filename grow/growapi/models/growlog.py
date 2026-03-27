"""
Growlog models
"""

from datetime import date

from django.db import models
from django.utils.safestring import SafeString
from django.utils.translation import gettext_lazy as _, gettext, ngettext
from django.utils import timezone
from django.conf import settings

from ..enums import (
    TextType,
    TEXT_CHOICES,
    PermissionType,
    PERMISSION_CHOICES,
    GrowlogStatus,
)

from .strain import Strain
from .location import Location


GROWLOG_PERMISSION_TYPE = _("This determines who can view the grow log.")


class Growlog(models.Model):
    #: The name of the growlog
    name = models.CharField(
        _("name"),
        max_length=255,
    )

    #: The desctiption of the growlog
    description = models.TextField(
        _("description"),
        default=""
    )

    @property
    def description_html(self) -> str:
        """
        Returns the HTML representation of the description.
        """
        if self.description:
            if self.description_type == TextType.MARKDOWN:
                from grow.growapi.parser.markdown import render_description_markdown
                return render_description_markdown(self.description)
            elif self.description_type == TextType.BBCODE:
                from grow.growapi.parser.bbcode import render_description_bbcode
                return render_description_bbcode(self.description)
            else:
                return self.description
        return ""

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
    notes = models.TextField(_("personal notes"),
                             blank=True,
                             null=True)

    @property
    def notes_html(self) -> str:
        """
        Returns the HTML representation of the personal notes.
        """
        if self.notes:
            if self.notes_type == TextType.MARKDOWN:
                from grow.growapi.parser.markdown import render_description_markdown
                return render_description_markdown(self.notes)
            elif self.notes_type == TextType.BBCODE:
                from grow.growapi.parser.bbcode import render_description_bbcode
                return render_description_bbcode(self.notes)
            else:
                return self.notes
        return ""

    #: The TextType of the personal notes (default: Markdown)
    notes_type_data = models.CharField(
        _("personal notes type"),
        max_length=50,
        default="markdown",
        choices=TEXT_CHOICES,
        db_column="notes_type"
    )

    #: The grower (creator) of the growlog.
    grower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='growlogs',
        verbose_name=_("grower"),
    )
    #: The timestamp, when the growlog was started. (automatically created)
    started_at = models.DateTimeField(
        _("started at"),
        auto_now_add=True
    )

    #: When the seeds germinated
    germinating_at = models.DateField(
        _("germinating at"),
        blank=True,
        null=True
    )

    vegetative_at = models.DateField(
        _("vegetative at"),
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

    updated_at = models.DateTimeField(
        _("updated at"),
        auto_now=True
    )

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
    def is_germinating(self) -> bool:
        """
        Check if the grow log has been germinated.
        """
        return (self.germinating_at is not None
                and not self.cutted_at
                and not self.vegetative_at
                and not self.flowering_at)

    @property
    def is_germintated(self) -> bool:
        """
        Check if the seeds have germinated.

        :return: _description_
        :rtype: bool
        """
        return (self.germinating_at and not self.cutted_at
                and (self.vegetative_at or self.flowering_at))

    @property
    def is_vegetative(self) -> bool:
        """
        Check if the grow log is in vegetative stage.
        """
        return self.vegetative_at is not None and not self.flowering_at and not self.finished_at

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
        if not self.is_germintated and not self.is_cutted:
            return 0

        if self.germinating_at:
            if self.finished_at:
                return self.finished_at.date() - self.germinating_at
            else:
                return date.today() - self.germinating_at
        elif self.cutted_at:
            if self.finished_at:
                return self.finished_at.date() - self.cutted_at
            else:
                return date.today() - self.cutted_at

        if self.finished_at:
            delta = self.finished_at.date() - self.germinating_at
        else:
            delta = timezone.now().date() - self.germinating_at

        return delta.days

    @property
    def germinating_days(self):
        """
        Calculate the number of days since germination started.
        Returns 0 if germination date is not set.
        """
        if not self.germinating_at:
            return 0

        if self.vegetative_at is not None:
            delta = self.vegetative_at - self.germinating_at
        elif self.flowering_at is not None:
            delta = self.flowering_at - self.germinating_at
        elif self.harvested_at is not None:
            delta = self.harvested_at - self.germinating_at
        elif self.finished_at is not None:
            delta = self.finished_at.date() - self.germinating_at
        else:
            delta = timezone.now().date() - self.germinating_at
        return delta.days

    @property
    def germinating_weeks(self) -> int:
        """
        Calculate the number of weeks since germination started.
        Returns 0 if germination date is not set.
        """
        if not self.germinating_at:
            return 0
        if self.germinating_days % 7 > 3:
            return (self.germinating_days // 7) + 1
        return self.germinating_days // 7

    @property
    def germinating_weeks_days(self) -> tuple[int, int] | None:
        """
        Calculate the number of weeks and days since germination started.
        Returns (0, 0) if germination date is not set.
        """
        if not self.germinating_at:
            return None

        weeks = self.germinating_days // 7
        days = self.germinating_days % 7
        return (weeks, days)

    @property
    def germinating_display(self):
        """
        Get a human-readable string representation of the germination duration.
        """
        weeks_days = self.germinating_weeks_days
        if weeks_days is None:
            return gettext("Not germinated")

        weeks, days = weeks_days

        parts = []
        if weeks > 0:
            parts.append(ngettext("{n} week", "{n} weeks", weeks).format(n=weeks))
        if days > 0:
            parts.append(ngettext("{n} day", "{n} days", days).format(n=days))

        if parts:
            return ", ".join(parts)

        return gettext("0 days")

    @property
    def rooting_days(self) -> int:
        if not self.cutted_at:
            return 0

        if self.vegetative_at is not None:
            delta = self.vegetative_at - self.cutted_at
        elif self.flowering_at is not None:
            delta = self.flowering_at - self.cutted_at
        elif self.harvested_at is not None:
            delta = self.harvested_at - self.cutted_at
        elif self.finished_at is not None:
            delta = self.finished_at - self.cutted_at
        else:
            delta = timezone.now().date() - self.cutted_at
        return delta.days

    @property
    def rooting_weeks(self) -> int:
        if not self.cutted_at:
            return 0

        if self.rooting_days % 7 > 3:
            return (self.rooting_days // 7) + 1
        return self.rooting_days // 7

    @property
    def rooting_weeks_days(self) -> tuple[int, int] | None:
        if not self.cutted_at:
            return None

        weeks = self.rooting_days // 7
        days = self.rooting_days % 7
        return (weeks, days)

    @property
    def rooting_display(self):
        weeks_days = self.rooting_weeks_days
        if weeks_days is None:
            return gettext("Not cutted")

        weeks, days = weeks_days

        parts = []
        if weeks > 0:
            parts.append(ngettext("{n} week", "{n} weeks", weeks).format(n=weeks))
        if days > 0:
            parts.append(ngettext("{n} day", "{n} days", days).format(n=days))

        if parts:
            return ", ".join(parts)

        return gettext("0 days")

    @property
    def age_weeks(self) -> int:
        """
        Calculate the age of the grow log in weeks since germination.
        Returns 0 if germination date is not set.
        """
        if not self.is_germinating and not self.is_cutted:
            return 0

        if self.age_days % 7 > 3:
            return (self.age_days // 7) + 1
        return self.age_days // 7

    @property
    def age_weeks_days(self) -> tuple[int, int] | None:
        """
        Calculate the age of the grow log in weeks and days since germination.
        Returns (0, 0) if germination date is not set.
        """
        if not self.is_germinating and not self.is_cutted:
            return None

        weeks = self.age_days // 7
        days = self.age_days % 7
        return (weeks, days)

    @property
    def age_years_weeks_days(self) -> tuple[int, int, int] | None:
        """
        Calculate the age of the grow log in years, weeks and days since germination.
        Returns (0, 0, 0) if germination date is not set.
        """
        if not self.is_germinating and not self.is_cutted:
            return None

        years = self.age_days // 365
        remaining_days = self.age_days % 365
        weeks = remaining_days // 7
        days = remaining_days % 7
        return (years, weeks, days)

    @property
    def age_display(self) -> str:
        """
        Get a human-readable string representation of the grow log's age.
        """
        age = self.age_years_weeks_days
        if age is None:
            return gettext("Not germinated")

        years, weeks, days = age

        parts = []
        if years > 0:
            parts.append(ngettext("{n} year", "{n} years", years).format(n=years))
        if weeks > 0:
            parts.append(ngettext("{n} week", "{n} weeks", weeks).format(n=weeks))
        if days > 0:
            parts.append(ngettext("{n} day", "{n} days", days).format(n=days))

        if parts:
            return ", ".join(parts)

        return gettext("0 days")

    @property
    def vegetative_days(self) -> int:
        """
        Calculate the number of days since vegetative stage started.
        Returns -1 if vegetative date is not set.
        """
        if not self.is_vegetative:
            return -1
        delta = timezone.now().date() - self.vegetative_at
        return delta.days

    @property
    def vegetative_weeks(self) -> int:
        """
        Calculate the number of weeks since vegetative stage started.
        Returns 0 if vegetative date is not set.
        """
        if not self.is_vegetative:
            return 0
        if self.vegetative_days % 7 > 3:
            return (self.vegetative_days // 7) + 1
        return self.vegetative_days // 7

    @property
    def vegetative_weeks_days(self) -> tuple[int, int] | None:
        """
        Calculate the number of weeks and days since vegetative stage started.
        Returns (0, 0) if vegetative date is not set.
        """
        if not self.is_vegetative:
            return None

        weeks = self.vegetative_days // 7
        days = self.vegetative_days % 7
        return (weeks, days)

    @property
    def vegetative_years_weeks_days(self):
        """
        Calculate the number of years, weeks and days since vegetative stage started.
        Returns (0, 0, 0) if vegetative date is not set.
        """
        if not self.is_vegetative:
            return None

        years = self.vegetative_days // 365
        remaining_days = self.vegetative_days - (years * 365)
        weeks = remaining_days // 7
        days = remaining_days % 7
        return (years, weeks, days)

    @property
    def vegetative_display(self) -> str:
        """
        Get a human-readable string representation of the vegetative stage duration.
        """
        vegetative = self.vegetative_years_weeks_days
        if vegetative is None:
            return gettext("Not in vegetative stage")

        years, weeks, days = vegetative

        parts = []
        if years > 0:
            parts.append(ngettext("{n} year", "{n} years", years).format(n=years))
        if weeks > 0:
            parts.append(ngettext("{n} week", "{n} weeks", weeks).format(n=weeks))
        if days > 0:
            parts.append(ngettext("{n} day", "{n} days", days).format(n=days))

        if parts:
            return ", ".join(parts)

        return gettext("0 days")

    @property
    def flowering_days(self) -> int:
        """
        Calculate the number of days since flowering started.
        Returns -1 if flowering date is not set.
        """
        if not self.is_flowering:
            return -1
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
    def flowering_display(self) -> str:
        """
        Get a human-readable string representation of the flowering stage duration.
        """
        flowering = self.flowering_weeks_days
        if flowering is None:
            return gettext("Not in flowering stage")

        weeks, days = flowering

        parts = []
        if weeks > 0:
            parts.append(ngettext("{n} week", "{n} weeks", weeks).format(n=weeks))
        if days > 0:
            parts.append(ngettext("{n} day", "{n} days", days).format(n=days))

        if parts:
            return ", ".join(parts)

        return gettext("0 days")

    @property
    def days_grown(self) -> int:
        """
        Calculate the total number of days the grow log has been active.
        Returns 0 if germination date is not set.
        """
        if not self.is_germinating and not self.is_cutted:
            return 0

        if self.harvested_at is not None:
            end_date = self.harvested_at if self.is_harvested else timezone.now().date()
        else:
            end_date = timezone.now().date()

        if self.is_cutted:
            delta = end_date - self.cutted_at
        else:
            delta = end_date - self.germinating_at

        if delta.days < 0:
            return 0

        return delta.days

    @property
    def weeks_grown(self) -> int:
        """
        Calculate the total number of weeks the grow log has been active.
        Returns 0 if germination date is not set.
        """
        if not self.is_germinating and not self.is_cutted:
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
    def duration_days(self) -> int:
        """
        Calculate the total duration of the grow log in days.
        Returns 0 if the grow log is not finished.
        """
        if self.finished_at:
            delta = self.finished_at.date() - self.started_at.date()
        else:
            delta = timezone.now().date() - self.started_at.date()

        if delta.days < 0:
            return 0
        return delta.days

    @property
    def duration_weeks(self) -> int:
        """
        Calculate the total duration of the grow log in weeks.
        Returns 0 if the grow log is not finished.
        """
        if self.duration_days % 7 > 3:
            return (self.duration_days // 7) + 1
        return self.duration_days // 7

    @property
    def duration_week_days(self) -> dict[str, int]:
        """
        Calculate the total duration of the grow log in weeks and days.
        Returns (0, 0) if the grow log is not finished.
        """
        weeks = self.duration_days // 7
        days = self.duration_days % 7
        return {'weeks': weeks, 'days': days}

    @property
    def duration_years(self) -> int:
        """
        Calculate the total duration of the grow log in years.
        Returns 0 if the grow log is not finished.
        """
        return self.duration_days // 365

    @property
    def duration_years_weeks_days(self) -> dict[str, int]:
        """
        Calculate the total duration of the grow log in years, weeks and days.
        Returns (0, 0, 0) if the grow log is not finished.
        """
        years = self.duration_days // 365
        remaining_days = self.duration_days % 365
        weeks = remaining_days // 7
        days = remaining_days % 7
        return {'years': years, 'weeks': weeks, 'days': days}

    @property
    def duration_delta(self) -> timezone.timedelta:
        """
        Calculate the total duration of the grow log as a timedelta.
        Returns 0 if the grow log is not finished.
        """
        if self.finished_at is not None:
            delta = self.finished_at - self.started_at
        else:
            delta = timezone.now() - self.started_at
        return delta

    @property
    def duration_display(self) -> str:
        """
        Get a human-readable string representation of the grow log's duration.
        """
        durations = self.duration_years_weeks_days
        years = durations['years']
        weeks = durations['weeks']
        days = durations['days']

        parts = []
        if years > 0:
            parts.append(ngettext("{n} year", "{n} years", years).format(n=years))
        if weeks > 0:
            parts.append(ngettext("{n} week", "{n} weeks", weeks).format(n=weeks))
        if days > 0:
            parts.append(ngettext("{n} day", "{n} days", days).format(n=days))

        if parts:
            return ", ".join(parts)

        return gettext("0 days")

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
        entries = self.entries.all().order_by('-timestamp')
        if entries:
            return entries.first().location
        return None

    @property
    def current_stage(self) -> str:
        """
        Get the current stage of the grow log as a human-readable string.
        """
        if self.is_finished:
            return gettext("Finished")
        elif self.is_harvested:
            return gettext("Harvested")
        elif self.is_flowering:
            return gettext("Flowering")
        elif self.is_vegetative:
            return gettext("Vegetative")
        elif self.is_cutted:
            return gettext("Cutted")
        elif self.is_germinating:
            return gettext("Germinating")
        else:
            return gettext("Unknown")

    class Meta:
        db_table = "grow_growlog"
        unique_together = [('grower', 'name')]
        ordering = ['-started_at']


class GrowlogStrain(models.Model):
    #: The growlog for this strain
    growlog = models.ForeignKey(
        Growlog,
        on_delete=models.CASCADE,
        related_name='growlog_strains',
        verbose_name=_("growlog")
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

    @property
    def plant_count(self) -> int:
        """
        Get the number of plants for this strain in the grow log.
        """
        return self.quantity

    class Meta:
        db_table = "grow_growlog_strains"
        unique_together = [
            ('growlog', 'strain'),
        ]

    def delete(self, *args, **kwargs):
        """
        Override the delete method to prevent deletion of the last strain in a grow log.
        """
        growlog = self.growlog
        if growlog.growlog_strains.count() <= 1:
            raise ValueError(_("Cannot delete the last strain from a grow log."))

        super().delete(*args, **kwargs)
        growlog.save()

    def save(self, *args, **kwargs):
        """
        Override the save method to ensure that the grow log is saved after
        saving the strain association.

        This is necessary to update the grow log's strain count and related
        properties.
        """
        super().save(*args, **kwargs)
        self.growlog.save()


class GrowlogEntry(models.Model):
    #: The growlog this entry belongs to
    growlog = models.ForeignKey(Growlog,
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
    def age(self) -> int:
        """Get the age in days since the growlog started."""
        age_start = self.growlog.started_at
        if self.growlog.is_germinating:
            age_start = self.growlog.germinating_at
        elif self.growlog.is_cutted:
            age_start = self.growlog.cutted_at
        elif self.growlog.is_vegetative():
            age_start = self.growlog.vegetative_at

        delta_days = (self.timestamp - age_start).days
        if delta_days < 0:
            return -1
        return delta_days

    @property
    def vegetative_time(self) -> int:
        """Get the vegetative time in days since vegetative started."""
        if self.growlog.vegetative_at is None:
            return -1
        delta_days = (self.timestamp.date() - self.growlog.vegetative_at).days
        if delta_days < 0:
            return -1
        return delta_days

    @property
    def flowering_time(self) -> int:
        """Get the flowering time in days since flowering started."""
        if self.growlog.flowering_at is None:
            return -1
        delta_days = (self.timestamp.date() - self.growlog.flowering_at).days
        if delta_days < 0:
            return -1
        return delta_days

    @property
    def content_html(self) -> str:
        """
        Returns the HTML representation of the content.
        """
        if self.content:
            if self.content_type == TextType.MARKDOWN:
                from grow.growapi.parser.markdown import render_description_markdown
                return render_description_markdown(self.content)
            elif self.content_type == TextType.BBCODE:
                from grow.growapi.parser.bbcode import render_description_bbcode
                return render_description_bbcode(self.content)
            else:
                return self.content
        return ""

    @property
    def status(self) -> GrowlogStatus:
        """
        Get the status of the grow log entry based on the grow log's current stage.
        """
        end_date = timezone.now().date()
        if self.growlog.finished_at is not None:
            end_date = self.growlog.finished_at.date()

        if self.timestamp.date() > end_date:
            return GrowlogStatus.FINISHED

        status = GrowlogStatus.ACTIVE

        if self.growlog.germinating_at:
            if self.timestamp.date() < self.growlog.germinating_at:
                return status
            status = GrowlogStatus.GERMINATING
        elif self.growlog.is_cutted:
            if self.timestamp.date() < self.growlog.cutted_at:
                return status
            status = GrowlogStatus.ROOTING

        if self.growlog.vegetative_at:
            if self.timestamp.date() < self.growlog.vegetative_at:
                return status
            status = GrowlogStatus.VEGETATIVE

        if self.growlog.flowering_at:
            if self.timestamp.date() < self.growlog.flowering_at:
                return status
            status = GrowlogStatus.FLOWERING

        if self.growlog.harvested_at:
            if self.timestamp.date() < self.growlog.harvested_at:
                return status
            status = GrowlogStatus.HARVESTED

        if self.growlog.finished_at:
            if self.timestamp.date() < self.growlog.finished_at.date():
                return status
            status = GrowlogStatus.FINISHED

        return status

    @property
    def status_display(self) -> str:
        """
        Get the display value of the grow log entry's status.
        """
        start_date = self.growlog.started_at.date()
        ret_str = gettext("Active (Day {n})")
        if self.growlog.germinating_at:
            if self.timestamp.date() < self.growlog.germinating_at:
                return ret_str.format(n=(self.timestamp.date() - start_date).days + 1)
            start_date = self.growlog.germinating_at
            ret_str = gettext("Germinating (Day {n})")
        elif self.growlog.is_cutted:
            if self.timestamp.date() < self.growlog.cutted_at:
                return ret_str.format(n=(self.timestamp.date() - start_date).days + 1)
            start_date = self.growlog.cutted_at
            ret_str = gettext("Rooting (Days {n})")

        if self.growlog.vegetative_at:
            if self.timestamp.date() < self.growlog.vegetative_at:
                return ret_str.format(n=(self.timestamp.date() - start_date).days + 1)
            start_date = self.growlog.vegetative_at
            ret_str = gettext("Vegetative (Day {n})")

        if self.growlog.flowering_at:
            if self.timestamp.date() < self.growlog.flowering_at:
                return ret_str.format(n=(self.timestamp.date() - start_date).days + 1)
            start_date = self.growlog.flowering_at
            ret_str = gettext("Flowering (Day {n})")

        if self.growlog.harvested_at:
            if self.timestamp.date() < self.growlog.harvested_at:
                return ret_str.format(n=(self.timestamp.date() - start_date).days + 1)
            start_date = self.growlog.harvested_at
            ret_str = gettext("Drying (Day {n})")

        if self.growlog.finished_at:
            if self.timestamp.date() < self.growlog.finished_at.date():
                return ret_str.format(n=(self.timestamp.date() - start_date).days + 1)
            start_date = self.growlog.finished_at.date()
            ret_str = gettext("Finished (Day {n})")

        return ret_str.format(n=(self.timestamp.date() - start_date).days + 1)

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
        if not self.growlog.germinating_at and not self.growlog.cutted_at and not self.growlog.vegetative_at:  # noqa: E501
            return 0

        if self.growlog.vegetative_at is not None:
            delta = self.timestamp.date() - self.growlog.vegetative_at
        elif self.growlog.germinating_at is not None:
            delta = self.timestamp.date() - self.growlog.germinating_at
        elif self.growlog.cutted_at is not None:
            delta = self.timestamp.date() - self.growlog.cutted_at

        return delta.days

    @property
    def age_weeks(self) -> int | None:
        """
        Calculate the age of the grow log entry in weeks since the grow log's germination.
        Returns None if germination date is not set.
        """
        if self.age_days % 7 > 3:
            return (self.age_days // 7) + 1
        return self.age_days // 7

    @property
    def age_weeks_days(self) -> tuple[int, int] | None:
        """
        Calculate the age of the grow log entry in weeks and days since the grow log's germination.
        Returns None if germination date is not set.
        """
        if not self.growlog.germinating_at:
            return None

        weeks = self.age_days // 7
        days = self.age_days % 7
        return (weeks, days)

    @property
    def vegetative_days(self) -> int:
        """
        Calculate the number of days since vegetative started for the grow log entry.
        Returns -1 if vegetative date is not set.
        """
        if not self.growlog.vegetative_at:
            return -1
        if self.timestamp.date() < self.growlog.vegetative_at:
            return -1

        if self.growlog.flowering_at and self.timestamp.date() > self.growlog.flowering_at:
            delta = self.growlog.flowering_at - self.growlog.vegetative_at
        elif self.growlog.harvested_at and self.timestamp.date() > self.growlog.harvested_at:
            delta = self.growlog.harvested_at - self.growlog.vegetative_at
        elif self.growlog.finished_at and self.timestamp.date() > self.growlog.finished_at.date():
            delta = self.growlog.finished_at - self.growlog.vegetative_at
        else:
            delta = self.timestamp.date() - self.growlog.vegetative_at

        return delta.days

    @property
    def vegetative_weeks(self) -> int:
        """
        Calculate the number of weeks since vegetative started for the grow log entry.
        Returns 0 if vegetative date is not set.
        """
        if not self.growlog.vegetative_at:
            return 0
        if self.vegetative_days % 7 > 3:
            return (self.vegetative_days // 7) + 1
        return self.vegetative_days // 7

    @property
    def vegetative_weeks_days(self) -> tuple[int, int] | None:
        """
        Calculate the number of weeks and days since vegetative started for the grow log entry.
        Returns None if vegetative date is not set.
        """
        if not self.growlog.is_vegetative:
            return None

        if not self.growlog.is_flowering:
            weeks = self.vegetative_days // 7
            days = self.vegetative_days % 7
        else:
            delta = self.growlog.flowering_at - self.growlog.vegetative_at
            total_days = delta.days
            weeks = total_days // 7
            days = total_days % 7

        return (weeks, days)

    @property
    def vegetative_years_weeks_days(self) -> tuple[int, int, int] | None:
        """
        Calculate the number of years, weeks and days since vegetative started
        for the grow log entry.

        Returns None if vegetative date is not set.
        """
        if not self.growlog.is_vegetative:
            return None

        if not self.growlog.is_flowering:
            total_days = self.vegetative_days
        else:
            delta = self.growlog.flowering_at - self.growlog.vegetative_at
            total_days = delta.days

        years = total_days // 365
        remaining_days = total_days % 365
        weeks = remaining_days // 7
        days = remaining_days % 7
        return (years, weeks, days)

    @property
    def flowering_days(self) -> int:
        """
        Calculate the number of days since flowering started for the grow log entry.
        Returns -1 if flowering date is not set.
        """
        if not self.growlog.flowering_at:
            return -1
        if self.timestamp.date() < self.growlog.flowering_at:
            return -1

        if self.growlog.harvested_at and self.timestamp.date() > self.growlog.harvested_at:
            delta = self.growlog.harvested_at - self.growlog.flowering_at
        elif self.growlog.finished_at and self.timestamp.date() > self.growlog.finished_at.date():
            delta = self.growlog.finished_at.date() - self.growlog.flowering_at
        else:
            delta = self.timestamp.date() - self.growlog.flowering_at

        return delta.days

    @property
    def flowering_weeks(self) -> int:
        """
        Calculate the number of weeks since flowering started for the grow log entry.
        Returns 0 if flowering date is not set.
        """
        if not self.growlog.flowering_at:
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
        if not self.growlog.is_flowering:
            return None

        if not self.growlog.is_harvested:
            weeks = self.flowering_days // 7
            days = self.flowering_days % 7
        else:
            delta = self.growlog.harvested_at - self.growlog.flowering_at
            total_days = delta.days
            weeks = total_days // 7
            days = total_days % 7

        return (weeks, days)

    @property
    def duration_days(self) -> int:
        """
        Calculate the total number of days since the grow log
        started for this image.

        Returns 0 if germination date is not set.
        """
        return (self.timestamp.date() - self.growlog.started_at.date()).days

    @property
    def duration_weeks(self) -> int:
        """
        Calculate the total number of weeks since the grow log
        started for this image.

        Returns 0 if germination date is not set.
        """
        if self.duration_days % 7 > 3:
            return (self.duration_days // 7) + 1
        return self.duration_days // 7

    @property
    def duration_weeks_days(self) -> tuple[int, int]:
        """
        Calculate the total number of weeks and days since the grow log
        started for this image.

        Returns (0, 0) if germination date is not set.
        """
        weeks = self.duration_days // 7
        days = self.duration_days % 7
        return (weeks, days)

    @property
    def duration_years_weeks_days(self):
        """
        Calculate the total number of years, weeks and days of this entry
        since  the grow log started.

        Returns (0, 0, 0) if germination date is not set.
        """
        years = self.duration_days // 365
        remaining_days = self.duration_days % 365
        weeks = remaining_days // 7
        days = remaining_days % 7
        return (years, weeks, days)

    @property
    def duration_display(self) -> str:

        years, weeks, days = self.duration_years_weeks_days

        parts = []
        if years > 0:
            years_str = ngettext("{n} year", "{n} years", years).format(n=years)
            parts.append(years_str)
        if weeks > 0:
            weeks_str = ngettext("{n} week", "{n} weeks", weeks).format(n=weeks)
            parts.append(weeks_str)
        if days > 0:
            days_str = ngettext("{n} day", "{n} days", days).format(n=days)
            parts.append(days_str)

        if parts:
            return ", ".join(parts) if parts else gettext("0 days")

        return gettext("0 days")

    @property
    def germinating_days(self):
        """
        Calculate the number of days since germination started for this grow log entry.
        Returns -1 if germination date is not set.
        """
        if not self.growlog.germinating_at:
            return -1

        delta = self.timestamp.date() - self.growlog.germinating_at

        if self.growlog.vegetative_at is not None:
            if self.timestamp.date() >= self.growlog.vegetative_at:
                delta = self.growlog.vegetative_at - self.growlog.germinating_at
        elif self.growlog.flowering_at is not None:
            if self.timestamp.date() >= self.growlog.flowering_at:
                delta = self.growlog.flowering_at - self.growlog.germinating_at
        elif self.growlog.harvested_at is not None:
            if self.timestamp.date() >= self.growlog.harvested_at:
                delta = self.growlog.harvested_at - self.growlog.germinating_at
        elif self.growlog.finished_at is not None:
            if self.timestamp.date() >= self.growlog.finished_at.date():
                delta = self.growlog.finished_at - self.growlog.germinating_at

        return delta.days

    @property
    def germinating_duration_display(self) -> str:
        """
        Get the display string for the germinating duration of this grow log entry.
        """
        germinating_days = self.germinating_days
        if germinating_days < 0:
            return gettext("Not germinated")
        return ngettext("{n} day", "{n} days", germinating_days).format(n=germinating_days)

    @property
    def rooting_days(self):
        """
        Calculate the number of days since germination started for this grow log entry.
        Returns -1 if germination date is not set.
        """
        if not self.growlog.cutted_at:
            return -1

        if self.growlog.vegetative_at is not None:
            if self.timestamp.date() < self.growlog.vegetative_at:
                delta = self.timestamp.date() - self.growlog.cutted_at
            else:
                delta = self.growlog.vegetative_at - self.growlog.cutted_at
        elif self.growlog.flowering_at is not None:
            if self.timestamp.date() < self.growlog.flowering_at:
                delta = self.timestamp.date() - self.growlog.cutted_at
            else:
                delta = self.growlog.flowering_at - self.growlog.cutted_at
        elif self.growlog.harvested_at is not None:
            if self.timestamp.date() < self.growlog.harvested_at:
                delta = self.timestamp.date() - self.growlog.cutted_at
            else:
                delta = self.growlog.harvested_at - self.growlog.cutted_at
        elif self.growlog.finished_at is not None:
            if self.timestamp.date() < self.growlog.finished_at:
                delta = self.timestamp.date() - self.growlog.cutted_at
            else:
                delta = self.growlog.finished_at - self.growlog.cutted_at
        else:
            delta = self.timestamp.date() - self.growlog.cutted_at
        return delta.days

    @property
    def rooting_duration_display(self) -> str:
        """
        Get the display string for the rooting duration of this grow log entry.
        """
        rooting_days = self.rooting_days
        if rooting_days < 0:
            return gettext("Not cutted")
        return ngettext("{n} day", "{n} days", rooting_days).format(n=rooting_days)

    @property
    def vegetative_duration_display(self) -> str:
        """
        Get the display string for the vegetative duration of this grow log entry.
        """
        vegetative_days = self.vegetative_days
        if vegetative_days < 0:
            return gettext("Not in vegetative stage")

        years, weeks, days = self.vegetative_years_weeks_days

        parts = []
        if years > 0:
            years_str = ngettext("{n} year", "{n} years", years).format(n=years)
            parts.append(years_str)
        if weeks > 0:
            weeks_str = ngettext("{n} week", "{n} weeks", weeks).format(n=weeks)
            parts.append(weeks_str)
        if days > 0:
            days_str = ngettext("{n} day", "{n} days", days).format(n=days)
            parts.append(days_str)

        if parts:
            return ", ".join(parts)

        return gettext("0 days")

    @property
    def flowering_duration_display(self) -> str:
        """
        Get the display string for the flowering duration of this grow log entry.
        """
        flowering_days = self.flowering_days
        if flowering_days < 0:
            return gettext("Not in flowering stage")

        weeks, days = self.flowering_weeks_days

        parts = []
        if weeks > 0:
            weeks_str = ngettext("{n} week", "{n} weeks", weeks).format(n=weeks)
            parts.append(weeks_str)
        if days > 0:
            days_str = ngettext("{n} day", "{n} days", days).format(n=days)
            parts.append(days_str)

        if parts:
            return ", ".join(parts)

        return gettext("0 days")

    def growlog_entry_image_count(self) -> int:
        """
        Get the number of images associated with this grow log entry.
        """
        return self.images.count()

    def delete(self, *args, **kwargs):
        """
        Override the delete method to remove all associated images
        when the grow log entry is deleted.
        """
        growlog = self.growlog

        for image in self.images.all():
            image.delete()

        super().delete(*args, **kwargs)

        growlog.save()

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        self.growlog.save()

        return result

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
    description_type_data = models.CharField(
        _("description type"),
        max_length=50,
        default=TextType.MARKDOWN.value,
        choices=TEXT_CHOICES,
        db_column="description_type"
    )

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
    def description_html(self) -> SafeString | str:
        """
        Get the HTML representation of the description.
        """
        if self.description:
            if self.description_type == TextType.MARKDOWN:
                from grow.growapi.parser.markdown import render_description_markdown
                return render_description_markdown(self.description)
            elif self.description_type == TextType.BBCODE:
                from grow.growapi.parser.bbcode import render_description_bbcode
                return render_description_bbcode(self.description)
            else:
                return self.description
        return ""

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
        Calculate the age of the grow log entry image in weeks and days since the grow
        log's germination.

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

    @property
    def flowering_duration_display(self):
        """
        Get the display string for the flowering duration of this grow log entry image.
        """
        return self.growlog_entry.flowering_duration_display

    def delete(self, *args, **kwargs):
        """
        Override the delete method to remove the image file from storage when the model
        instance is deleted.
        """
        image = self.image
        storage = image.storage
        growlog = self.growlog_entry.growlog

        super().delete(*args, **kwargs)

        if storage.exists(image.name):
            storage.delete(image.name)

        growlog.save()

    def save(self, *args, **kwargs):
        """
        Override the save method to update the grow log's updated_at field when an image is
        added or modified.
        """
        result = super().save(*args, **kwargs)
        self.growlog_entry.growlog.save()
        return result

    class Meta:
        db_table = "grow_growlogentry_image"
