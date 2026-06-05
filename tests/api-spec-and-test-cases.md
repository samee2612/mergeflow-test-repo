```markdown
# API Analysis Document for MergeFlow PR #41

## 1. Change Summary

This PR refactors the login API by removing the `remember_me` functionality and simplifying the response. The `remember_me` field has been removed from the `LoginRequest` schema and is no longer accepted in the request payload. Consequently, the `expires_in` field has been removed from the `LoginResponse` schema and the `authenticate_user` service function. The API now only returns a `token` and `token_type` upon successful login.

## 2. Endpoint(s) Detected

*   **Login Endpoint**
    *   Method: `POST`
    *   Path: `/login`
    *   Feature Area: Authentication

## 3. Directly Related Files Considered

*   `backend/routes/auth.py`
*   `backend/schemas/auth.py`
*   `backend/services/auth_service.py`

## 4. API Specification Snapshot

### Endpoint: Login

*   **Operation Name:** `login`
*   **Method:** `POST`
*   **Path:** `/login`
*   **Tags:** `auth`
*   **Summary:** Log in with email and password.
*   **Auth Requirement:** Not specified, assumed none for login.
*   **Parameters:**
    *   Path Parameters: None
    *   Query Parameters: None
*   **Headers Required:** None explicitly mentioned, but `Content-Type: application/json` is implied for POST requests with a body.
*   **Request Body:**
    *   **Schema:**
        ```json
        {
          "type": "object",
          "properties": {
            "email": {
              "title": "Email",
              "description": "Email address for the account attempting to log in.",
              "example": "admin@example.com",
              "type": "string"
            },
            "password": {
              "title": "Password",
              "description": "Plain text password submitted by the user.",
              "example": "correct-horse-battery-staple",
              "type": "string",
              "minLength": 8
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
*   **Env Vars Needed:** `AUTH_TOKEN_ISSUER` (optional, defaults to "mergeflow-test")
*   **Direct Dependencies / Related Files:**
    *   `backend/schemas/auth.py` (for `LoginRequest`, `LoginResponse`, `ErrorResponse`)
    *   `backend/services/auth_service.py` (for `authenticate_user`)
*   **Responses:**
    *   **200 OK:**
        *   **Description:** Login succeeded and returned a bearer token.
        *   **Response Body Shape:**
            ```json
            {
              "token": "string",
              "token_type": "string"
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
        *   **Description:** The request body is missing required fields or contains invalid values.
        *   **Response Body Shape:**
            ```json
            {
              "detail": "string"
            }
            ```
        *   **Example Error Response:**
            ```json
            {"detail": "Email and password are required."}
            ```
            or
            ```json
            {"detail": "Email and password are required and must be valid."}
            ```
    *   **401 Unauthorized:**
        *   **Description:** The supplied email and password do not match a known user.
        *   **Response Body Shape:**
            ```json
            {
              "detail": "string"
            }
            ```
        *   **Example Error Response:**
            ```json
            {"detail": "Invalid email or password."}
            ```

## 5. Test Cases

### Happy Path

*   **Test Case:** Successful login with valid credentials.
*   **Description:** Send a POST request to `/login` with a valid email and password.
*   **Request:**
    ```http
    POST /login HTTP/1.1
    Host: example.com
    Content-Type: application/json

    {
      "email": "admin@example.com",
      "password": "correct-horse-battery-staple"
    }
    ```
*   **Expected Response:**
    *   Status Code: `200 OK`
    *   Body: A JSON object containing `token` and `token_type`.
        ```json
        {
          "token": "mergeflow-test-token-for-admin-user",
          "token_type": "bearer"
        }
        ```

### Missing Required Field

*   **Test Case:** Login with missing email.
*   **Description:** Send a POST request to `/login` with only a password.
*   **Request:**
    ```http
    POST /login HTTP/1.1
    Host: example.com
    Content-Type: application/json

    {
      "password": "correct-horse-battery-staple"
    }
    ```
*   **Expected Response:**
    *   Status Code: `400 Bad Request`
    *   Body: `{"detail": "Email and password are required."}`

*   **Test Case:** Login with missing password.
*   **Description:** Send a POST request to `/login` with only an email.
*   **Request:**
    ```http
    POST /login HTTP/1.1
    Host: example.com
    Content-Type: application/json

    {
      "email": "admin@example.com"
    }
    ```
*   **Expected Response:**
    *   Status Code: `400 Bad Request`
    *   Body: `{"detail": "Email and password are required."}`

### Invalid Input

*   **Test Case:** Login with invalid email format.
*   **Description:** Send a POST request to `/login` with an improperly formatted email.
*   **Request:**
    ```http
    POST /login HTTP/1.1
    Host: example.com
    Content-Type: application/json

    {
      "email": "invalid-email",
      "password": "correct-horse-battery-staple"
    }
    ```
*   **Expected Response:**
    *   Status Code: `400 Bad Request`
    *   Body: `{"detail": "Email and password are required and must be valid."}`

*   **Test Case:** Login with password shorter than minimum length.
*   **Description:** Send a POST request to `/login` with a password shorter than 8 characters.
*   **Request:**
    ```http
    POST /login HTTP/1.1
    Host: example.com
    Content-Type: application/json

    {
      "email": "admin@example.com",
      "password": "short"
    }
    ```
*   **Expected Response:**
    *   Status Code: `400 Bad Request`
    *   Body: `{"detail": "Email and password are required and must be valid."}`

### Unauthorized / Forbidden

*   **Test Case:** Login with incorrect password.
*   **Description:** Send a POST request to `/login` with a valid email but incorrect password.
*   **Request:**
    ```http
    POST /login HTTP/1.1
    Host: example.com
    Content-Type: application/json

    {
      "email": "admin@example.com",
      "password": "wrong-password"
    }
    ```
*   **Expected Response:**
    *   Status Code: `401 Unauthorized`
    *   Body: `{"detail": "Invalid email or password."}`

*   **Test Case:** Login with non-existent email.
*   **Description:** Send a POST request to `/login` with an email not in the user store.
*   **Request:**
    ```http
    POST /login HTTP/1.1
    Host: example.com
    Content-Type: application/json

    {
      "email": "nonexistent@example.com",
      "password": "any-password"
    }
    ```
*   **Expected Response:**
    *   Status Code: `401 Unauthorized`
    *   Body: `{"detail": "Invalid email or password."}`

### Edge Cases

*   **Test Case:** Login with empty payload.
*   **Description:** Send a POST request to `/login` with an empty JSON body.
*   **Request:**
    ```http
    POST /login HTTP/1.1
    Host: example.com
    Content-Type: application/json

    {}
    ```
*   **Expected Response:**
    *   Status Code: `400 Bad Request`
    *   Body: `{"detail": "Email and password are required."}`

*   **Test Case:** Login with `null` payload.
*   **Description:** Send a POST request to `/login` with a `null` body.
*   **Request:**
    ```http
    POST /login HTTP/1.1
    Host: example.com
    Content-Type: application/json

    null
    ```
*   **Expected Response:**
    *   Status Code: `400 Bad Request`
    *   Body: `{"detail": "Email and password are required."}`

*   **Test Case:** Login with email containing leading/trailing spaces.
*   **Description:** Send a POST request to `/login` with an email that has spaces.
*   **Request:**
    ```http
    POST /login HTTP/1.1
    Host: example.com
    Content-Type: application/json

    {
      "email": "  admin@example.com  ",
      "password": "correct-horse-battery-staple"
    }
    ```
*   **Expected Response:**
    *   Status Code: `200 OK`
    *   Body: A JSON object containing `token` and `token_type`. (The service normalizes the email).

## 6. Edge Cases

*   **Empty Payload:** The API correctly handles an empty JSON payload or a `null` body by returning a `400 Bad Request` with a "Email and password are required." message.
*   **Whitespace in Email:** The `authenticate_user` function in `auth_service.py` strips and lowercases the email, so leading/trailing whitespace in the email address should be handled correctly.
*   **Case Sensitivity of Email:** The `authenticate_user` function converts the email to lowercase, making the email lookup case-insensitive.

## 7. Regression Risks

*   **Removal of `remember_me`:** Any existing clients or integrations that relied on the `remember_me` flag for longer-lived tokens will be broken. They will now receive standard-duration tokens.
*   **Removal of `expires_in` from Response:** Clients expecting the `expires_in` field in the `LoginResponse` will encounter errors. This field is no longer provided.
*   **Simplified Error Messages:** While not explicitly stated as a change, the removal of specific examples in the `responses` section of the route might imply a simplification of error reporting, which could be a minor regression if detailed error messages were previously relied upon.

## 8. Swagger/OpenAPI-Ready Notes

*   The `login` endpoint is well-defined and can be directly translated into an OpenAPI operation.
*   The request body schema (`LoginRequest`) and response body schema (`LoginResponse`, `ErrorResponse`) are clearly defined using Pydantic models, which map well to OpenAPI schemas.
*   The `responses` section in the route definition provides clear status codes and descriptions, which can be used for OpenAPI `responses`.
*   The `summary` field in the route decorator is suitable for the OpenAPI `summary` field.
*   The `tags` field is present and can be used for OpenAPI `tags`.
*   The removal of `remember_me` from the request and `expires_in` from the response simplifies the OpenAPI definition.
*   Consider adding explicit `securitySchemes` if authentication is introduced later, though for login it's typically not required.
*   The `Content-Type: application/json` header is implicitly handled by FastAPI for POST requests with a JSON body and doesn't need explicit mention in the OpenAPI spec unless custom handling is involved.
```
