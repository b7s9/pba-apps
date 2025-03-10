from asgiref.sync import async_to_sync
from celery import shared_task
from django.contrib.gis.geos import Point

from facets.utils import geocode_address


@shared_task
def geocode_signature(signature_id):
    from campaigns.models import PetitionSignature

    signature = PetitionSignature.objects.get(id=signature_id)

    if signature.postal_address_line_1 is not None:
        print(f"Geocoding {signature}")
        address = async_to_sync(geocode_address)(
            signature.postal_address_line_1 + " " + signature.zip_code
        )
        if address is not None:
            print(f"Address found {address}")
            PetitionSignature.objects.filter(id=signature_id).update(
                location=Point(address.longitude, address.latitude)
            )
        else:
            print(f"No address found for {signature.postal_address_line_1} {signature.zip_code}")
            PetitionSignature.objects.filter(id=signature_id).update(location=None)
