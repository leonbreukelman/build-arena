# leonbreukelman-engineer pilot source docs

Repo: `/home/leonb/projects/leonbreukelman-engineer`

Selection: Required pilot 3: clean Leon-owned public-site/agent-metadata repo, JavaScript/Python/static-data shape differs from Build Arena and FMC-MCP.

## README.md

```text
# leonbreukelman.engineer

AI-first public presence for making messy cloud, security, infrastructure, and agent-tooling systems easier to reason about. Humans get a concise site; agents get the same public facts through JSON, llms.txt, well-known metadata, and MCP.

## Quick Start

```bash
# Install dependencies
npm install

# Build the site (fails closed if Python/Jinja dependencies are unavailable)
npm run build

# Preview locally
npm run preview

# Deploy to Cloudflare Pages
npm run deploy
```

## Structure

```
/api/v1/          - Structured JSON data for profile, offers, case studies, projects, and capabilities
/prompt/          - Agent representation instructions
/.well-known/     - Discovery protocols (ai.json, agent-card.json)
/human/           - Human-readable HTML pages
/worker/mcp/      - MCP server endpoint (Cloudflare Worker)
/llms.txt         - LLM crawler instructions
```

## For AI Agents

Start at `/llms.txt` or `/.well-known/ai.json` for discovery.

## For Humans

Navigate to `/human/` for the traditional web surface.

## Deployment

Requires:
- `CLOUDFLARE_API_TOKEN` - API token with Pages:Edit and DNS:Edit permissions
- `CLOUDFLARE_ACCOUNT_ID` - Your Cloudflare account ID

Set these as environment variables or in a `.env` file.

## Development

The site is built from JSON data in `/api/v1/`. Edit those files to update content, then rebuild.

`npm run build` runs the Python static-site generator (`scripts/build.py`). It fails closed if dependencies are missing so stale fallback output cannot accidentally republish removed public surfaces. Install Python dependencies with `python3 -m pip install -r scripts/requirements.txt` if needed.

Templates are in `/templates/`. Public pages are generated from the JSON data and the offer/work/about/contact templates.

```

## package.json

```text
{
  "name": "leonbreukelman-engineer",
  "version": "1.0.0",
  "description": "AI-first professional presence for Leon Breukelman",
  "scripts": {
    "build": "bash scripts/build-site.sh",
    "deploy": "npm run build && wrangler pages deploy dist --project-name=leonbreukelman-engineer",
    "dev": "wrangler pages dev dist",
    "preview": "npm run build && wrangler pages dev dist",
    "check:links": "python3 scripts/check-public-links.py"
  },
  "author": "Leon Breukelman",
  "license": "MIT",
  "devDependencies": {
    "wrangler": "^4.0.0"
  }
}

```
