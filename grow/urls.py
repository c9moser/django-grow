from django.urls import path
from .views import (
    IndexView,
    BreederIndexView,
    BreederView,
    BreederCreateView,
    BreederUpdateView,
    StrainCreateView,
    StrainUpdateView,
    StrainView,
)

app_name = "grow"

urlpatterns = [
    path("", IndexView.as_view(), name="home"),
    path("strain/", BreederIndexView.as_view(), name="breeder-overview"),
    path("breeder-create/", BreederCreateView.as_view(), name="breeder-create"),
    path("breeder-update/<slug:slug>", BreederUpdateView.as_view(), name="breeder-update"),
    path("strain/<slug:slug>/", BreederView.as_view(), name="breeder-detail"),
    path("strain-create/<slug:breeder_slug>", StrainCreateView.as_view(), name="strain-create"),
    path("strain/<slug:breeder_slug>/<slug:slug>/", StrainView.as_view(), name="strain-detail"),
    path("strain/<slug:breeder_slug>/<slug:slug>/update", StrainUpdateView.as_view(), name="strain-update"),  # noqa: E501

]
