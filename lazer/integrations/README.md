## Submit PPA Smartsheet

The `submit_form.py` contains all necessary tools to submit the form to PPA's Smartsheet. It uses Playwright to open a browser with the form.
The form is pre-filled using [Smartsheet query string](https://help.smartsheet.com/articles/2478871-url-query-string-form-default-values).

The form has a few dropdowns that only accept exact values, otherwise pre-fill doesn't work. Those are enums `ViolationObserved`, `OccuranceFrequency`, `VehicleType`, and `VehicleColor`.

The address returned by plate/car recognition API is a full address, while the form accepts "street number", "block", and "zip code". The address is parsed using [pyap2](https://pypi.org/project/pyap2/) (actively maintained fork of `pyap`).

The `MobilityAccessViolation` has a handy `from_json` call that takes in the API returned object.

> Note: Not sure if the Photo, "Email me with the copy", and the email itself can be pre-filled.
