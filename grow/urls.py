from django.urls import path
from .views import (
    IndexView,
    BreederIndexView,
    BreederView,
    BreederCreateView,
    BreederUpdateView,
)

app_name = "grow"

urlpatterns = [
    path("", IndexView.as_view(), name="home"),
    path("strain/", BreederIndexView.as_view(), name="breeder-overview"),
    path("strain/<slug:slug>/", BreederView.as_view(), name="breeder-detail"),
    path("breeder-create/", BreederCreateView.as_view(), name="breeder-create"),
    path("breeder-update/<slug:slug>", BreederUpdateView.as_view(), name="breeder-update"),
]
