# API Analysis: MergeFlow PR 40

## 1. Change Summary

This PR enhances the existing `/login` API endpoint. The primary change is the addition of a `remember_me` boolean field to the login request payload. This flag, when set to `True`, instructs the service to issue a longer-lived authentication token (86400 seconds) compared to the default token (3600 seconds). The `LoginResponse` model has been updated to include an `expires_in` field to communicate the token's validity period to the client.

## 2. Endpoint(s) Detected

### POST /login

*   **Operation Name:** `login`
*   **Feature Area:** Authentication
*   **Summary:** Log in with email and password, with an option to extend token expiration.
*   **Auth Required:** No (This is the login endpoint itself)

## 3. Directly Related Files Considered

*   `backend/routes/auth.py`: Defines the `/login` API route and its handler function.
*   `backend/schemas/auth.py`: Defines the Pydantic models for `LoginRequest` and `LoginResponse`.
*   `backend/services/auth_service.py`: Contains the `authenticate_user` function, which now accepts the `remember_me` parameter.

## 4. API Specification Snapshot

### POST /login

*   **method:** `POST`
*   **path:** `/login`
*   **tags:** `auth`
*   **summary:** Log in with email and password
*   **auth:** Not detected from provided context (This is the authentication endpoint)
*   **parameters:**
    *   **Path Parameters:** None
    *   **Query Parameters:** None
    *   **Headers:**
        *   `X-Request-ID` (Optional, string): Optional client-generated request ID for tracing login attempts.
*   **request body:**
    *   **Schema:** `LoginRequest` (from `backend/schemas/auth.py`)
    *   **Example:**
        ```json
        {
          "email": "admin@example.com",
          "password": "correct-horse-battery-staple",
          "remember_me": true
        }
        ```
*   **env vars:**
    *   `AUTH_TOKEN_ISSUER` (Optional, string): Used to prefix the generated token. Defaults to "mergeflow-test".
*   **responses:**
    *   **200 OK:**
        *   **Description:** Login succeeded and returned a bearer token.
        *   **Response Body Schema:** `LoginResponse`
        *   **Example:**
            ```json
            {
              "token": "mergeflow-test-token-for-admin-user",
              "token_type": "bearer",
              "expires_in": 86400
            }
            ```
    *   **400 Bad Request:**
        *   **Description:** The request body is missing required fields or contains invalid values.
        *   **Response Body Schema:** `ErrorResponse`
        *   **Example:**
            ```json
            {
              "detail": "Email and password are required and must be valid."
            }
            ```
    *   **401 Unauthorized:**
        *   **Description:** The supplied email and password do not match a known user.
        *   **Response Body Schema:** `ErrorResponse`
        *   **Example:**
            ```json
            {
              "detail": "Invalid email or password."
            }
            ```

## 5. Test Cases

### Happy Path

1.  **Test Case:** Successful login with `remember_me: false` (default).
    *   **Request:** `POST /login` with `{"email": "admin@example.com", "password": "correct-horse-battery-staple"}`.
    *   **Expected Response:** `200 OK` with a `LoginResponse` containing a token and `expires_in: 3600`.
2.  **Test Case:** Successful login with `remember_me: true`.
    *   **Request:** `POST /login` with `{"email": "admin@example.com", "password": "correct-horse-battery-staple", "remember_me": true}`.
    *   **Expected Response:** `200 OK` with a `LoginResponse` containing a token and `expires_in: 86400`.
3.  **Test Case:** Successful login with `remember_me: false` explicitly.
    *   **Request:** `POST /login` with `{"email": "admin@example.com", "password": "correct-horse-battery-staple", "remember_me": false}`.
    *   **Expected Response:** `200 OK` with a `LoginResponse` containing a token and `expires_in: 3600`.
4.  **Test Case:** Successful login with `X-Request-ID` header.
    *   **Request:** `POST /login` with `{"email": "admin@example.com", "password": "correct-horse-battery-staple"}` and `X-Request-ID: test-req-123`.
    *   **Expected Response:** `200 OK` with a `LoginResponse`. The `X-Request-ID` should be processed internally but not returned in the response.

