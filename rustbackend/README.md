# Rust Backend

A simple Rust implementation of the backend service using Axum.

## Prerequisites

- Rust (stable channel)
- Cargo

## Project Structure

- `src/main.rs` - Entry point with server configuration
- `src/lib.rs` - Shared code for the application and tests
- `tests/integration.rs` - Integration tests for the API

## Development

Build the project:

```bash
cargo build
```

Run the project (server will listen on http://localhost:8000):

```bash
cargo run
```

Run tests:

```bash
cargo test
```

Run linter:

```bash
cargo clippy
```

Format code:

```bash
cargo fmt
```

## API Endpoints

- `GET /` - Health check endpoint that returns "Hello, World!"

## CI/CD

This project is configured to run tests on GitHub Actions. The workflow will:

1. Build the Rust application
2. Run the tests
3. Check code style with Clippy
4. Verify formatting with rustfmt

See the `.github/workflows/rust.yml` file for the complete configuration.