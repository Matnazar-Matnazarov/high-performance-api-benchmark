use std::env;

#[derive(Clone)]
pub struct Config {
    pub db_name: String,
    pub db_user: String,
    pub db_password: String,
    pub db_host: String,
    pub db_port: u16,
    pub app_port: u16,
    pub db_pool_size: u32,
    pub jwt_secret: String,
    pub jwt_expires: i64,
}

impl Config {
    pub fn load() -> Self {
        // Load .env from project root (parent of rust/)
        let manifest_dir = std::path::Path::new(env!("CARGO_MANIFEST_DIR"));
        let project_root = manifest_dir.parent().unwrap_or(manifest_dir);
        let env_path = project_root.join(".env");
        dotenvy::from_path(&env_path).ok();
        let get_env = |key: &str, default: &str| {
            env::var(key).unwrap_or_else(|_| default.to_string())
        };
        let get_env_int = |key: &str, default: u16| {
            env::var(key)
                .ok()
                .and_then(|v| v.parse().ok())
                .unwrap_or(default)
        };
        let get_env_u32 = |key: &str, default: u32| {
            env::var(key)
                .ok()
                .and_then(|v| v.parse().ok())
                .unwrap_or(default)
        };
        Self {
            db_name: get_env("DB_NAME", "bolt_test"),
            db_user: get_env("DB_USER", "postgres"),
            db_password: get_env("DB_PASSWORD", ""),
            db_host: get_env("DB_HOST", "localhost"),
            db_port: get_env_int("DB_PORT", 5432),
            app_port: get_env_int("RUST_PORT", 8006),
            db_pool_size: get_env_u32("DB_POOL_SIZE", 32),
            jwt_secret: get_env("BOLT_JWT_SECRET", &get_env("SECRET_KEY", "change-me-in-production")),
            jwt_expires: env::var("BOLT_JWT_EXPIRES_SECONDS")
                .ok()
                .and_then(|v| v.parse().ok())
                .unwrap_or(3600),
        }
    }

    pub fn database_url(&self) -> String {
        format!(
            "postgres://{}:{}@{}:{}/{}",
            self.db_user, self.db_password, self.db_host, self.db_port, self.db_name
        )
    }
}
