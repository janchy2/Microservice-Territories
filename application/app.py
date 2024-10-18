from fastapi import FastAPI, Path, Body
from application.create_functions import create_request
from application.update_functions import update_request
from application.delete_functions import delete_request
from application.retrieve_functions import retrieve_request
from application.common_functions import generate_response

app = FastAPI()


@app.post("/territories")
def create_resource(body: dict = Body(...)):
    return create_request(body)


@app.patch("/territories")
def update_resource(body: dict = Body(...)):
    return update_request(body)


@app.delete("/territories/{uuid}")
def delete_resource(uuid: str = Path(...)):
    return delete_request({"uuid": uuid})


@app.get("/territories/{uuid}")
def retrieve_resource(uuid: str = Path(...)):
    return retrieve_request({"uuid": uuid})


@app.get("/")
def read_root():
    return generate_response(400, "Method not supported!")
