# leonbreukelman-engineer local verification

Command: `bash -lc 'npm run build && npm run check:links'`

CWD: `/home/leonb/projects/leonbreukelman-engineer`

Return code: `0`

```text

> leonbreukelman-engineer@1.0.0 build
> bash scripts/build-site.sh

Building leonbreukelman.engineer...
Building human pages...
Copying machine-readable surfaces and assets...
Build complete! Output in /home/leonb/projects/leonbreukelman-engineer/dist

> leonbreukelman-engineer@1.0.0 check:links
> python3 scripts/check-public-links.py

Checking 8 public URLs
OK 200 https://cmmc-level1-readiness-assistant.pages.dev -> https://cmmc-level1-readiness-assistant.pages.dev
    api/v1/projects.json:42
    dist/api/v1/projects.json:42
    dist/human/work/index.html:155
OK 200 https://github.com/leonbreukelman -> https://github.com/leonbreukelman
    api/v1/profile.json:55
    dist/api/v1/profile.json:55
    dist/human/contact/index.html:82
    dist/human/contact/index.html:82
    dist/llms.txt:37
OK 200 https://github.com/leonbreukelman/fmc-mcp -> https://github.com/leonbreukelman/fmc-mcp
    api/v1/case_studies.json:15
    api/v1/projects.json:16
    dist/api/v1/case_studies.json:15
    dist/api/v1/projects.json:16
    dist/human/work/index.html:88
OK 200 https://leonbreukelman.engineer -> https://leonbreukelman.engineer/human/
    api/v1/profile.json:54
    dist/api/v1/profile.json:54
OK 200 https://leonbreukelman.engineer/.well-known/security.txt -> https://leonbreukelman.engineer/.well-known/security.txt
    dist/well-known/security.txt:5
    well-known/security.txt:5
OK 200 https://leonbreukelman.engineer/assets/schema/ai.json -> https://leonbreukelman.engineer/assets/schema/ai.json
    dist/well-known/ai.json:2
    well-known/ai.json:2
OK 200 https://leonbreukelman.engineer/mcp/ -> https://leonbreukelman.engineer/mcp/
    dist/well-known/agent-card.json:4
    well-known/agent-card.json:4
OK 200 https://schema.org/Person -> https://schema.org/Person
    api/v1/profile.json:2
    dist/api/v1/profile.json:2


```
