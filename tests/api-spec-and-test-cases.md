## MergeFlow API Analysis: PR #47 - Test MergeFlow Step 7 release summary email

### 1. Change Summary

This PR introduces a new `remember_me` option to the user login API. When set to `true`, this option instructs the backend to generate a longer-lived authentication token, suitable for trusted devices. The change involves modifying the `LoginRequest` schema to include the `remember_me` field, updating the `/login` endpoint to pass this new parameter to the authentication service, and modifying the authentication service to generate different token types based on the `remember_me` flag.

### 2. Endpoint(s) Detected

*   **POST /login**

### 3. Directly Related Files Considered

*   `backend/routes/auth.py`
*   `backend/schemas/auth.py`
*   `backend/services/auth_service.py`

### 4. API Specification Snapshot

#### POST /login

*   **method**: `POST`
*   **path**: `/login`
*   **endpoint name / operation name**: `login`
*   **tags / feature area**: `auth`
*   **summary**: Log in with email and password
*   **description**: Validate credentials and return a bearer token for authenticated users.
*   **auth requirement**: None (this endpoint is for authentication)
*   **parameters**:
    *   **Path Parameters**: Not detected from provided context.
    *   **Query Parameters**: Not detected from provided context.
*   **request body**:
    *   **description**: User credentials for login.
    *   **content type**: `application/json`
    *   **schema**: `LoginRequest`
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
                },
                "remember_me": {
                    "type": "boolean",
                    "default": false,
                    "description": "When true, issue a longer-lived session token for trusted devices.",
                    "example": false
                }
            },
            "required": [
                "email",
                "password"
            ]
        }
        ```
    *   **example request body**:
        ```json
        {
            "email": "admin@example.com",
            "password": "correct-horse-battery-staple",
            "remember_me": true
        }
        ```
*   **headers**:
    *   `Content-Type: application/json` (for request body)
*   **auth**: Not applicable (this endpoint provides authentication tokens).
*   **env vars**:
    *   `AUTH_TOKEN_ISSUER`: Used in `backend/services/auth_service.py` to prefix the generated token. Defaults to "mergeflow-test" if not set.
*   **responses**:
    *   **200 OK**:
        *   **description**: Successful authentication, returns a bearer token.
        *   **schema**: `LoginResponse`
            ```json
            {
                "type": "object",
                "properties": {
                    "token": {
                        "type": "string",
                        "description": "Bearer token returned after successful authentication.",
                        "example": "mergeflow-test-long-lived-token-for-admin-user"
                    },
                    "token_type": {
                        "type": "string",
                        "default": "bearer",
                        "description": "Token type clients should use in the Authorization header.",
                        "example": "bearer"
                    }
                },
                "required": [
                    "token"
                ]
            }
            ```
        *   **example successful response**:
            ```json
            {
                "token": "mergeflow-test-long-lived-token-for-admin-user",
                "token_type": "bearer"
            }
            ```
            (if `remember_me` was true)
            ```json
            {
                "token": "mergeflow-test-session-token-for-admin-user",
                "token_type": "bearer"
            }
            ```
            (if `remember_me` was false or omitted)
    *   **400 Bad Request**:
        *   **description**: The request body is missing required fields or contains invalid values.
        *   **schema**: `ErrorResponse`
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
                "required": [
                    "detail"
                ]
            }
            ```
        *   **example error responses**:
            ```json
            {
                "detail": "Email and password are required."
            }
            ```
            (if payload is empty)
            ```json
            {
                "detail": "Email and password are required and must be valid."
            }
            ```
            (if email is invalid or password too short)
    *   **401 Unauthorized**:
        *   **description**: The supplied email and password do not match a known user.
        *   **schema**: `ErrorResponse`
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
                "required": [
                    "detail"
                ]
            }
            ```
        *   **example error response**:
            ```json
            {
                "detail": "Invalid email or password."
            }
            ```

### 5. Test Cases

1.  **Happy Path - `remember_me` true**:
    *   **Request**: `POST /login` with `{"email": "admin@example.com", "password": "correct-horse-battery-staple", "remember_me": true}`
    *   **Expected Response**: `200 OK` with `token` containing "long-lived" suffix (e.g., `mergeflow-test-long-lived-token-for-admin-user`).
2.  **Happy Path - `remember_me` false**:
    *   **Request**: `POST /login` with `{"email": "admin@example.com", "password": "correct-horse-battery-staple", "remember_me": false}`
    *   **Expected Response**: `200 OK` with `token` containing "session" suffix (e.g., `mergeflow-test-session-token-for-admin-user`).
3.  **Happy Path - `remember_me` omitted (defaults to false)**:
    *   **Request**: `POST /login` with `{"email": "admin@example.com", "password": "correct-horse-battery-staple"}`
    *   **Expected Response**: `200 OK` with `token` containing "session" suffix.
4.  **Invalid Credentials**:
    *   **Request**: `POST /login` with `{"email": "admin@example.com", "password": "wrong-password", "remember_me": false}`
    *   **Expected Response**: `401 Unauthorized` with `{"detail": "Invalid email or password."}`.
5.  **Non-existent User**:
    *   **Request**: `POST /login` with `{"email": "nonexistent@example.com", "password": "any-password", "remember_me": false}`
    *   **Expected Response**: `401 Unauthorized` with `{"detail": "Invalid email or password."}`.
6.  **Missing Email**:
    *   **Request**: `POST /login` with `{"password": "correct-horse-battery-staple", "remember_me": false}`
    *   **Expected Response**: `400 Bad Request` with `{"detail": "Email and password are required and must be valid."}`.
7.  **Missing Password**:
    *   **Request**: `POST /login` with `{"email": "admin@example.com", "remember_me": false}`
    *   **Expected Response**: `400 Bad Request` with `{"detail": "Email and password are required and must be valid."}`.
8.  **Invalid Email Format**:
    *   **Request**: `POST /login` with `{"email": "invalid-email", "password": "correct-horse-battery-staple", "remember_me": false}`
    *   **Expected Response**: `400 Bad Request` with `{"detail": "Email and password are required and must be valid."}`.
9.  **Password Too Short**:
    *   **Request**: `POST /login` with `{"email": "admin@example.com", "password": "short", "remember_me": false}`
    *   **Expected Response**: `400 Bad Request` with `{"detail": "Email and password are required and must be valid."}`.
10. **Empty Request Body**:
    *   **Request**: `POST /login` with an empty body `{}` or `null`.
    *   **Expected Response**: `400 Bad Request` with `{"detail": "Email and password are required."}` or `{"detail": "Email and password are required and must be valid."}` depending on exact FastAPI validation flow.

### 6. Edge Cases

*   **Empty Payload**: Sending an empty JSON body `{}` or `null` to `/login` should correctly trigger a `400 Bad Request` due to missing required fields.
*   **`remember_me` Type Coercion**: Ensure that if `remember_me` is sent as a string (e.g., `"true"`, `"false"`), Pydantic handles it gracefully or rejects it with a validation error, as it's defined as a boolean. Pydantic typically handles string-to-bool coercion for "true"/"false".
*   **`AUTH_TOKEN_ISSUER` Environment Variable**: The token generation relies on `os.getenv("AUTH_TOKEN_ISSUER", "mergeflow-test")`. Testing with and without this environment variable set can confirm the default value is correctly applied.
*   **Case Sensitivity of Email**: The `authenticate_user` function normalizes the email (`email.strip().lower()`). This should be tested to ensure `Admin@Example.com` works the same as `admin@example.com`.

### 7. Regression Risks

*   **Existing Login Functionality**: The core login logic (email/password validation) was modified to accept an additional parameter. While the default `remember_me=False` should maintain existing behavior, there's a risk that the change in the `authenticate_user` signature or its call site could inadvertently break existing login flows for clients not sending `remember_me`.
*   **Token Format**: The token format now includes a `session_suffix`. While this is intended, ensure no downstream systems rely on the *exact* previous token string format (e.g., `issuer-token-for-user_id`).
*   **Pydantic Validation**: Changes to `LoginRequest` schema could affect how existing clients' payloads are validated, especially if they send unexpected types for `remember_me`.

### 8. Swagger/OpenAPI-Ready Notes

*   The `LoginRequest`, `LoginResponse`, and `ErrorResponse` schemas are well-defined and can be directly translated into OpenAPI components.
*   The `POST /login` endpoint definition includes summary, description, request body schema, and response schemas with examples, making it straightforward for OpenAPI generation.
*   The `remember_me` field in `LoginRequest` has a clear `default: false` and `description` which will translate well.
*   The `token` examples in `LoginResponse` should reflect the dynamic nature based on `remember_me` (e.g., `mergeflow-test-session-token-for-admin-user` vs. `mergeflow-test-long-lived-token-for-admin-user`). Consider adding multiple examples for the 200 response to illustrate both cases.
