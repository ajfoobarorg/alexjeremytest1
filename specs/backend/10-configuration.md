# Configuration Specification

This specification defines the configuration requirements for the Ultimate Tic-Tac-Toe API.

## Overview

The configuration system should provide:

1. Environment-specific settings
2. Easy overrides for testing
3. Secure handling of sensitive values
4. Centralized access to configuration values

## Configuration Categories

### Server Configuration

- **Host**: String - Server host (default: "127.0.0.1")
- **Port**: Integer - Server port (default: 8000)
- **Workers**: Integer - Number of worker processes (default: 1)
- **Debug**: Boolean - Enable debug mode (default: false in production, true in development)
- **Log Level**: String - Logging level (default: "info")

### Database Configuration

- **DB_PATH**: String - Path to SQLite database file
- **DB_PRAGMAS**: Object - Database pragmas for SQLite optimization
  - **foreign_keys**: Boolean - Enable foreign key support (default: true)
  - **journal_mode**: String - Journal mode (default: "wal")

### Cookie Security

- **IS_PRODUCTION**: Boolean - Whether the environment is production
- **BACKEND_DOMAIN**: String - Domain for cookies
- **COOKIE_SECURE**: Boolean - Use secure cookies (default: true in production, false in development)
- **COOKIE_SAMESITE**: String - SameSite cookie policy (default: "none" in production, "lax" in development)
- **COOKIE_MAX_AGE**: Integer - Cookie max age in seconds (default: 31536000, 1 year)

### CORS Configuration

- **ALLOWED_ORIGINS**: Array - List of allowed CORS origins
- **ALLOW_CREDENTIALS**: Boolean - Allow credentials in CORS (default: true)
- **ALLOW_METHODS**: Array - List of allowed HTTP methods (default: ["*"])
- **ALLOW_HEADERS**: Array - List of allowed HTTP headers (default: ["*"])

### Game Configuration

- **DEFAULT_ELO**: Integer - Default ELO rating for new players (default: 1000)
- **TOTAL_TIME_ALLOWED**: Integer - Time limit in seconds (default: 360, 6 minutes)
- **MATCHMAKING_TTL**: Integer - TTL for matchmaking in seconds (default: 30)
- **ELO_K_FACTOR**: Integer - K-factor for ELO calculations (default: 32)

## Environment Variables

The application should support configuration via environment variables:

- **UTTT_HOST** - Server host
- **UTTT_PORT** - Server port
- **UTTT_WORKERS** - Number of worker processes
- **UTTT_DEBUG** - Enable debug mode
- **UTTT_LOG_LEVEL** - Logging level
- **UTTT_DB_PATH** - Path to SQLite database
- **UTTT_IS_PRODUCTION** - Whether in production mode
- **UTTT_BACKEND_DOMAIN** - Backend domain for cookies
- **UTTT_ALLOWED_ORIGINS** - Comma-separated list of allowed origins

## Configuration Loading Precedence

Configuration values should be loaded in the following order (each overrides the previous):

1. Default values hard-coded in the application
2. Configuration file (config.toml, config.json, etc.)
3. Environment variables
4. Command-line arguments

## Configuration File Format

The application should support a configuration file in a standard format like TOML, JSON, or YAML:

```toml
[server]
host = "127.0.0.1"
port = 8000
workers = 1
debug = false
log_level = "info"

[database]
db_path = "uttt.db"

[cookies]
is_production = false
backend_domain = "localhost"

[cors]
allowed_origins = ["http://localhost:3000", "http://localhost:5173"]

[game]
total_time_allowed = 360
matchmaking_ttl = 30
elo_k_factor = 32
```

## Testing Configuration

For testing, the application should:

1. Support a separate test configuration
2. Use an in-memory or temporary database
3. Override settings for deterministic test behavior

## Configuration API

The application should provide a simple API to access configuration values:

```rust
let config = Config::load();
let port = config.server.port;
let db_path = config.database.db_path;
```

## Security Considerations

1. Do not hardcode sensitive values in the application code
2. Do not log sensitive configuration values
3. Use appropriate file permissions for configuration files
4. Validate configuration values at startup

## Default Configuration

The application should include sensible defaults for all configuration values to simplify setup and deployment.

## Configuration Documentation

All configuration options should be documented with:

1. Name
2. Type
3. Default value
4. Description
5. Environment variable name
6. Example value

## Implementation Notes

1. Use a configuration library appropriate for the implementation language
2. Support hot reloading of configuration when feasible
3. Validate configuration at startup and fail fast if invalid
4. Log the active configuration at startup (excluding sensitive values)
5. Include configuration schema documentation in the project