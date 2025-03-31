use std::sync::Arc;
use tokio::net::TcpListener;
use tokio::sync::oneshot;

#[tokio::test]
async fn test_health_endpoint() {
    // Start the server in a background task
    let (shutdown_tx, shutdown_rx) = oneshot::channel::<()>();
    let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
    let addr = listener.local_addr().unwrap();

    // Use rustbackend library
    use rustbackend::{create_router, AppState};
    let app_state = Arc::new(AppState {});
    let app = create_router(app_state);

    // Spawn the server task with graceful shutdown
    let server_handle = tokio::spawn(async move {
        axum::serve(listener, app)
            .with_graceful_shutdown(async {
                let _ = shutdown_rx.await;
            })
            .await
            .expect("Server error");
    });

    // Create the HTTP client
    let client = reqwest::Client::new();

    // Test the health endpoint
    let response = client
        .get(format!("http://{}", addr))
        .send()
        .await
        .expect("Failed to send request");

    assert_eq!(response.status(), 200);
    assert_eq!(response.text().await.unwrap(), "Hello, World!");

    // Shutdown the server
    let _ = shutdown_tx.send(());
    let _ = server_handle.await;
}
