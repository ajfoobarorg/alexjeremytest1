use axum::{routing::get, Router};
use std::sync::Arc;
use tower_http::trace::TraceLayer;

pub struct AppState {
    // For future use when we add database connections, configuration, etc.
}

pub fn create_router(state: Arc<AppState>) -> Router {
    Router::new()
        .route("/", get(health_check))
        .layer(TraceLayer::new_for_http())
        .with_state(state)
}

async fn health_check() -> &'static str {
    "Hello, World!"
}
