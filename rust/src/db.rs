use sqlx::postgres::PgPoolOptions;
use sqlx::PgPool;

use crate::config::Config;

pub async fn init_pool(cfg: &Config) -> Result<PgPool, sqlx::Error> {
    let max_conns = cfg.db_pool_size;
    let pool = PgPoolOptions::new()
        .max_connections(max_conns)
        .min_connections(max_conns / 2)
        .connect(&cfg.database_url())
        .await?;
    Ok(pool)
}
