from grow.growapi.enums import GrowLightType
from ._base import BaseView
from .. import settings
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from ..forms.location import LocationForm, LocationTypeChangeForm
from ..growapi.models.location import Location, OutdoorLocation, GrowRoom
from ..enums import LocationType
from django.utils.translation import gettext as _


class LocationIndexView(LoginRequiredMixin, BaseView):
    template_name = settings.GROW_TEMPLATES['grow/location/index']

    def get(self, request: HttpRequest) -> HttpResponse:
        locations = request.user.locations.all().order_by('name')
        return render(request, self.template_name, {
            'locations': locations,
        })


class LocationCreateView(LoginRequiredMixin, BaseView):
    template_name = settings.GROW_TEMPLATES['grow/location/create']

    def get(self, request: HttpRequest) -> HttpResponse:
        form = LocationForm()
        return render(request, self.template_name, {
            'form': form,
            'location_pk': 0,
        })

    def post(self, request: HttpRequest) -> HttpResponse:
        form = LocationForm(request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            location.owner = request.user
            location.save()
            if location.location_type == LocationType.INDOOR:
                gr = GrowRoom(
                    location=location,
                    width=form.cleaned_data.get('width', 0),
                    depth=form.cleaned_data.get('depth', 0),
                    height=form.cleaned_data.get('height', 0),
                    light_power_consumption=form.cleaned_data.get('light_power_consumption', 0)
                )
                gr.light_type = GrowLightType.from_string(
                    form.cleaned_data.get('light_type',
                                          GrowLightType.LED.value))
                gr.save()
            elif location.location_type == LocationType.OUTDOOR:
                OutdoorLocation.objects.create(location=location,
                                               longitude=form.cleaned_data.get('longitude', None),
                                               latitude=form.cleaned_data.get('latitude', None))
            return redirect(reverse('grow:location-index'))
        print("Form is not valid:")
        print(form.errors)
        return render(request, self.template_name, {
            'form': form,
            'location_pk': 0,
        })


class LocationUpdateView(LoginRequiredMixin, BaseView):
    template_name = settings.GROW_TEMPLATES['grow/location/update']

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        location = Location.objects.get(pk=pk, owner=request.user)
        initial_data = {}
        outdoor = getattr(location, 'outdoor_location', None)
        growroom = getattr(location, 'grow_room', None)
        if outdoor:
            initial_data.update({
                'longitude': outdoor.longitude,
                'latitude': outdoor.latitude,
            })
        if growroom:
            initial_data.update({
                'width': growroom.width,
                'depth': growroom.depth,
                'height': growroom.height,
                'light_type': growroom.light_type.value,
                'light_power_consumption': growroom.light_power_consumption,
                'ventilation_intensity': growroom.ventilation_intensity,
                'ventilation_power_consumption': growroom.ventilation_power_consumption,
            })

        form = LocationForm(instance=location, initial=initial_data)
        return render(request, self.template_name, {
            'form': form,
            'location': location,
            'location_pk': location.pk,
        })

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        location = get_object_or_404(Location, pk=pk, owner=request.user)
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            location = form.save(commit=False)
            location.save()
            if location.location_type == LocationType.INDOOR:
                gr = getattr(location, 'grow_room', None)
                if not gr:
                    gr = GrowRoom(
                        location=location,
                        width=form.cleaned_data.get('width', 0),
                        depth=form.cleaned_data.get('depth', 0),
                        height=form.cleaned_data.get('height', 0),
                        light_power_consumption=form.cleaned_data.get('light_power_consumption', 0),
                        ventilation_intensity=form.cleaned_data.get('ventilation_intensity', 0),
                        ventilation_power_consumption=form.cleaned_data.get(
                            'ventilation_power_consumption', 0),
                    )
                    gr.light_type = GrowLightType.from_string(
                        form.cleaned_data.get('light_type',
                                              GrowLightType.LED.value))
                else:
                    gr.width = form.cleaned_data.get('width', 0)
                    gr.depth = form.cleaned_data.get('depth', 0)
                    gr.height = form.cleaned_data.get('height', 0)
                    gr.light_power_consumption = form.cleaned_data.get('light_power_consumption', 0)
                    gr.light_type = GrowLightType.from_string(
                        form.cleaned_data.get('light_type',
                                              GrowLightType.LED.value))
                    gr.ventilation_intensity = form.cleaned_data.get('ventilation_intensity', 0)
                    gr.ventilation_power_consumption = form.cleaned_data.get(
                        'ventilation_power_consumption', 0)
                gr.save()

            elif location.location_type == LocationType.OUTDOOR:
                outdoor = getattr(location, 'outdoor_location', None)
                if outdoor:
                    outdoor.longitude = form.cleaned_data.get('longitude', None)
                    outdoor.latitude = form.cleaned_data.get('latitude', None)
                    outdoor.save()
                else:
                    OutdoorLocation.objects.create(location=location,
                                                   longitude=form.cleaned_data.get(
                                                       'longitude', None),
                                                   latitude=form.cleaned_data.get(
                                                       'latitude', None))

            return redirect(reverse('grow:location-index'))
        print("Form is not valid:")
        print(form.errors)
        return render(request, self.template_name, {
            'form': form,
            'location': location,
            'location_pk': location.pk,
        })


class HxLocationTypeChangeView(LoginRequiredMixin, BaseView):
    template_name = settings.GROW_TEMPLATES['grow/location/hx-type-change']

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        if pk:
            location = get_object_or_404(Location, pk=pk, owner=request.user)
        else:
            location = None
        location_type = request.GET.get('location_type', 'other')

        width = None
        depth = None
        height = None
        light_type = None
        light_power_consumption = None
        ventilation_intensity = None
        ventilation_power_consumption = None

        longitude = None
        latitude = None

        try:
            lt = LocationType.from_string(location_type)
            if location:
                if lt == LocationType.INDOOR:
                    if hasattr(location, 'grow_room') and location.grow_room:
                        width = location.grow_room.width
                        depth = location.grow_room.depth
                        height = location.grow_room.height
                        light_type = location.grow_room.light_type.value
                        light_power_consumption = location.grow_room.light_power_consumption
                        ventilation_intensity = location.grow_room.ventilation_intensity
                        ventilation_power_consumption = location.grow_room.ventilation_power_consumption  # noqa: E501
                elif lt == LocationType.OUTDOOR:
                    if hasattr(location, 'outdoor_location') and location.outdoor_location:
                        longitude = location.outdoor_location.longitude
                        latitude = location.outdoor_location.latitude
                else:
                    location_type = 'other'
        except ValueError:
            lt = None
            location_type = 'other'

        form = LocationTypeChangeForm(initial={
            'width': width,
            'depth': depth,
            'height': height,
            'longitude': longitude,
            'latitude': latitude,
            'light_type': light_type,
            'light_power_consumption': light_power_consumption,
            'ventilation_intensity': ventilation_intensity,
            'ventilation_power_consumption': ventilation_power_consumption,
        })

        return render(request, self.template_name, context={
            'location_type': location_type,
            'location_pk': pk,
            'form': form
        })


class LocationDeleteView(LoginRequiredMixin, BaseView):
    template_name = settings.GROW_TEMPLATES['grow/location/delete']

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        location = get_object_or_404(Location, pk=pk, owner=request.user)
        error = None
        if location.growlogs:
            error = _('Location cannot be deleted because it has associated growlogs.')

        return render(request, self.template_name, {
            'location': location,
            'error': error,
        })

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        location = get_object_or_404(Location, pk=pk, owner=request.user)
        if location.growlogs:
            return render(request, self.template_name, {
                'location': location,
                'error': _('Location cannot be deleted because it has associated growlogs.')
            })
        location.delete()
        return redirect(reverse('grow:location-index'))


class HxLocationDeleteView(LoginRequiredMixin, BaseView):
    template_name = settings.GROW_TEMPLATES['grow/location/hx-delete']

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        location = get_object_or_404(Location, pk=pk, owner=request.user)
        error = None
        if location.growlogs:
            error = _('Location cannot be deleted because it has associated growlogs.')
        return render(request, self.template_name, {
            'location': location,
            'error': error,
        })

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        location = get_object_or_404(Location, pk=pk, owner=request.user)
        if location.growlogs:
            return render(request, self.template_name, {
                'location': location,
                'error': _('Location cannot be deleted because it has associated growlogs.')
            })
        location.delete()
        return redirect(reverse('grow:location-index'))