### Error Cases

1.  **Test Case:** Missing `payload` (empty request body).
    *   **Request:** `POST /login` with an empty body `{}`.
    *   **Expected Response:** `400 Bad Request` with detail "Email and password are required.".
2.  **Test Case:** Missing `email` in payload.
    *   **Request:** `POST /login` with `{"password": "correct-horse-battery-staple"}`.
    *   **Expected Response:** `400 Bad Request` with detail "Email and password are required and must be valid.".
3.  **Test Case:** Missing `password` in payload.
    *   **Request:** `POST /login` with `{"email": "admin@example.com"}`.
    *   **Expected Response:** `400 Bad Request` with detail "Email and password are required and must be valid.".
4.  **Test Case:** Invalid email format.
    *   **Request:** `POST /login` with `{"email": "invalid-email", "password": "correct-horse-battery-staple"}`.
    *   **Expected Response:** `400 Bad Request` with detail "Email and password are required and must be valid.".
5.  **Test Case:** Incorrect password.
    *   **Request:** `POST /login` with `{"email": "admin@example.com", "password": "wrong-password"}`.
    *   **Expected Response:** `401 Unauthorized` with detail "Invalid email or password.".
6.  **Test Case:** Non-existent user email.
    *   **Request:** `POST /login` with `{"email": "nonexistent@example.com", "password": "any-password"}`.
    *   **Expected Response:** `401 Unauthorized` with detail "Invalid email or password.".
7.  **Test Case:** Password less than min_length (if enforced by Pydantic, though not explicitly shown in diff).
    *   **Request:** `POST /login` with `{"email": "admin@example.com", "password": "short"}`.
    *   **Expected Response:** `400 Bad Request` with detail "Email and password are required and must be valid.". (Assuming `min_length=8` from schema definition).

## 6. Edge Cases

*   **Email with leading/trailing spaces:** The `authenticate_user` function normalizes the email by stripping whitespace and converting to lowercase. This should be handled correctly.
*   **Case sensitivity of email:** The `authenticate_user` function normalizes the email to lowercase, making the lookup case-insensitive.
*   **`remember_me` field omitted:** The `remember_me` field defaults to `False` in the `LoginRequest` schema, so omitting it should result in the default shorter token expiration.
*   **`remember_me` field with non-boolean value:** Pydantic validation should catch this and return a `400 Bad Request`.

## 7. Regression Risks

*   **Authentication Logic:** Any subtle changes in how `authenticate_user` handles credentials or token generation could break existing login flows. The addition of `remember_me` seems straightforward, but thorough testing is advised.
*   **Response Structure:** Clients relying on the exact structure of the `LoginResponse` might be affected if the `expires_in` field is not handled correctly or if its presence causes issues.
*   **Validation Errors:** Changes in Pydantic validation for `LoginRequest` could lead to unexpected `400` responses for previously valid inputs.

## 8. Swagger/OpenAPI-Ready Notes

*   The `/login` endpoint is well-defined with clear request/response models and status codes.
*   The `LoginRequest` schema includes `email`, `password`, and `remember_me` with appropriate types and examples.
*   The `LoginResponse` schema includes `token`, `token_type`, and `expires_in` with types and examples.
*   The `ErrorResponse` schema is defined for error messages.
*   The `summary` and `description` fields are present for the endpoint and models, aiding OpenAPI generation.
*   The `Header` parameter `X-Request-ID` is documented.
*   The `example` fields in the request body and responses are useful for generating OpenAPI examples.
*   The `responses` dictionary in the route decorator provides OpenAPI-compatible descriptions for status codes.
*   The `tags` field is used to group the endpoint under "auth".
*   The `response_model` is correctly specified.
*   The `Body` parameter is used with `default=None` and an `example`, which is good for OpenAPI generation.
*   The `ValidationError` handling is explicit, which is good for API clarity.
