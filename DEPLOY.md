# Deploy & Run Notes — SOPL 2025 Insights Platform

This file contains quick commands and troubleshooting tips for running the dashboard, running tests, and troubleshooting the embedded assistant (Pickaxe).

## Run locally (development)

Create a virtualenv and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the Streamlit app:

```bash
streamlit run app.py --server.port 8501
```

Open the Local URL printed by Streamlit (usually http://localhost:8501).

## Run tests

Make sure project root is on PYTHONPATH so tests can import the top-level `app` module:

```bash
PYTHONPATH=. pytest -q
```

CI (GitHub Actions) is configured to run pytest on PRs and pushes to `main`.

## Troubleshooting the Pickaxe assistant embed

The assistant is embedded using a remote script from `https://studio.pickaxe.co`.
If the assistant UI doesn't appear in the sidebar, try the following:

- Ensure the `Show Assistant Bot (Pickaxe)` checkbox inside the `Upload Data` expander is checked.
- Some corporate networks or Codespaces may block external script hosts. Open Pickaxe Studio in a new tab:
  - https://studio.pickaxe.co
- Use the diagnostics expander in the sidebar (it shows `session_state.show_bot` and a quick action to open Pickaxe Studio).

If you want to disable the embed entirely, comment out the `components.html(...)` call near the bottom of `app.py`.

## CI

A simple CI workflow runs pytest and flake8. The workflow file is at `.github/workflows/ci.yml`.

## Notes

- The app attempts to robustly repair common garbled characters (replacement character U+FFFD) using heuristics. See `_repair_replacement_chars` in `app.py`.
- If your CSV uses cp1252 (Windows) encoding, try the `Encoding` selector in the Upload area or re-save the file with UTF-8.

## Deploying with Docker or Render

You can deploy this app as a container or via a platform like Render that supports Docker images.

1) Build locally with Docker:

```bash
docker build -t sopl-dashboard:latest .
docker run --rm -p 8501:8501 sopl-dashboard:latest
```

2) Use docker-compose for local sharing:

```bash
docker-compose up --build
```

3) GitHub Container Registry + Render (recommended for easy sharing):

- Push to GitHub; GitHub Actions will build and push an image to GHCR (`ghcr.io/<owner>/<repo>:latest`).
- To automatically trigger a Render deploy from the workflow, set these repository secrets:
  - `RENDER_API_KEY` — your Render API key
  - `RENDER_SERVICE_ID` — the Render service ID to deploy

The workflow `.github/workflows/deploy-container.yml` will trigger on push to `main`. See the file for details.

If you want me to set up a one-click Deploy to Render button or help create a Render service from this repo, I can prepare the exact Render service YAML and instructions — I can't create the service or set secrets from here, but I can give you the exact steps to finish the deploy.
