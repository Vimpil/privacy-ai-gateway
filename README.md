# Cipher Oracle

Privacy-focused AI gateway with encrypted frontend/backend exchange, local Ollama inference, and tamper-evident audit logs.

## Project Structure

```text
backend/
  app/
	api/routes/
	ai/
	audit/
	crypto/
	core/
	schemas/
	services/
  data/
  tests/
  requirements.txt
frontend/
  public/
  src/
	components/
	crypto/
	pages/
	services/
	types/
docs/
```

## Quick Start

1. Create local env files (from project root):

```powershell
Copy-Item .\backend\.env.example .\backend\.env
Copy-Item .\frontend\.env.example .\frontend\.env
```

2. Start backend (Terminal 1):

```powershell
Set-Location .\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

3. Start frontend (Terminal 2):

```powershell
Set-Location .\frontend
npm install
npx vite --host=127.0.0.1 --port=5173
```

4. Open:
   - Frontend: `http://127.0.0.1:5173`
   - Backend health: `http://127.0.0.1:8000/health`

See `docs/architecture.md` for the flow and module responsibilities.

## Troubleshooting (Windows)

- PowerShell blocks `Activate.ps1`: run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then retry activation.
- `python` or `npm` is not recognized: restart terminal after installing Python/Node, then verify with `python --version` and `npm --version`.
- Port already in use (`8000` or `5173`): either stop the process using that port or run with a different port, for example `--port 8001` or `--port 5174`.

