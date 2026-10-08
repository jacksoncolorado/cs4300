from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import BookingViewSet, MovieViewSet, SeatViewSet, book_seat_view, movie_list

router = DefaultRouter()
router.register("api/movies", MovieViewSet)
router.register("api/seats", SeatViewSet)
router.register("api/bookings", BookingViewSet, basename="booking")

urlpatterns = [
    path("", movie_list, name="movie_list"),
    path("movies/<int:movie_id>/seats/", book_seat_view, name="book_seat"),
] + router.urls
