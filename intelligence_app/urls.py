from django.urls import path
from .views import ProfileCreateView, ProfileDetailView, ProfileListView

urlpatterns = [
    path('profiles/list', ProfileListView.as_view()),
    path('profiles/', ProfileCreateView.as_view()),
    path('profiles/<uuid:pk>', ProfileDetailView.as_view()),
]