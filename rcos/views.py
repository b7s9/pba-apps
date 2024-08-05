import json
import pathlib

import sentry_sdk
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from geopy.geocoders import GoogleV3, Nominatim
from shapely.geometry import Point, shape

with open(pathlib.Path(__file__).parent / "data" / "Zoning_RCO-2.geojson") as f:
    RCOS = json.load(f)

UA = "apps.bikeaction.org Geopy"


def index(request):
    return render(request, "rcosearch.html")


@csrf_exempt
def query_address(request):
    submission = request.POST.get("street_address")
    search_address = f"{submission} Philadelphia, PA"

    try:
        if settings.GOOGLE_MAPS_API_KEY is not None:
            address = GoogleV3(api_key=settings.GOOGLE_MAPS_API_KEY, user_agent=UA).geocode(
                search_address
            )
        else:
            address = Nominatim(user_agent=UA).geocode(search_address)
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

    results = []
    for feature in RCOS["features"]:
        if feature["properties"]["ORG_TYPE"] != "Ward":
            polygon = shape(feature["geometry"])
            if polygon.contains(point):
                results.append(feature["properties"])

    return render(request, "rco_partial.html", context={"RCOS": results})
