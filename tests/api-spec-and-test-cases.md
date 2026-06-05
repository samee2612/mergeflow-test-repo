# API Analysis Document - MergeFlow PR 39

## 1. Change Summary

This PR introduces a new API endpoint for user login. It includes request validation using Pydantic schemas, authentication logic against an in-memory user store, and returns a bearer token upon successful authentication. Error handling for missing fields, invalid input, and incorrect credentials is also implemented.

## 2. Endpoint(s) Detected

*   **Name:** `login`
*   **HTTP Method:** `POST`
*   **Path:** `/login`
*   **Tags:** `auth`
*   **Summary:** Log in with email and password

## 3. Directly Related Files Considered

*   `backend/routes/auth.py`
*   `backend/schemas/auth.py`
*   `backend/services/auth_service.py`

## 4. API Specification Snapshot

### Endpoint: `login`

*   **method:** `POST`
*   **path:** `/login`
*   **tags:** `auth`
*   **summary:** Log in with email and password
*   **auth:** Not detected from provided context (assumed to be public for login)
*   **parameters:**
    *   **Path Parameters:** None
    *   **Query Parameters:** None
*   **request body:**
    *   **Schema:**
        ```json
        {
          "type": "object",
          "properties": {
            "email": {
              "type": "string",
              "format": "email",
              "description": "Email address for the account attempting to log in.",
              "example": "admin@example.com"
            },
            "password": {
              "type": "string",
              "minLength": 8,
              "description": "Plain text password submitted by the user.",
              "example": "correct-horse-battery-staple"
            }
          },
          "required": ["email", "password"]
        }
        ```
    *   **Example Request Body:**
        ```json
        {
          "email": "admin@example.com",
          "password": "correct-horse-battery-staple"
        }
        ```
*   **headers:** None explicitly required by the endpoint definition, but `Content-Type: application/json` is implied for POST requests with a JSON body.
*   **env vars:** `AUTH_TOKEN_ISSUER` (optional, defaults to "mergeflow-test")
*   **responses:**
    *   **200 OK:**
        *   **Schema:**
            ```json
            {
              "type": "object",
              "properties": {
                "token": {
                  "type": "string",
                  "description": "Bearer token returned after successful authentication.",
                  "example": "demo-token-for-admin-user"
                },
                "token_type": {
                  "type": "string",
                  "default": "bearer",
                  "description": "Token type clients should use in the Authorization header.",
                  "example": "bearer"
                }
              },
              "required": ["token", "token_type"]
            }
            ```
        *   **Example Successful Response:**
            ```json
            {
              "token": "mergeflow-test-token-for-admin-user",
              "token_type": "bearer"
            }
            ```
    *   **400 Bad Request:**
        *   **Schema:**
            ```json
            {
              "type": "object",
              "properties": {
                "detail": {
                  "type": "string",
                  "description": "Human-readable error explaining why login failed.",
                  "example": "Email and password are required."
                }
              },
              "required": ["detail"]
            }
            ```
        *   **Example Error Response (Missing Fields):**
            ```json
            {
              "detail": "Email and password are required."
            }
            ```
        *   **Example Error Response (Invalid Values):**
            ```json
            {
              "detail": "Email and password are required and must be valid."
            }
            ```
    *   **401 Unauthorized:**
        *   **Schema:**
            ```json
            {
              "type": "object",
              "properties": {
                "detail": {
                  "type": "string",
                  "description": "Human-readable error explaining why login failed.",
                  "example": "Invalid email or password."
                }
              },
              "required": ["detail"]
            }
            ```
        *   **Example Error Response:**
            ```json
            {
              "detail": "Invalid email or password."
            }
            ```
*   **Direct Dependencies / Related Files:**
    *   `backend/schemas/auth.py` (for `LoginRequest`, `LoginResponse`, `ErrorResponse`)
    *   `backend/services/auth_service.py` (for `authenticate_user`)

## 5. Test Cases

### Happy Path

*   **Test Case:** Successful login with valid credentials.
*   **Request:**
    ```http
    POST /login
    Content-Type: application/json

    {
      "email": "admin@example.com",
      "password": "correct-horse-battery-staple"
    }
    ```
*   **Expected Response:**
    *   Status Code: `200 OK`
    *   Body: A JSON object containing a `token` and `token_type` (e.g., `{"token": "mergeflow-test-token-for-admin-user", "token_type": "bearer"}`).

### Error Cases

*   **Test Case:** Missing request body.
*   **Request:**
    ```http
    POST /login
    Content-Type: application/json

    {}
    ```
*   **Expected Response:**
    *   Status Code: `400 Bad Request`
    *   Body: `{"detail": "Email and password are required."}`

*   **Test Case:** Missing `email` field.
*   **Request:**
    ```http
    POST /login
    Content-Type: application/json

    {
      "password": "somepassword"
    }
    ```
