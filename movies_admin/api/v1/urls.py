from api.v1 import views
from django.urls import path

urlpatterns = [
    path("movies/", views.MoviesListApi.as_view()),
    path("movies/<uuid:pk>/", views.MoviesDetailApi.as_view()),
]
