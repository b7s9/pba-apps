from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
import os
import pyap
from playwright.sync_api import sync_playwright
import pytz
import urllib
from django.core.files.base import ContentFile
from playwright.async_api import FilePayload

PPA_SMARTSHEET_URL = os.getenv(
    "PPA_SMARTSHEET_URL",
    "https://app.smartsheet.com/b/form/463e9faa2a644f4fae2a956f331f451c",
)


class ViolationObserved(StrEnum):
    CORNER_CLEARANCE = "Corner Clearance (vehicle parked on corner)"
    CROSSWALK = "Crosswalk (vehicle on crosswalk)"
    HANDICAP_RAMP = "Handicap Ramp (vehicle blocking handicap ramp)"
    SIDEWALK = "Sidewalk"


class OccuranceFrequency(StrEnum):
    NOT_FREQUENTLY = "Not Frequently"
    SOMEWHAT_OFTEN = "Somewhat Often"
    FREQUENTLY = "Frequently"
    UNSURE = "Unsure"


class VehicleType(StrEnum):
    COUPE = "Coupe (2 door car)"
    SEDAN = "Sedan (4 door car)"
    PICKUP_TRUCK = "Pickup Truck"
    BOX_TRUCK = "Box-Truck"
    SUV = "SUV"
    MINIVAN = "Minivan"
    VAN = "Van"
    BUS = "Bus"
    MOTORCYCLE = "Motorcycle"
    DIRT_BIKE = "Dirt Bike"
    ATV = "ATV"
    TRACTOR = "Tractor"
    TRAILER = "Trailer"
    TOW_TRUCK = "Tow-Truck"
    FLATBED = "Flatbed"
    CAMPER = "Camper"
    RV = "RV"
    BOAT = "Boat"
    CONSTRUCTION_EQUIPMENT = "Construction Equipment"
    UNKNOWN = "Unknown"

    @classmethod
    def find_closest(cls, vehicle_type: str) -> "VehicleType":
        """Finds the closest VehicleType based on the provided vehicle type string."""
        vehicle_type = vehicle_type.lower()
        for vt in cls:
            if vehicle_type in vt.value.lower():
                return vt
        return cls.UNKNOWN


class VehicleColor(StrEnum):
    RED = "Red"
    BLUE = "Blue"
    GREEN = "Green"
    YELLOW = "Yellow"
    PURPLE = "Purple"
    PINK = "Pink"
    ORANGE = "Orange"
    BROWN = "Brown"
    BLACK = "Black"
    WHITE = "White"
    GRAY = "Gray"
    GOLD = "Gold"
    SILVER = "Silver"
    TEAL = "Teal"
    MAGENTA = "Magenta"
    VIOLET = "Violet"
    CYAN = "Cyan"
    MAROON = "Maroon"
    BEIGE = "Beige"
    OTHER = "Other"

    @classmethod
    def find_closest(cls, vehicle_color: str) -> "VehicleColor":
        """Finds the closest VehicleType based on the provided vehicle type string."""
        vehicle_color = vehicle_color.lower()
        for vc in cls:
            if vehicle_color in vc.value.lower():
                return vc
        return cls.OTHER