*   **Expected Response:**
    *   Status Code: `400 Bad Request`
    *   Body: `{"detail": "Email and password are required and must be valid."}`

*   **Test Case:** Missing `password` field.
*   **Request:**
    ```http
    POST /login
    Content-Type: application/json

    {
      "email": "admin@example.com"
    }
    ```
*   **Expected Response:**
    *   Status Code: `400 Bad Request`
    *   Body: `{"detail": "Email and password are required and must be valid."}`

*   **Test Case:** Invalid email format.
*   **Request:**
    ```http
    POST /login
    Content-Type: application/json

    {
      "email": "invalid-email",
      "password": "correct-horse-battery-staple"
    }
    ```
*   **Expected Response:**
    *   Status Code: `400 Bad Request`
    *   Body: `{"detail": "Email and password are required and must be valid."}`

*   **Test Case:** Password too short.
*   **Request:**
    ```http
    POST /login
    Content-Type: application/json

    {
      "email": "admin@example.com",
      "password": "short"
    }
    ```
*   **Expected Response:**
    *   Status Code: `400 Bad Request`
    *   Body: `{"detail": "Email and password are required and must be valid."}`

*   **Test Case:** Incorrect password.
*   **Request:**
    ```http
    POST /login
    Content-Type: application/json

    {
      "email": "admin@example.com",
      "password": "wrong-password"
    }
    ```
*   **Expected Response:**
    *   Status Code: `401 Unauthorized`
    *   Body: `{"detail": "Invalid email or password."}`

*   **Test Case:** Non-existent email.
*   **Request:**
    ```http
    POST /login
    Content-Type: application/json

    {
      "email": "nonexistent@example.com",
      "password": "any-password"
    }
    ```
*   **Expected Response:**
    *   Status Code: `401 Unauthorized`
    *   Body: `{"detail": "Invalid email or password."}`

## 6. Edge Cases

*   **Email Case Sensitivity:** The `authenticate_user` function normalizes the email to lowercase (`email.strip().lower()`). Therefore, `Admin@example.com` should be treated the same as `admin@example.com`.
    *   **Test Case:** Login with mixed-case email.
    *   **Request:**
        ```http
        POST /login
        Content-Type: application/json

        {
          "email": "Admin@example.com",
          "password": "correct-horse-battery-staple"
        }
        ```
    *   **Expected Response:** `200 OK` with a valid token.

*   **Whitespace in Email:** The `authenticate_user` function also strips whitespace from the email.
    *   **Test Case:** Login with email containing leading/trailing whitespace.
    *   **Request:**
        ```http
        POST /login
        Content-Type: application/json

        {
          "email": "  admin@example.com  ",
          "password": "correct-horse-battery-staple"
        }
        ```
    *   **Expected Response:** `200 OK` with a valid token.

*   **Empty Request Body:** The route handler explicitly checks for `payload is None`.
    *   **Test Case:** Sending an empty POST request without a body.
    *   **Request:**
        ```http
        POST /login
        ```
    *   **Expected Response:** `400 Bad Request` with `{"detail": "Email and password are required."}`.

## 7. Regression Risks

*   **Changes to `authenticate_user` logic:** Any modification to the `authenticate_user` function in `auth_service.py` could break the login flow.
*   **Changes to Pydantic schemas:** Altering the `LoginRequest` schema (e.g., removing `min_length` for password, changing field names) without updating the route handler would cause validation errors.
*   **Changes to `ErrorResponse` schema:** If the `ErrorResponse` schema is modified, the documented error responses might not match the actual output.
*   **Removal of `auth` tag:** If the `tags=["auth"]` is removed from the router, the endpoint might not be correctly categorized in generated API documentation.

## 8. Swagger/OpenAPI-Ready Notes

*   The `POST /login` endpoint is well-defined with clear request and response models.
*   The `responses` dictionary in the route handler directly maps to OpenAPI `responses` objects, including schema definitions for `400` and `401`.
*   The `summary` and `description` fields in the route handler and Pydantic models can be directly mapped to OpenAPI `summary` and `description` fields.
*   The `tags=["auth"]` can be used for OpenAPI `tags`.
*   The `LoginRequest` and `LoginResponse` Pydantic models can be directly translated into OpenAPI `schemas`.
*   The `ErrorResponse` Pydantic model can also be translated into an OpenAPI `schema`.
*   The `AUTH_TOKEN_ISSUER` environment variable is used but not explicitly documented as a parameter or header, which is typical for environment variables. It should be noted in the documentation for deployment.
*   The `response_model` in the route decorator directly informs the `responses.200.content.application/json.schema` in OpenAPI.
*   The `Body(default=None)` and subsequent `if payload is None:` check can be represented by making the entire request body optional in OpenAPI, but the internal logic enforces its presence and structure. The Pydantic `LoginRequest` schema with `...` for fields implies they are required.
