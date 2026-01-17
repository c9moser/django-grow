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
    BreederTranslationView,
    StrainAddToStockView,
    StrainCommentCreateView,
    StrainCommentUpdateView,
    StrainCreateView,
    StrainDeleteView,
    StrainGalleryView,
    StrainImageUploadView,
    StrainRemoveFromStockView,
    StrainSearchView,
    StrainTranslationView,
    StrainUpdateView,
    StrainView,
    HxBreederDeleteView,
    HxBreederFilterView,
    HxBreederTranslationView,
    HxStrainDeleteView,
    HxStrainFilterView,
    HxStrainAddToStockView,
    HxStrainRemoveFromStockView,
    HxStrainTranslationView,
)
from .views.utils import HxSelectDateDaysSanitizeView

from django.conf.urls.i18n import i18n_patterns
app_name = "grow"

strain_patterns = i18n_patterns(
    path("", IndexView.as_view(), name="home"),
    # Views for Breeders and Strains details
    path("strains/", BreederIndexView.as_view(), name="breeder-overview"),
    path("strains/<slug:slug>/", BreederView.as_view(), name="breeder-detail"),
    path("strains/<slug:breeder_slug>/<slug:slug>/", StrainView.as_view(), name="strain-detail"),

    # Views for creating, updating, deleting Breeders
    path("breeder/create/", BreederCreateView.as_view(), name="breeder-create"),
    path("breeder/update/<int:pk>/", BreederUpdateView.as_view(), name="breeder-update"),
    path("breeder/delete/<int:pk>/", BreederDeleteView.as_view(), name="breeder-delete"),
    path("breeder/translate/<int:pk>/",
         BreederTranslationView.as_view(),
         name="breeder-translate"),

     # Views for creating, updating, deleting Strains
    path("strain/create/<int:breeder_pk>",
         StrainCreateView.as_view(),
         name="strain-create"),
    path("strain/update/<int:pk>/", StrainUpdateView.as_view(), name="strain-update"),
    path("strain/delete/<int:pk>/", StrainDeleteView.as_view(), name="strain-delete"),
    path("strain/gallery/<int:strain_pk>/",
         StrainGalleryView.as_view(),
         name="strain-gallery"),
    path("strain/image-upload/<int:strain_pk>/",
         StrainImageUploadView.as_view(),
         name="strain-image-upload"),
    path("strain/search/", StrainSearchView.as_view(), name="strain-search"),
    path("strain/translate/<int:pk>/",
         StrainTranslationView.as_view(),
         name="strain-translate"),
    path("strain/add_to_stock/<int:strain>/<int:feminized>/",
         StrainAddToStockView.as_view(),
         name="strain-add-to-stock"),
    path("strain/remove_from_stock/<int:strain>/<int:feminized>/",
         StrainRemoveFromStockView.as_view(),
         name="strain-remove-from-stock"),
     path("strain/add_comment/<int:strain_pk>/",
         StrainCommentCreateView.as_view(),
         name="strain-comment-add"),
     path("strain/update_comment/<int:pk>/",
         StrainCommentUpdateView.as_view(),
         name="strain-comment-update"),

    # HTMX Views
    path("__hx__/sanitize_date_day/<int:year>/<int:month>/",
         HxSelectDateDaysSanitizeView.as_view(),
         name="hx-sanitize-date-day"),
    path("__hx__/breeder/delete/<int:pk>", HxBreederDeleteView.as_view(), name="hx-breeder-delete"),
    path("__hx__/breeder/filter-strains/<int:breeder_pk>/",
         HxStrainFilterView.as_view(),
         name="hx-strain-search"),
    path("__hx__/breeder/translation/<int:pk>/",
         HxBreederTranslationView.as_view(),
         name="hx-breeder-translation"),
    path("__hx__/strain/delete/<int:pk>", HxStrainDeleteView.as_view(), name="hx-strain-delete"),
    path("__hx__/strain/add_to_stock/<int:strain>/<int:feminized>/",
         HxStrainAddToStockView.as_view(),
         name="hx-strain-add-to-stock"),
    path("__hx__/strain/remove_from_stock/<int:strain>/<int:feminized>/",
         HxStrainRemoveFromStockView.as_view(),
         name="hx-strain-remove-from-stock"),
    path("__hx__/strain/delete/<int:pk>/", HxStrainDeleteView.as_view(), name="hx-strain-delete"),
    path("__hx__/strain/translation/<int:pk>/",
         HxStrainTranslationView.as_view(),
         name="hx-strain-translation"),
    path("__hx__/breeder/filter/",
         HxBreederFilterView.as_view(),
         name="hx-breeder-filter"),
    path("__hx__/select_date_days_sanitize/<int:year>/<int:month>/",
         HxSelectDateDaysSanitizeView.as_view(),
         name="hx-select-date-days-sanitize"),
)

urlpatterns = [
     *strain_patterns,
]