@dataclass
class MobilityAccessViolation:
    date_time_observed: datetime
    make: str
    address: str
    body_style: VehicleType
    vehicle_color: VehicleColor
    violation_observed: ViolationObserved

    # optional fields
    model: str = ""
    additional_information: str = ""
    # maybe b64 encoded?
    picture: str = ""

    parsed_address: pyap.Address = field(init=False)

    def __post_init__(self):
        """Post-initialization to parse the address."""
        parsed_addresses = pyap.parse(self.address, country="US")
        if (
            len(parsed_addresses) != 1
            or parsed_addresses[0].street_name is None
            or parsed_addresses[0].street_type is None
            or parsed_addresses[0].postal_code is None
        ):
            raise ValueError(f"address could not be parsed: {self.address}")
        self.parsed_address = parsed_addresses[0]
        # convert to est
        est = pytz.timezone("US/Eastern")
        self.date_time_observed = self.date_time_observed.astimezone(est)

    # street name here is a dropdown, not a free form.
    # block_number: int
    # street_name: str
    # example address: Wharton Square Park, 2300 Wharton St, Philadelphia, PA 19146, USA
    @property
    def block_number(self) -> int:
        """Returns the block number from the address."""
        return self.parsed_address.street_number  # type: ignore

    @property
    def street_name(self) -> str:
        """Returns the street name from the address."""
        return (
            self.parsed_address.street_name.upper()  # type: ignore
            + " "
            + self.parsed_address.street_type.upper()  # type: ignore
        )

    @property
    def zip_code(self) -> str:
        """Returns the zip code from the address."""
        return self.parsed_address.postal_code  # type: ignore

    @property
    def date_observed(self) -> str:
        """Returns the date part of the observed datetime."""
        return self.date_time_observed.strftime("%m/%d/%Y")

    @property
    def time_observed(self) -> str:
        """Returns the time part of the observed datetime."""
        # Return the time in EST (should this be 24 hour format?)
        return self.date_time_observed.strftime("%I:%M %p")

    @classmethod
    def from_json(cls, data: dict) -> "MobilityAccessViolation":
        """Creates a MobilityAccessViolation instance from a JSON-like dictionary."""
        vehicle = data.get("vehicle", {})
        if not vehicle:
            raise ValueError(
                "Vehicle data is required to create a MobilityAccessViolation."
            )
        if "timestamp" not in data or "address" not in data:
            raise ValueError("Timestamp and address are required fields.")
        plate = (
            vehicle.get("plate", {})
            .get("props", {})
            .get("plate", {})[0]
            .get("value", "")
        )
        region = (
            vehicle.get("plate", {})
            .get("props", {})
            .get("region", {})[0]
            .get("value", "")
        )
        # override to make it easier
        vehicle = vehicle.get("vehicle", {})

        vehicle_type = vehicle.get("type", "")
        body_style = VehicleType.find_closest(vehicle_type)

        props = vehicle.get("props")

        make_model = props.get("make_model", {})[0]
        make = make_model.get("make", "")
        model = make_model.get("model", "")
        color = props.get("color", "")[0].get("value", "")
        vehicle_color = VehicleColor.find_closest(color)

        return cls(
            date_time_observed=datetime.fromisoformat(data["timestamp"]),
            make=make,
            model=model,
            body_style=body_style,
            vehicle_color=vehicle_color,
            additional_information=f"License Plate: {plate} ({region})",
            # not sure which one to select here...
            violation_observed=ViolationObserved.CROSSWALK,  # type: ignore
            address=data["address"],
            # picture=data.get("picture", ""),
        )


async def submit_form_with_playwright(
    violation: MobilityAccessViolation, photo: str | ContentFile
) -> None:
    """Method to submit a violation to the PPA's Smartsheet using Playwright.

    Args:
        violation (MobilityAccessViolation): The description of the violation to submit.
    """
    # smartsheet allows pre-filling of fields using query parameters.
    # for example, date observed would be Date%20Observed=06/03/2025

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Construct the URL with query parameters
        params = {
            "Date Observed": violation.date_observed,
            "Time Observed": violation.time_observed,
            "Make": violation.make,
            "Model": violation.model,
            "Body Style": violation.body_style,
            "Vehicle Color": violation.vehicle_color,
            "Violation Observed": violation.violation_observed.value,
            "Block Number": violation.block_number,
            "Street Name": violation.street_name,
            "Zip Code": violation.zip_code,
            "How frequently does this occur?": OccuranceFrequency.UNSURE,
            "Additional Information": violation.additional_information,
            # not sure how to do "send me a copy of my responses"
        }
        url_parts = urllib.parse.urlparse(PPA_SMARTSHEET_URL)
        query = dict(urllib.parse.parse_qsl(url_parts.query))
        query.update(params)  # type: ignore

        full_url = url_parts._replace(query=urllib.parse.urlencode(query)).geturl()

        page.goto(full_url)
        # wait for the form to load
        page.wait_for_load_state("networkidle")

        # click the file chooser
        with page.expect_file_chooser() as fc_info:
            page.get_by_text("browse files").click()
        file_chooser = fc_info.value
        if isinstance(photo, str):
            file_chooser.set_files(photo)
        elif isinstance(photo, ContentFile):
            upload = FilePayload(
                name=getattr(photo, "name", "violation_photo.jpg"),
                mimeType="image/jpeg",
                buffer=photo.read(),  # limit how much we read?
            )

            file_chooser.set_files(upload)

        # submit the form
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")

        context.close()
        browser.close()
