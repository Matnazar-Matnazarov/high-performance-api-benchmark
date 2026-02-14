//! OpenAPI/Swagger documentation for the Rust API.

#![allow(dead_code)]

use utoipa::OpenApi;

#[derive(OpenApi)]
#[openapi(
    info(
        title = "Rust API (Bolt-compatible)",
        description = "Same endpoints as Django Bolt. X-Server-Time, X-Response-Time on every response.",
        version = "0.1.0"
    ),
    paths(
        health,
        health_test,
        ready,
        login,
        list_roles,
        get_role_by_code,
        list_users,
        get_user,
    ),
    components(schemas(
        HealthResponse,
        HealthTestResponse,
        ReadyResponse,
        LoginRequest,
        LoginResponse,
        RoleSchema,
        UserSchema,
        UserListResponse,
        ErrorDetail,
    ))
)]
pub struct ApiDoc;

// --- Health schemas ---

#[derive(utoipa::ToSchema)]
struct HealthResponse {
    status: String,
}

#[derive(utoipa::ToSchema)]
struct HealthTestResponse {
    status: String,
    message: String,
}

#[derive(utoipa::ToSchema)]
struct ReadyResponse {
    status: String,
    checks: std::collections::HashMap<String, String>,
}

// --- Auth schemas ---

#[derive(utoipa::ToSchema)]
struct LoginRequest {
    username: String,
    password: String,
}

#[derive(utoipa::ToSchema)]
struct LoginResponse {
    access_token: String,
    expires_in: i64,
    token_type: String,
}

// --- Role schemas ---

#[derive(utoipa::ToSchema)]
struct RoleSchema {
    code: String,
    name: String,
}

// --- User schemas ---

#[derive(utoipa::ToSchema)]
struct UserSchema {
    id: i32,
    username: String,
    role: String,
}

#[derive(utoipa::ToSchema)]
struct UserListResponse {
    results: Vec<UserSchema>,
    count: i64,
    next: Option<String>,
    previous: Option<String>,
}

#[derive(utoipa::ToSchema)]
struct ErrorDetail {
    detail: String,
}

// --- Path definitions (doc-only) ---

/// Liveness check
#[utoipa::path(
    get,
    path = "/health",
    responses((status = 200, body = HealthResponse))
)]
fn health() {}

/// Custom health check
#[utoipa::path(
    get,
    path = "/health/test",
    responses((status = 200, body = HealthTestResponse))
)]
fn health_test() {}

/// Readiness check (DB)
#[utoipa::path(
    get,
    path = "/ready",
    responses(
        (status = 200, body = ReadyResponse, description = "Healthy"),
        (status = 503, body = ReadyResponse, description = "Unhealthy")
    )
)]
fn ready() {}

/// JWT login
#[utoipa::path(
    post,
    path = "/auth/login",
    request_body = LoginRequest,
    responses(
        (status = 200, body = LoginResponse),
        (status = 400, body = ErrorDetail),
        (status = 401, body = ErrorDetail)
    )
)]
fn login() {}

/// List all roles
#[utoipa::path(
    get,
    path = "/roles",
    responses((status = 200, body = Vec<RoleSchema>))
)]
fn list_roles() {}

/// Get role by code
#[utoipa::path(
    get,
    path = "/roles/code/{code}",
    params(("code" = String, Path, description = "Role code: ADMIN, SHOPKEEPER, CUSTOMER")),
    responses(
        (status = 200, body = RoleSchema),
        (status = 404, body = ErrorDetail)
    )
)]
fn get_role_by_code() {}

/// List users (paginated)
#[utoipa::path(
    get,
    path = "/users",
    params(
        ("search" = Option<String>, Query),
        ("role" = Option<String>, Query),
        ("role_code" = Option<String>, Query),
        ("page" = Option<i32>, Query),
        ("page_size" = Option<i32>, Query)
    ),
    responses((status = 200, body = UserListResponse))
)]
fn list_users() {}

/// Get user by ID
#[utoipa::path(
    get,
    path = "/users/{user_id}",
    params(("user_id" = i32, Path)),
    responses(
        (status = 200, body = UserSchema),
        (status = 404, body = ErrorDetail)
    )
)]
fn get_user() {}
