mod config;
mod db;
mod handlers;
mod middleware;
mod openapi;

use actix_web::{web, App, HttpServer};
use std::sync::Arc;
use utoipa::OpenApi;
use utoipa_swagger_ui::SwaggerUi;

use config::Config;
use handlers::{get_role_by_code, get_user, health, health_test, list_roles, list_users, login, ready};

#[derive(Clone)]
pub struct AppState {
    pub pool: sqlx::PgPool,
    pub config: Config,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let cfg = Config::load();
    let pool = db::init_pool(&cfg).await.expect("DB init failed");
    let state = Arc::new(AppState {
        pool: pool.clone(),
        config: cfg.clone(),
    });

    let port = state.config.app_port;
    println!("Rust API (Actix) listening on 0.0.0.0:{}", port);

    let workers = std::thread::available_parallelism()
        .map(|p| p.get())
        .unwrap_or(4);

    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::from(state.clone()))
            .wrap_fn(middleware::timing_wrap_fn)
            .service(
                SwaggerUi::new("/swagger-ui/{_:.*}")
                    .url("/api-docs/openapi.json", openapi::ApiDoc::openapi()),
            )
            .route("/health", web::get().to(health))
            .route("/health/test", web::get().to(health_test))
            .route("/ready", web::get().to(ready))
            .route("/auth/login", web::post().to(login))
            .route("/roles", web::get().to(list_roles))
            .route("/roles/code/{code}", web::get().to(get_role_by_code))
            .route("/users", web::get().to(list_users))
            .route("/users/{user_id}", web::get().to(get_user))
    })
    .workers(workers)
    .bind(("0.0.0.0", port))?
    .run()
    .await
}
