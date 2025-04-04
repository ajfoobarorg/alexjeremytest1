# CLAUDE.md - Development Guide

## Backend (Python)
- Run server: `cd backend && uvicorn main:app --reload`
- Run all tests: `cd backend && pytest`
- Run single test: `cd backend && pytest tests/test_game_logic.py::TestGameLogic::test_move_to_completed_board -v`
- Lint code: `cd backend && ruff check .`
- Format code: `cd backend && black .`

## Backend (Rust)
- Run server: `cd rustbackend && cargo run`
- Run tests: `cd rustbackend && cargo test`
- Lint code: `cd rustbackend && cargo clippy`
- Format code: `cd rustbackend && cargo fmt`

## Frontend (Svelte)
- Run dev server: `cd frontend && bun run dev`
- Build for production: `cd frontend && bun run build`

## Style Guidelines
- Python: Google-style docstrings, Black formatting (88 chars), imports ordered (standard → third-party → FastAPI → local)
- Rust: Standard Rust formatting (rustfmt), follow Rust API guidelines, proper error handling with Result/Option
- JS/Svelte: Prettier formatting, 2-space indent, 100 char line limit, single quotes
- Svelte components: script → style → template structure
- Error handling: Clear error messages, proper validation
- Types: Strong typing everywhere (Pydantic for Python, proper types for Rust, TypeScript for frontend)

## Git Workflow
- Feature branches from main
- Descriptive commit messages
- PR for all changes

## Cursor Rules
This project uses Cursor rules defined in .cursor/rules/. When using Claude Code CLI, please read and apply all rules from this directory.