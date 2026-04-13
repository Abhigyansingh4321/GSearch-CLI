
A small terminal search tool I built while learning how Python CLI projects are structured.

`G-Search CLI` lets me search the web from the terminal, open useful results quickly, and experiment with things like command-line UX, packaging, environment variables, fallbacks, and optional API integrations.

It was started as a learning project, but I wanted it to be genuinely usable, not just a demo that looks good but gets lost in the folders and I never run it again.

<img width="1115" height="647" alt="Screenshot 2026-04-13 084402" src="https://github.com/user-attachments/assets/8f8a3876-773d-4558-ac4d-127153fe407f" />
# G-Search CLI

## Why I Built It

While studying and practicing, I end up searching for documentation, errors, and quick references constantly. Opening a browser every few minutes breaks flow, so I wanted a simple tool that could stay inside the terminal and still feel pleasant to use.

This project also gave me a good excuse to understand a few practical things properly:

- how a CLI tool is structured
- how Python packages are installed
- how environment variables are used
- how to design a fallback path when one provider fails
- how to make a small tool usable across different operating systems

## Build Note

I usually use AI tools in a supporting role while polishing parts of this project, especially for code cleanup and documentation. I still treat the codebase as mine to understand, maintain, and explain, and I only keep changes that make sense to me.

## Features

- Search the web directly from the terminal
- Use DuckDuckGo by default
- Optionally use Google Custom Search with API credentials(good luck finding it, cause i wasn't able to find it anywhere for free)
- Open the top result instantly with `--lucky`
- Restrict results to a specific domain with `--site`
- Print JSON output with `--json-output`
- Skip the interactive prompt with `--no-prompt`
- Run on Windows, Linux, and macOS

## Before You Start

You need to have:

- Python 3.10 or newer
- an internet connection
- a terminal

Google credentials are optional. If you do not configure them, the tool still works with DuckDuckGo.

Check whether Python is installed:

```bash
python --version
```

If that does not work, try:

```bash
python3 --version
```

If neither works, install Python first from the official website:

- Windows / macOS: https://www.python.org/downloads/
- Linux: install Python using your distribution package manager

## Getting Into the Project Folder

If you downloaded the project as a ZIP file, extract it first.

Then open a terminal and go into the folder that contains:

- `README.md`
- `setup.py`
- `requirements.txt`
- `src/`

Example:

```bash
cd path/to/Google-cli
```

## Installation

Choose the setup steps for your operating system.

### Windows PowerShell

```powershell
python -m venv venv_win
.\venv_win\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

First run:

```powershell
gsearch "python list comprehension"
```

### Windows Command Prompt (CMD)

```bat
python -m venv venv_win
venv_win\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

First run:

```bat
gsearch "python list comprehension"
```

### Linux

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

First run:

```bash
gsearch "python list comprehension"
```

### macOS

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

First run:

```bash
gsearch "python list comprehension"
```

## If `gsearch` Is Not Recognized

Usually this means the virtual environment is not active, or the command is not available in your current shell session yet.

You can still run the tool directly through Python.

### Windows PowerShell

```powershell
.\venv_win\Scripts\python -m src.main "python list comprehension"
```

### Windows CMD

```bat
venv_win\Scripts\python -m src.main "python list comprehension"
```

### Linux / macOS

```bash
./venv/bin/python -m src.main "python list comprehension"
```

## Common Commands

Basic search:

```bash
gsearch "binary search explanation"
```

Get 5 results:

```bash
gsearch "python decorators" --num 5
```

Use DuckDuckGo explicitly:

```bash
gsearch "rich table example" --engine duckduckgo
```

Use Google explicitly:

```bash
gsearch "python packaging tutorial" --engine google
```

Restrict results to one site:

```bash
gsearch "click prompts" --site docs.python.org
```

Open the top result directly:

```bash
gsearch "pytest fixtures" --lucky
```

Print JSON output:

```bash
gsearch "openai responses api" --json-output
```

Show help:

```bash
gsearch --help
```

## Optional Google Search Setup

By default, the tool uses DuckDuckGo.

If you want Google Custom Search support, you need:

1. a Google API key
2. a Programmable Search Engine
3. its Search Engine ID

Then create a `.env` file in the project root by copying the template.

### Windows PowerShell

```powershell
Copy-Item .env.template .env
```

### Windows CMD

```bat
copy .env.template .env
```

### Linux / macOS

```bash
cp .env.template .env
```

Then fill in:

```text
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_google_custom_search_engine_id_here
```

After that, these commands work:

```bash
gsearch "python requests docs" --engine google
gsearch "python requests docs" --engine auto
```

`--engine auto` tries Google first when credentials are available and falls back to DuckDuckGo if Google fails.

## Troubleshooting

### `python` is not recognized

Try:

```bash
python3 --version
```

If that works, use `python3` in the commands instead of `python`.

### `pip` is not recognized

Use:

```bash
python -m pip install -r requirements.txt
```

Or on Linux/macOS:

```bash
python3 -m pip install -r requirements.txt
```

### PowerShell says scripts are disabled

Run this once in PowerShell:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate the environment again:

```powershell
.\venv_win\Scripts\Activate.ps1
```

### Google engine gives a credentials error

That usually means `.env` is missing, incomplete, or not loaded correctly.

Make sure both of these are present:

- `GOOGLE_API_KEY`
- `GOOGLE_CSE_ID`

### Search fails with a network error

Check:

- your internet connection
- firewall or proxy restrictions
- whether the provider is temporarily unavailable

You can also try a different engine:

```bash
gsearch "python generators" --engine duckduckgo
```

## Project Map

Once the folder structure starts making sense, the code becomes much easier to approach.

```text
Google-cli/
├── src/
│   ├── main.py        # CLI entry point and command options
│   ├── engine.py      # Search logic, provider selection, fallbacks
│   └── ui.py          # Rich terminal output
├── tests/
│   ├── test_engine.py # Search engine tests
│   └── test_main.py   # CLI tests
├── .env.template      # Template for optional Google API credentials
├── requirements.txt   # Python dependencies
├── setup.py           # Packaging and console command setup
└── README.md          # Documentation
```

## What I Learned From This Project

Even though the project is small, it helped me understand:

- how Python CLI tools are organized
- how `click` handles arguments and options
- how `rich` improves terminal UX
- how environment variables fit into real projects
- how to support optional integrations cleanly
- how to test both logic and CLI behavior
- how to think about errors and fallback design
- how to make one project easier to run on different operating systems

## Running Tests

### Windows PowerShell

```powershell
.\venv_win\Scripts\python -m unittest -v
```

### Windows CMD

```bat
venv_win\Scripts\python -m unittest -v
```

### Linux / macOS

```bash
./venv/bin/python -m unittest -v
```

## License

MIT
