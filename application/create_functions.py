import uuid
from typing import List, Dict, Any, Optional
from application.common_functions import generate_response, connect_to_database
from fastapi.responses import JSONResponse


def create_request(body: Dict[str, Any]) -> JSONResponse:
    territory_data: Optional[Dict[str, str]] = extract_data(body)
    if not territory_data:
        return generate_response(400, "Invalid or incomplete territory data!")

    table = connect_to_database()
    levels: List[str] = [
        "administrative_area_1",
        "administrative_area_2",
        "locality",
        "postal_code",
    ]
    path: str = "RS"  # root is RS - we need it because of the secondary index

    for level in levels:
        element_id: Optional[str] = check_if_element_exists(
            table, territory_data[level], level
        )
        if element_id and level == "postal_code":
            # element already exists, conflict
            return generate_response(409, "Postal code already exists!")
        if not element_id:
            element_id = create_element(table, territory_data[level], level, path)
        path += "#" + element_id

    return generate_response(201, "Territory created successfully!")


def extract_data(body: Dict[str, Any]) -> Optional[Dict[str, str]]:
    # body is the response from Google Geoencoder
    if "results" in body and len(body["results"]):
        result = body["results"][0]
        address_components = result.get("address_components", [])
        territory_data: Dict[str, str] = {}

        for component in address_components:
            if "locality" in component["types"]:
                territory_data["locality"] = component["long_name"]
            elif "administrative_area_level_2" in component["types"]:
                territory_data["administrative_area_2"] = component["long_name"]
            elif "administrative_area_level_1" in component["types"]:
                territory_data["administrative_area_1"] = component["long_name"]
            elif "postal_code" in component["types"]:
                territory_data["postal_code"] = component["long_name"]
            elif "country" in component["types"]:
                territory_data["country"] = component["long_name"]

        if len(territory_data) == 5 and territory_data["country"] == "Serbia":
            # all attributes present and territory belongs to Serbia
            return territory_data
    return None


def check_if_element_exists(table: Any, name: str, type: str) -> Optional[str]:
    response = table.scan(
        FilterExpression="territory_name = :name_value AND territory_type = :type_value",
        ExpressionAttributeValues={":name_value": name, ":type_value": type},
    )

    if response["Items"]:
        # element exists
        return response["Items"][0]["uuid"]
    return None


def create_element(table: Any, name: str, type: str, path: str) -> str:
    uuid = generate_uuid()
    item_data = {
        "uuid": uuid,
        "territory_name": name,
        "territory_type": type,
        "territory_path": path,
    }
    table.put_item(Item=item_data)
    return uuid


def generate_uuid() -> str:
    # create UUID v4 and extract the last part
    generated_uuid = uuid.uuid4()
    uuid_str = str(generated_uuid)
    return uuid_str.split("-")[-1]
