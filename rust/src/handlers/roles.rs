use actix_web::{web, HttpResponse, Responder};
use serde::{Deserialize, Serialize};

#[derive(Serialize)]
struct RoleSchema {
    code: &'static str,
    name: &'static str,
}

const ROLES: &[(&'static str, &'static str)] = &[
    ("ADMIN", "Administrator"),
    ("SHOPKEEPER", "Shopkeeper"),
    ("CUSTOMER", "Customer"),
];

#[derive(Deserialize)]
pub(crate) struct CodeParam {
    code: String,
}

pub async fn list_roles() -> impl Responder {
    HttpResponse::Ok().json(
        ROLES
            .iter()
            .map(|(code, name)| RoleSchema {
                code: *code,
                name: *name,
            })
            .collect::<Vec<_>>(),
    )
}

pub async fn get_role_by_code(path: web::Path<CodeParam>) -> impl Responder {
    let code = path.code.trim().to_uppercase();
    for (c, n) in ROLES {
        if *c == code {
            return HttpResponse::Ok().json(RoleSchema { code: c, name: n });
        }
    }
    HttpResponse::NotFound().json(serde_json::json!({"detail": "Role not found"}))
}
