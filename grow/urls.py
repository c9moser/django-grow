from django.urls import path

from . import settings
from .views.index import IndexView
from .views.strain import (
    BreederIndexView,
    BreederView,
    BreederCreateView,
    BreederDeleteView,
    BreederUpdateView,
    BreederTranslationView,
    StrainAddToStockView,
    StrainAddToStock2View,

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
    HxStrainAddToStock2View,
    HxStrainRemoveFromStockView,
    HxStrainSearchView,
    HxStrainStockNotesView,
    HxStrainTranslationView,
    HxSeedsInStockInfoView,
    HxSeedsInStockDialogView,
    HxSeedsInStockDialogUpdateView,
)

from .views.location import (
     HxLocationTypeChangeView,
     LocationIndexView,
     LocationCreateView,
     LocationUpdateView,
     LocationDeleteView,
     HxLocationTypeChangeView,
     HxLocationDeleteView,
)

from .views.user import (
     UserInfoView,
     HxUserInfoAddSeedsToStockView,
     HxUserInfoRemoveSeedsFromStockView,
)

from .views.growlog import (  # noqa: F401
     GrowlogCreateView,
     GrowlogUpdateView,
     GrowlogDeleteView,
     GrowlogDetailView,
     HxGrowlogAddSeedsView,
)

from .views.utils import HxSelectDateDaysSanitizeView

app_name = "grow"

strain_patterns = [
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
    path("strain/add_to_stock/", StrainAddToStock2View.as_view(), name="strain-add-to-stock2"),
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
    path("__hx__/strain/add_to_stock2/",
         HxStrainAddToStock2View.as_view(),
         name="hx-strain-add-to-stock2"),
    path("__hx__/strain/filter/<int:breeder_pk>/",
         HxStrainFilterView.as_view(),
         name="hx-strain-filter"),
    path("__hx__/strain/remove_from_stock/<int:strain>/<int:feminized>/",
         HxStrainRemoveFromStockView.as_view(),
         name="hx-strain-remove-from-stock"),
    path("__hx__/strain/stock_notes/<int:pk>/", HxStrainStockNotesView.as_view(), name="hx-strain-stock-notes"),
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
    path("__hx__/select_date_days_sanitize/<int:year>/<int:month>/<int:day>/",
         HxSelectDateDaysSanitizeView.as_view(),
         name="hx-select-date-days-sanitize"),
    path("__hx__/strain/search/", HxStrainSearchView.as_view(), name="hx-strain-search"),
    path("__hx__/strain/seeds_in_stock_info/",
         HxSeedsInStockInfoView.as_view(),
         name="hx-seeds-in-stock-info"),
    path("__hx__/strain/seeds_in_stock_dialog/",
         HxSeedsInStockDialogView.as_view(),
         name="hx-seed-in-stock-dialog"),
    path("__hx__/strain/seeds_in_stock_dialog/update/",
         HxSeedsInStockDialogUpdateView.as_view(),
         name="hx-seed-in-stock-dialog-update"),
]


location_patterns = [
     path("location/", LocationIndexView.as_view(), name="location-index"),
     path("location/create/", LocationCreateView.as_view(), name="location-create"),
     path("location/update/<int:pk>/", LocationUpdateView.as_view(), name="location-update"),
     path("location/delete/<int:pk>/", LocationDeleteView.as_view(), name="location-delete"),
     #path("location/detail/<int:pk>/", LocationDetailView.as_view(), name="location-detail"),
     path("__hx__/location/type-change/<int:pk>/",
          HxLocationTypeChangeView.as_view(),
          name="hx-location-type-change"),
     path("__hx__/location/delete/<int:pk>/", HxLocationDeleteView.as_view(), name="hx-location-delete"),
]

user_patterns = [
     path("grow/my-info/", UserInfoView.as_view(), name="user-info"),
     path("__hx__/grow/user/add_seeds_to_stock/<int:strain>/<int:feminized>/",
          HxUserInfoAddSeedsToStockView.as_view(),
          name="hx-user-add-seeds-to-stock"),
     path("__hx__/grow/user/remove_seeds_from_stock/<int:strain>/<int:feminized>/",
          HxUserInfoRemoveSeedsFromStockView.as_view(),
          name="hx-user-remove-seeds-from-stock"),
]

growlog_patterns = [
     path("growlog/create/", GrowlogCreateView.as_view(), name="growlog-create"),
     #path("growlog/update/<int:pk>/", GrowlogUpdateView.as_view(), name="growlog-update"),
     #path("growlog/delete/<int:pk>/", GrowlogDeleteView.as_view(), name="growlog-delete"),
     path("growlog/detail/<int:pk>/", GrowlogDetailView.as_view(), name="growlog-detail"),
     path("__hx__/growlog/<int:growlog_pk>/add_seeds/",
          HxGrowlogAddSeedsView.as_view(),
          name="hx-growlog-add-seeds"),
     #path("__hx__/growlog/<int:growlog_pk>/add_strain/",
     #     HxGrowlogAddStrainView.as_view(),
     #     name="hx-growlog-add-strain"),
]

urlpatterns = [
     *strain_patterns,
     *location_patterns,
     *growlog_patterns,
     *user_patterns,
]
