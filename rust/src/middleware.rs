//! Timing middleware: adds X-Server-Time and X-Response-Time headers to every response.
//!
//! - **X-Server-Time**: UTC timestamp when response was sent (ISO 8601)
//! - **X-Response-Time**: request processing duration in milliseconds (e.g. "1.23ms")

use actix_web::{dev::{Service, ServiceRequest}, http::header, Error};
use chrono::Utc;
use std::time::Instant;

/// Adds X-Server-Time and X-Response-Time headers to a response.
/// Call this after receiving the response from the inner service.
#[inline]
pub fn add_timing_headers(
    res: &mut actix_web::dev::ServiceResponse<actix_web::body::BoxBody>,
    start: Instant,
) {
    let elapsed_ms = start.elapsed().as_secs_f64() * 1000.0;
    let server_time = Utc::now().format("%Y-%m-%dT%H:%M:%S%.3fZ").to_string();
    res.headers_mut().insert(
        header::HeaderName::from_static("x-server-time"),
        header::HeaderValue::from_str(&server_time).unwrap(),
    );
    res.headers_mut().insert(
        header::HeaderName::from_static("x-response-time"),
        header::HeaderValue::from_str(&format!("{:.2}ms", elapsed_ms)).unwrap(),
    );
}

/// Closure for `.wrap_fn()`: measures request duration and adds timing headers.
pub fn timing_wrap_fn(
    req: ServiceRequest,
    srv: &impl Service<
        ServiceRequest,
        Response = actix_web::dev::ServiceResponse<actix_web::body::BoxBody>,
        Error = Error,
    >,
) -> impl std::future::Future<Output = Result<actix_web::dev::ServiceResponse<actix_web::body::BoxBody>, Error>> {
    let start = Instant::now();
    let fut = srv.call(req);
    async move {
        let mut res: actix_web::dev::ServiceResponse<actix_web::body::BoxBody> = fut.await?;
        add_timing_headers(&mut res, start);
        Ok(res)
    }
}
