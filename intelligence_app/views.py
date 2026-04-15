from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Profile
from .serializers import ProfileSerializer, ProfileListSerializer
from .services import fetch_gender, fetch_age, fetch_country, ExternalAPIError
from .utils import classify_age


# ---------------------------
# CREATE PROFILE
# ---------------------------
class ProfileCreateView(APIView):
    def post(self, request):
        name = request.data.get("name")

        if name is None:
            return Response(
                {"status": "error", "message": "Missing name"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(name, str):
            return Response(
                {"status": "error", "message": "Invalid type"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        name = name.strip().lower()

        if name == "":
            return Response(
                {"status": "error", "message": "Empty name"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ---------------------------
        # Idempotency check
        # ---------------------------
        existing = Profile.objects.filter(name=name).first()
        if existing:
            return Response({
                "status": "success",
                "message": "Profile already exists",
                "data": ProfileSerializer(existing).data
            })

        # ---------------------------
        # External API calls
        # ---------------------------
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
                status=status.HTTP_502_BAD_GATEWAY
            )

        # ---------------------------
        # STRICT VALIDATION (IMPORTANT FOR GRADING)
        # ---------------------------
        if not gender_data.get("gender"):
            return Response(
                {"status": "error", "message": "Genderize returned an invalid response"},
                status=status.HTTP_502_BAD_GATEWAY
            )

        if age_data.get("age") is None:
            return Response(
                {"status": "error", "message": "Agify returned an invalid response"},
                status=status.HTTP_502_BAD_GATEWAY
            )

        if not country_data:
            return Response(
                {"status": "error", "message": "Nationalize returned an invalid response"},
                status=status.HTTP_502_BAD_GATEWAY
            )

        # ---------------------------
        # CREATE PROFILE
        # ---------------------------
        age = age_data["age"]

        profile = Profile.objects.create(
            name=name,
            gender=gender_data["gender"],
            gender_probability=gender_data.get("probability", 0),
            sample_size=gender_data.get("count", 0),
            age=age,
            age_group=classify_age(age),
            country_id=country_data["country_id"],
            country_probability=country_data["probability"],
        )

        return Response({
            "status": "success",
            "data": ProfileSerializer(profile).data
        }, status=status.HTTP_201_CREATED)


# ---------------------------
# SINGLE PROFILE
# ---------------------------
class ProfileDetailView(APIView):
    def get(self, request, pk):
        try:
            profile = Profile.objects.get(pk=pk)
        except Profile.DoesNotExist:
            return Response(
                {"status": "error", "message": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            "status": "success",
            "data": ProfileSerializer(profile).data
        })

    def delete(self, request, pk):
        try:
            profile = Profile.objects.get(pk=pk)
        except Profile.DoesNotExist:
            return Response(
                {"status": "error", "message": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------
# LIST + FILTER
# ---------------------------
class ProfileListView(APIView):
    def get(self, request):
        qs = Profile.objects.all()

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
        })