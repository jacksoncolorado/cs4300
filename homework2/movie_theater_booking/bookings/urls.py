from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import MovieViewSet, SeatViewSet, movie_list

router = DefaultRouter()
router.register("api/movies", MovieViewSet)
router.register("api/seats", SeatViewSet)

urlpatterns = [
    path("", movie_list, name="movie_list"),
] + router.urls
