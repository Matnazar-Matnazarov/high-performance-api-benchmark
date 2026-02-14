use actix_web::{web, HttpResponse, Responder};
use serde::{Deserialize, Serialize};

use crate::AppState;

#[derive(Deserialize)]
pub struct LoginRequest {
    username: String,
    password: String,
}

#[derive(Serialize)]
struct LoginResponse {
    access_token: String,
    expires_in: i64,
    token_type: &'static str,
}

pub async fn login(state: web::Data<AppState>, body: web::Json<LoginRequest>) -> impl Responder {
    let pool = &state.pool;
    let cfg = &state.config;
    if body.username.is_empty() || body.password.is_empty() {
        return HttpResponse::BadRequest()
            .json(serde_json::json!({"detail": "username and password required"}));
    }
    let row: Option<(i64, String, Option<String>, bool)> = sqlx::query_as(
        "SELECT id, password, role, is_staff FROM accounts_user WHERE username = $1",
    )
    .bind(&body.username)
    .fetch_optional(pool)
    .await
    .ok()
    .flatten();
    let Some((id, stored_hash, role, is_staff)) = row else {
        return HttpResponse::Unauthorized()
            .json(serde_json::json!({"detail": "Invalid credentials"}));
    };
    let role = role.unwrap_or_else(|| "CUSTOMER".to_string());
    match djangohashers::check_password(&body.password, &stored_hash) {
        Ok(true) => {}
        _ => {
            return HttpResponse::Unauthorized()
                .json(serde_json::json!({"detail": "Invalid credentials"}));
        }
    }
    let exp = chrono::Utc::now() + chrono::Duration::seconds(cfg.jwt_expires);
    let claims = serde_json::json!({
        "user_id": id,
        "username": body.username,
        "role": role,
        "is_staff": is_staff,
        "exp": exp.timestamp(),
        "iat": chrono::Utc::now().timestamp(),
    });
    let token = match jsonwebtoken::encode(
        &jsonwebtoken::Header::default(),
        &claims,
        &jsonwebtoken::EncodingKey::from_secret(cfg.jwt_secret.as_bytes()),
    ) {
        Ok(t) => t,
        Err(_) => {
            return HttpResponse::InternalServerError()
                .json(serde_json::json!({"detail": "Token creation failed"}));
        }
    };
    HttpResponse::Ok().json(LoginResponse {
        access_token: token,
        expires_in: cfg.jwt_expires,
        token_type: "bearer",
    })
}
