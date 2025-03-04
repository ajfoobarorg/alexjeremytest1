# Alex Jeremy Test 1
Our first shared repo

# Arch notes
Backend is FastAPI (a python backend)

FE is Svelte, served for development via vite.

No CSS framework yet (consider Tailwind)


# How to run
```
cd frontend
bun run dev
```
and in another terminal:
```
cd backend && uvicorn main:app --reload
```

# Local setup
```
# Bun is a javascript package manager (similar to npm)
curl -fsSL https://bun.sh/install | bash
cd frontend && bun install
```

# Python setup
*Doesn't work on python 3.13, use 3.12*

```
# Maybe run this the first time to create it
python3.12 -m venv ~/python-environments/alexjeremy

# Run every time to enter the env (TODO: how to auto-do this when
you CC into the relevant repo dir)
. ~/python-environments/alexjeremy/bin/activate
```

To get out of the environment, run `deactivate`

Then configure Cursor:

1. Cmd-Shift-P (palette)
1. Python: Select Interpreter
1. Enter path to ~/python-environments/alexjeremy/bin/python

# Pydantic Setup
One of our `pip` packages needs `pydantic`, which needs Rust and its package manager Cargo:
```
curl https://sh.rustup.rs -sSf | sh
```

# Pip package install
```
pip install -r requirements.txt
```

# Cursor extensions
Svelte Extension - it should auto ask you if you want to install the svelte extension
Typescript Extension

# Serving extensions
Getting the backend up at running on render.com, see [ChatGPT's guidance](https://chatgpt.com/share/67c74b42-e3b8-8000-8577-ac6f27b02043).
