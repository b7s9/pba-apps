import json
import pathlib

import sentry_sdk
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render
from geopy.adapters import AioHTTPAdapter
from geopy.geocoders import GoogleV3, Nominatim
from shapely.geometry import Point, shape

with open(pathlib.Path(__file__).parent / "data" / "Zoning_RCO-2.geojson") as f:
    RCOS = json.load(f)

with open(pathlib.Path(__file__).parent / "data" / "Council_Districts_2024.geojson") as f:
    DISTRICTS = json.load(f)

with open(pathlib.Path(__file__).parent / "data" / "Political_Divisions.geojson") as f:
    DIVISIONS = json.load(f)

with open(pathlib.Path(__file__).parent / "data" / "polling_places.geojson") as f:
    POLLING_PLACES = json.load(f)

UA = "apps.bikeaction.org Geopy"


def index(request):
    return render(
        request, "rcosearch.html", context={"GOOGLE": settings.GOOGLE_MAPS_API_KEY is not None}
    )


@transaction.non_atomic_requests
async def query_address(request):
    submission = request.POST.get("street_address")
    search_address = f"{submission} Philadelphia, PA"

    try:
        if settings.GOOGLE_MAPS_API_KEY is not None:
            async with GoogleV3(
                api_key=settings.GOOGLE_MAPS_API_KEY, user_agent=UA, adapter_factory=AioHTTPAdapter
            ) as geolocator:
                address = await geolocator.geocode(search_address)
        else:
            async with Nominatim(user_agent=UA, adapter_factory=AioHTTPAdapter) as geolocator:
                address = await geolocator.geocode(search_address)
    except Exception as err:
        error = "Backend API failure, try again?"
        sentry_sdk.capture_exception(err)
        return HttpResponse(f'<p style="color: red;">{error}</p>')

    if address is None:
        error = (
            f"Failed to find address ({submission}) "
            "be sure to include your entire street address"
        )
        return HttpResponse(f'<p style="color: red;">{error}</p>')

    point = Point(address.longitude, address.latitude)

    rcos = []
    other = []
    wards = []
    for feature in RCOS["features"]:
        polygon = shape(feature["geometry"])
        if polygon.contains(point):
            if feature["properties"]["ORG_TYPE"] == "Ward":
                wards.append(feature["properties"])
            elif feature["properties"]["ORG_TYPE"] in ["NID", "SSD", None]:
                other.append(feature["properties"])
            else:
                rcos.append(feature["properties"])

    district = None
    for feature in DISTRICTS["features"]:
        polygon = shape(feature["geometry"])
        if polygon.contains(point):
            district = feature["properties"]["DISTRICT"]
            break

    ward, division = None, None
    for feature in DIVISIONS["features"]:
        polygon = shape(feature["geometry"])
        if polygon.contains(point):
            dn = feature["properties"]["DIVISION_NUM"]
            ward, division = [int(dn[i : i + 2]) for i in range(0, len(dn), 2)]
            break

    polling_place = None
    for feature in POLLING_PLACES["features"]:
        if feature["properties"]["ward"] == ward and feature["properties"]["division"] == division:
            polling_place = (
                f"{feature['properties']['placename']} - {feature['properties']['street_address']}"
            )
            break

    return render(
        request,
        "rco_partial.html",
        context={
            "DISTRICT": district,
            "RCOS": rcos,
            "OTHER": other,
            "WARDS": wards,
            "WARD": ward,
            "DIVISION": division,
            "POLLING_PLACE": polling_place,
            "address": address,
        },
    )
