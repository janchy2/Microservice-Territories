A microservice for managing territories in Serbia, made using **FastAPI**, that runs in a **Docker** container. The microservice uses a **DynamoDB** database that runs locally inside a container.  
The territories are stored in a hierarchy using **materialized path pattern** - each path starts with RS (for Serbia) and contains UUIDs of ancestor territories. The hierarchy levels are:
- administrative area 1
- administrative area 2
- locality
- postal code

It supports **CRUD** operations with the following API:
* POST /territories - adds a new territory to the hierarchy
    * body must contain JSON response from *Google Geoencoder API*
    * that response must contain attributes administrative_area_1, administrative_area_2, locality and postal_code
* PATCH /territories - updates the locality of the postal code or the administrative area 2 of postal code and its locality
    * body must contain UUID of postal code that should be updated and UUID of new territory - locality or administrative area 2
* DELETE /territories/{uuid} - deletes a territory with the given UUID if it does not have subterritories
* GET /territories/{uuid} - retrieves a territory with the given UUID and all its subterritories

Black, Ruff and MyPy are used for linting, formatting and type-checking.  
Unit tests for each endpoint are given in the folder tests.
