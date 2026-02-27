import json
from urllib.request import Request, urlopen

BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"


def fetch_bls_data(series_ids, start_year, end_year, registration_key):
    payload = {
        "seriesid": series_ids,
        "startyear": str(start_year),
        "endyear": str(end_year),
        "registrationkey": registration_key,
    }

    req = Request(
        BLS_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(req, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))

    if data.get("status") != "REQUEST_SUCCEEDED":
        messages = "; ".join(data.get("message", ["Unknown BLS API error"]))
        raise ValueError(messages)

    return data.get("Results", {}).get("series", [])
