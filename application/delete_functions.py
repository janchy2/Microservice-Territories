from typing import Dict, Any, Optional
from boto3.dynamodb.conditions import Attr
from application.common_functions import generate_response, connect_to_database
from fastapi.responses import JSONResponse


def delete_request(parameters: Dict[str, Any]) -> JSONResponse:
    table = connect_to_database()
    element: Optional[Dict[str, Any]] = get_element(table, parameters["uuid"])

    if not element:
        return generate_response(404, "Non-existent uuid!")

    if has_children(table, element):
        return generate_response(
            409, "Territory has subterritories, it cannot be deleted!"
        )

    delete_element(table, element)
    return generate_response(200, "Territory deleted successfully!")


def get_element(table: Any, uuid: str) -> Optional[Dict[str, Any]]:
    response = table.get_item(Key={"uuid": uuid})
    return response.get("Item")


def has_children(table: Any, element: Dict[str, Any]) -> bool:
    response = table.scan(
        FilterExpression=Attr("territory_path").begins_with(
            element["territory_path"] + "#" + element["uuid"] + "#"
        )
    )
    return bool(response.get("Items", []))


def delete_element(table: Any, element: Dict[str, Any]) -> None:
    table.delete_item(Key={"uuid": element["uuid"]})
