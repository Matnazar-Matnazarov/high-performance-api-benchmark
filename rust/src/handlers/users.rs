use actix_web::{web, HttpResponse, Responder};
use serde::{Deserialize, Serialize};

use crate::AppState;

#[derive(Serialize)]
struct UserSchema {
    id: i64,
    username: String,
    role: String,
}

#[derive(Serialize)]
struct UserListResponse {
    results: Vec<UserSchema>,
    count: i64,
    next: Option<String>,
    previous: Option<String>,
}

#[derive(Deserialize, Default)]
pub struct ListUsersQuery {
    search: Option<String>,
    role: Option<String>,
    role_code: Option<String>,
    page: Option<i32>,
    page_size: Option<i32>,
}

const VALID_ROLES: &[&str] = &["ADMIN", "SHOPKEEPER", "CUSTOMER"];

pub async fn list_users(
    state: web::Data<AppState>,
    query: web::Query<ListUsersQuery>,
) -> impl Responder {
    let pool = &state.pool;
    let q = query.into_inner();
    let search = q.search.as_deref().unwrap_or("").trim();
    let role_filter = q
        .role
        .or(q.role_code)
        .as_deref()
        .unwrap_or("")
        .trim()
        .to_uppercase();
    let role_filter = if role_filter.is_empty() || !VALID_ROLES.contains(&role_filter.as_str()) {
        String::new()
    } else {
        role_filter
    };
    let page = q.page.unwrap_or(1).max(1);
    let page_size = q.page_size.unwrap_or(10).clamp(1, 100);
    let offset = (page - 1) * page_size;

    let search_param = format!("%{}%", search);
    let total: i64 = match (search.is_empty(), role_filter.is_empty()) {
        (true, true) => sqlx::query_scalar("SELECT COUNT(*)::bigint FROM accounts_user")
            .fetch_one(pool)
            .await,
        (false, true) => sqlx::query_scalar(
            "SELECT COUNT(*)::bigint FROM accounts_user WHERE username ILIKE $1",
        )
        .bind(&search_param)
        .fetch_one(pool)
        .await,
        (true, false) => sqlx::query_scalar(
            "SELECT COUNT(*)::bigint FROM accounts_user WHERE role = $1",
        )
        .bind(&role_filter)
        .fetch_one(pool)
        .await,
        (false, false) => sqlx::query_scalar(
            "SELECT COUNT(*)::bigint FROM accounts_user WHERE username ILIKE $1 AND role = $2",
        )
        .bind(&search_param)
        .bind(&role_filter)
        .fetch_one(pool)
        .await,
    }
    .unwrap_or(0);

    let rows: Vec<(i64, String, String)> = match (search.is_empty(), role_filter.is_empty()) {
        (true, true) => sqlx::query_as(
            "SELECT id, username, COALESCE(role, 'CUSTOMER') FROM accounts_user ORDER BY id LIMIT $1 OFFSET $2",
        )
        .bind(page_size)
        .bind(offset)
        .fetch_all(pool)
        .await,
        (false, true) => sqlx::query_as(
            "SELECT id, username, COALESCE(role, 'CUSTOMER') FROM accounts_user WHERE username ILIKE $1 ORDER BY id LIMIT $2 OFFSET $3",
        )
        .bind(&search_param)
        .bind(page_size)
        .bind(offset)
        .fetch_all(pool)
        .await,
        (true, false) => sqlx::query_as(
            "SELECT id, username, COALESCE(role, 'CUSTOMER') FROM accounts_user WHERE role = $1 ORDER BY id LIMIT $2 OFFSET $3",
        )
        .bind(&role_filter)
        .bind(page_size)
        .bind(offset)
        .fetch_all(pool)
        .await,
        (false, false) => sqlx::query_as(
            "SELECT id, username, COALESCE(role, 'CUSTOMER') FROM accounts_user WHERE username ILIKE $1 AND role = $2 ORDER BY id LIMIT $3 OFFSET $4",
        )
        .bind(&search_param)
        .bind(&role_filter)
        .bind(page_size)
        .bind(offset)
        .fetch_all(pool)
        .await,
    }
    .unwrap_or_else(|e| {
        eprintln!("[users] SELECT error: {:?}", e);
        Vec::new()
    });

    let results: Vec<UserSchema> = rows
        .into_iter()
        .map(|(id, username, role)| UserSchema { id, username, role })
        .collect();

    let next = if (offset + results.len() as i32) < total as i32 {
        Some(format!("?page={}&page_size={}", page + 1, page_size))
    } else {
        None
    };
    let previous = if page > 1 {
        Some(format!("?page={}&page_size={}", page - 1, page_size))
    } else {
        None
    };

    HttpResponse::Ok().json(UserListResponse {
        results,
        count: total,
        next,
        previous,
    })
}

pub async fn get_user(state: web::Data<AppState>, path: web::Path<i32>) -> impl Responder {
    let user_id = path.into_inner();
    let pool = &state.pool;
    let row: Option<(i64, String, String)> = sqlx::query_as(
        "SELECT id, username, COALESCE(role, 'CUSTOMER') FROM accounts_user WHERE id = $1",
    )
    .bind(user_id)
    .fetch_optional(pool)
    .await
    .ok()
    .flatten();
    match row {
        Some((id, username, role)) => HttpResponse::Ok().json(UserSchema { id, username, role }),
        None => HttpResponse::NotFound().json(serde_json::json!({"detail": "User not found"})),
    }
}
