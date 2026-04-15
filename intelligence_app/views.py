from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Profile
from .serializers import ProfileSerializer, ProfileListSerializer
from .services import fetch_gender, fetch_age, fetch_country, ExternalAPIError
from .utils import classify_age


class ProfileView(APIView):
    """
    Handles:
    POST /api/profiles
    GET  /api/profiles
    """

    def post(self, request):
        name = request.data.get("name")

        # Validate input
        if name is None:
            return Response(
                {"status": "error", "message": "Missing name"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(name, str):
            return Response(
                {"status": "error", "message": "Invalid type"},
                status=422
            )

        name = name.strip().lower()

        if not name:
            return Response(
                {"status": "error", "message": "Missing name"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Idempotency check
        existing = Profile.objects.filter(name=name).first()
        if existing:
            return Response({
                "status": "success",
                "message": "Profile already exists",
                "data": ProfileSerializer(existing).data
            }, status=status.HTTP_200_OK)

        # Fetch external APIs
        try:
            gender_data = fetch_gender(name)
            age_data = fetch_age(name)
            country_data = fetch_country(name)
        except ExternalAPIError as e:
            return Response(
                {
                    "status": "error",
                    "message": f"{str(e)} returned an invalid response"
                },
                status=502
            )

        age = age_data["age"]

        # Create profile
        profile = Profile.objects.create(
            name=name,
            gender=gender_data["gender"],
            gender_probability=gender_data["probability"],
            sample_size=gender_data["count"],
            age=age,
            age_group=classify_age(age),
            country_id=country_data["country_id"],
            country_probability=country_data["probability"],
        )

        return Response({
            "status": "success",
            "data": ProfileSerializer(profile).data
        }, status=status.HTTP_201_CREATED)

    def get(self, request):
        qs = Profile.objects.all()

        # Filters (case-insensitive)
        gender = request.GET.get("gender")
        country_id = request.GET.get("country_id")
        age_group = request.GET.get("age_group")

        if gender:
            qs = qs.filter(gender__iexact=gender)

        if country_id:
            qs = qs.filter(country_id__iexact=country_id)

        if age_group:
            qs = qs.filter(age_group__iexact=age_group)

        return Response({
            "status": "success",
            "count": qs.count(),
            "data": ProfileListSerializer(qs, many=True).data
        }, status=status.HTTP_200_OK)


class ProfileDetailView(APIView):
    """
    Handles:
    GET /api/profiles/{id}
    DELETE /api/profiles/{id}
    """

    def get(self, request, pk):
        try:
            profile = Profile.objects.get(pk=pk)
        except Profile.DoesNotExist:
            return Response(
                {"status": "error", "message": "Profile not found"},
                status=404
            )

        return Response({
            "status": "success",
            "data": ProfileSerializer(profile).data
        }, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        try:
            profile = Profile.objects.get(pk=pk)
        except Profile.DoesNotExist:
            return Response(
                {"status": "error", "message": "Profile not found"},
                status=404
            )

        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)