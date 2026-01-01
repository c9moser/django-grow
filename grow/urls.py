from django.urls import path
from .views import (
    IndexView,
    BreederIndexView,
    BreederView,
    BreederCreateView,
    BreederDeleteView,
    BreederUpdateView,
    StrainCreateView,
    StrainUpdateView,
    StrainView,
    HxBreederDeleteView,
    #HxStrainDeleteView,
)

app_name = "grow"

urlpatterns = [
    path("", IndexView.as_view(), name="home"),
    path("strain/", BreederIndexView.as_view(), name="breeder-overview"),
    path("breeder/create/", BreederCreateView.as_view(), name="breeder-create"),
    path("breeder/update/<int:pk>/", BreederUpdateView.as_view(), name="breeder-update"),
    path("breeder/delete/<int:pk>/", BreederDeleteView.as_view(), name="breeder-delete"),
    path("breeder/__hx__/delete/<int:pk>", HxBreederDeleteView.as_view(), name="hx-breeder-delete"),
    path("breeder/view/<slug:slug>/", BreederView.as_view(), name="breeder-detail"),
    path("strain/create/<int:breeder_pk>", StrainCreateView.as_view(), name="strain-create"),
    path("strain/view/<slug:breeder_slug>/<slug:slug>/", StrainView.as_view(), name="strain-detail"),
    path("strain/update/<int:pk>/", StrainUpdateView.as_view(), name="strain-update"),
    #path("strain/image-upload/<int:pk>/", StrainUploadImageView.as_view(), name="strain-image-upload"),
    #path("strain/delete/<int:pk>/", StrainDeleteView.as_view(), name="strain-delete"),
    #path("strain/__hx__/delete/<int:pk>/", HxStrainDeleteView.as_view(), name=hx-strain-delete),
    #path("strain/__hx__/image-uplaid/<int:pk>/", HxStrainImageUploadView.as_view(), name=hx-strain-image-upload),

]
