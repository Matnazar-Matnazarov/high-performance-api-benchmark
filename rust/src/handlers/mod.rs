//! HTTP request handlers for health, auth, roles, and users.

pub mod auth;
pub mod health;
pub mod roles;
pub mod users;

pub use auth::login;
pub use health::{health, health_test, ready};
pub use roles::{get_role_by_code, list_roles};
pub use users::{get_user, list_users};
