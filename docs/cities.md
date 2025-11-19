# Cities API (draft)

This document sketches the intended contract for **cities** endpoints.
These routes will support CRUD operations and integrate with the shared
`validate_city_payload` helper.

## Endpoints

- `GET /api/v1/cities` — list cities (supports future pagination/filtering)
- `POST /api/v1/cities` — create a city (requires: `name`, `state_id`, `country_id`; optional: `population`)
- `GET /api/v1/cities/{city_id}` — fetch one city
- `PUT /api/v1/cities/{city_id}` — replace a city
- `PATCH /api/v1/cities/{city_id}` — partial update
- `DELETE /api/v1/cities/{city_id}` — delete a city

## Minimal OpenAPI (to be merged into the main spec)
```yaml
openapi: 3.0.3
info:
  title: RJRTM Cities API
  version: 0.1.0
paths:
  /api/v1/cities:
    get:
      summary: List cities
      responses:
        "200":
          description: OK
          content:
            application/json:
              schema:
                type: array
                items: { $ref: '#/components/schemas/City' }
    post:
      summary: Create a city
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: '#/components/schemas/CityCreate' }
      responses:
        "201":
          description: Created
          content:
            application/json:
              schema: { $ref: '#/components/schemas/City' }
  /api/v1/cities/{city_id}:
    get:
      summary: Get a city
      parameters:
        - in: path
          name: city_id
          required: true
          schema: { type: string }
      responses:
        "200":
          description: OK
          content:
            application/json:
              schema: { $ref: '#/components/schemas/City' }
    put:
      summary: Replace a city
      parameters:
        - in: path
          name: city_id
          required: true
          schema: { type: string }
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: '#/components/schemas/CityCreate' }
      responses:
        "200":
          description: OK
    patch:
      summary: Update a city
      parameters:
        - in: path
          name: city_id
          required: true
          schema: { type: string }
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              additionalProperties: true
      responses:
        "200": { description: OK }
    delete:
      summary: Delete a city
      parameters:
        - in: path
          name: city_id
          required: true
          schema: { type: string }
      responses:
        "204": { description: No Content }

components:
  schemas:
    CityBase:
      type: object
      properties:
        name: { type: string, example: "Queens" }
        state_id: { type: string, example: "NY" }
        country_id: { type: string, example: "US" }
        population: { type: integer, minimum: 0, example: 2400000 }
    CityCreate:
      allOf:
        - $ref: '#/components/schemas/CityBase'
      required: [name, state_id, country_id]
    City:
      allOf:
        - $ref: '#/components/schemas/CityBase'
      properties:
        id: { type: string, example: "c_01HZX2M1KZ6A" }
