from django.urls import path
from .views import ProfileView, ProfileDetailView

urlpatterns = [
    path('profiles', ProfileView.as_view()),
    path('profiles/', ProfileView.as_view()),
    path('profiles/<uuid:pk>', ProfileDetailView.as_view()),
    path('profiles/<uuid:pk>/', ProfileDetailView.as_view()),
]