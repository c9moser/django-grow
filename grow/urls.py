from django.urls import path

from grow.views.utils import HxSelectDateDaysSanitizeView
from . import settings
from .views import (
    IndexView,
    BreederIndexView,
    BreederView,
    BreederCreateView,
    BreederDeleteView,
    BreederUpdateView,
    StrainAddToStockView,
    StrainCreateView,
    StrainDeleteView,
    StrainRemoveFromStockView,
    StrainUpdateView,
    StrainView,
    HxBreederDeleteView,
    HxBreederFilterView,
    HxSanitizeDateDayView,
    HxStrainDeleteView,
    HxStrainAddToStockView,
    HxStrainRemoveFromStockView,
)

app_name = "grow"

urlpatterns = [
    path("", IndexView.as_view(), name="home"),
    path("strains/", BreederIndexView.as_view(), name="breeder-overview"),
    path("strains/<slug:slug>/", BreederView.as_view(), name="breeder-detail"),
    path("strains/<slug:breeder_slug>/<slug:slug>/", StrainView.as_view(), name="strain-detail"),
    path("breeder/create/", BreederCreateView.as_view(), name="breeder-create"),
    path("breeder/update/<int:pk>/", BreederUpdateView.as_view(), name="breeder-update"),
    path("breeder/delete/<int:pk>/", BreederDeleteView.as_view(), name="breeder-delete"),
    path("strain/create/<int:breeder_pk>", StrainCreateView.as_view(), name="strain-create"),
    path("strain/update/<int:pk>/", StrainUpdateView.as_view(), name="strain-update"),
    path("strain/delete/<int:pk>/", StrainDeleteView.as_view(), name="strain-delete"),
    path("strain/add_to_stock/<int:strain>/<int:feminized>/",
         StrainAddToStockView.as_view(),
         name="strain-add-to-stock"),
    path("strain/remove_from_stock/<int:strain>/<int:feminized>/",
         StrainRemoveFromStockView.as_view(),
         name="strain-remove-from-stock"),
    # path("strain/image-upload/<int:pk>/", StrainUploadImageView.as_view(), name="strain-image-upload"),
    path("__hx__/sanitize_date_day/<int:year>/<int:month>/",
         HxSanitizeDateDayView.as_view(),
         name="hx-sanitize-date-day"),
    path("__hx__/breeder/delete/<int:pk>", HxBreederDeleteView.as_view(), name="hx-breeder-delete"),
    path("__hx__/strain/delete/<int:pk>", HxStrainDeleteView.as_view(), name="hx-strain-delete"),
    path("__hx__/strain/add_to_stock/<int:strain>/<int:feminized>/",
         HxStrainAddToStockView.as_view(),
         name="hx-strain-add-to-stock"),
    path("__hx__/strain/remove_from_stock/<int:strain>/<int:feminized>/",
         HxStrainRemoveFromStockView.as_view(),
         name="hx-strain-remove-from-stock"),
    path("__hx__/strain/delete/<int:pk>/", HxStrainDeleteView.as_view(), name="hx-strain-delete"),
    # path("__hx__/strain/image-upload/<int:pk>/", HxStrainImageUploadView.as_view(), name=hx-strain-image-upload),

    path("__hx__/breeder/filter/",
         HxBreederFilterView.as_view(),
         name="hx-breeder-filter"),
    path("__hx__/select_date_days_sanitize/<int:year>/<int:month>/",
         HxSelectDateDaysSanitizeView.as_view(),
         name="hx-select-date-days-sanitize"),

]
