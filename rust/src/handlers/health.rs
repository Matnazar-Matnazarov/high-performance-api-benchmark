use actix_web::{web, HttpResponse, Responder};
use serde::Serialize;
use std::collections::HashMap;

use crate::AppState;

#[derive(Serialize)]
struct HealthResponse {
    status: &'static str,
}

#[derive(Serialize)]
struct HealthTestResponse {
    status: &'static str,
    message: &'static str,
}

#[derive(Serialize)]
struct ReadyResponse {
    status: &'static str,
    checks: HashMap<&'static str, &'static str>,
}

pub async fn health() -> impl Responder {
    HttpResponse::Ok().json(HealthResponse { status: "ok" })
}

pub async fn health_test() -> impl Responder {
    HttpResponse::Ok().json(HealthTestResponse {
        status: "ok",
        message: "Test health check endpoint",
    })
}

pub async fn ready(state: web::Data<AppState>) -> impl Responder {
    match sqlx::query("SELECT 1").fetch_one(&state.pool).await {
        Ok(_) => HttpResponse::Ok().json(ReadyResponse {
            status: "healthy",
            checks: [("database", "ok")].into_iter().collect(),
        }),
        Err(_) => HttpResponse::ServiceUnavailable().json(ReadyResponse {
            status: "unhealthy",
            checks: [("database", "error")].into_iter().collect(),
        }),
    }
}
