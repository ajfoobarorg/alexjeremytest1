# Alex Jeremy Test 1


# Arch notes
Backend is FastAPI (a python backend)

FE is Svelte, served for development via vite.

No CSS framework yet (consider Tailwind)


# How to run locally
```
cd frontend && bun run dev
```
and in another terminal:
```
cd backend && uvicorn main:app --reload
```

# Local setup
### Bun - the JS package manager (like NPM)
```
curl -fsSL https://bun.sh/install | bash
cd frontend && bun install
```

### Python setup
*Doesn't work on python 3.13, use 3.12*

```
# Run this the first time to create the venv
python3.12 -m venv ~/python-environments/alexjeremy

# Run every time to enter the env (TODO: how to auto-do this when
you CC into the relevant repo dir)
. ~/python-environments/alexjeremy/bin/activate

# Needs to run once to setup the venv with required packages
pip install -r backend/requirements.txt

```

One of our `pip` packages needs `pydantic`, which needs Rust and its package manager Cargo:
```
curl https://sh.rustup.rs -sSf | sh
```

To get out of the environment, run `deactivate`


# Cursor
Then configure Cursor:

1. Cmd-Shift-P (palette)
1. Python: Select Interpreter
1. Enter path to ~/python-environments/alexjeremy/bin/python


Install some extentions:

*  Svelte Extension - it should auto ask you if you want to install the svelte extension
*  Typescript Extension

# Hosting
Getting the backend up at running on render.com, see [ChatGPT's guidance](https://chatgpt.com/share/67c74b42-e3b8-8000-8577-ac6f27b02043).

