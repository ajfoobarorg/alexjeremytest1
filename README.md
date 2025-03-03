# Alex Jeremy Test 1
Our first shared repo


# How to run
```
cd frontend
bun run dev
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
python3.12 -m venv ~/python-environments/alexjeremy
~/python-environments/alexjeremy/bin/activate
```
To get out of the environment, run `deactivate`

Then configure Cursor:
1. Cmd-Shift-P (palette)
2. Python: Select Interpreter
3. Enter path to ~/python-environments/alexjeremy/bin/python

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