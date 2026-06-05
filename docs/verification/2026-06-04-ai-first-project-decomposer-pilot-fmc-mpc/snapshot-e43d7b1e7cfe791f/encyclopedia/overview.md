# Project Encyclopedia

This generated encyclopedia is a provenance-backed navigation cache, not authoritative truth.
Accepted claims must trace through the ProjectGraph back to disk/git provenance.

## Source inventory

### config

- `config` `.pre-commit-config.yaml` — [source://.pre-commit-config.yaml#L1] — Provenance `prov:3e753b536bef97f1` via `filesystem` confidence `deterministic` hash `503f34c9f403`
- `config` `pyproject.toml` — [source://pyproject.toml#L1] — Provenance `prov:e3613801121c5bb2` via `filesystem` confidence `deterministic` hash `e70bf8f1e517`
- `config` `uv.lock` — [source://uv.lock#L1] — Provenance `prov:d194260c714e1db7` via `filesystem` confidence `deterministic` hash `fec7ff28653a`

### file

- `file` `.env.example` — [source://.env.example#L1] — Provenance `prov:aff5f019c243b68d` via `filesystem` confidence `deterministic` hash `99cdaf4eaea2`

Redacted source signal:

```text
# FMC MCP Server Configuration
# Copy this file to .env and fill in your FMC credentials

# Required: FMC connection details
FMC_HOST=fmc.example.com
FMC_USERNAME=api_user
FMC_[REDACTED]

# Optional: SSL verification (defaults to false for lab environments)
# FMC_VERIFY_SSL=false

# Optional: Overri
```
- `file` `.gitignore` — [source://.gitignore#L1] — Provenance `prov:eafa121ef423efa4` via `filesystem` confidence `deterministic` hash `48b33f9f89ef`
- `file` `LICENSE` — [source://LICENSE#L1] — Provenance `prov:9cda615525fc7237` via `filesystem` confidence `deterministic` hash `c71d239df917`
- `file` `README.md` — [source://README.md#L1] — Provenance `prov:d209dcd4ea586e51` via `filesystem` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `file` `fmc-mcp-spec.md` — [source://fmc-mcp-spec.md#L1] — Provenance `prov:efd5ab447da866a6` via `filesystem` confidence `deterministic` hash `1709c8c43091`
- `file` `src/fmc_mcp/__init__.py` — [source://src/fmc_mcp/__init__.py#L1] — Provenance `prov:b4741bc92619f465` via `filesystem` confidence `deterministic` hash `e3b410a40e58`
- `file` `src/fmc_mcp/__main__.py` — [source://src/fmc_mcp/__main__.py#L1] — Provenance `prov:b49026ac607fe9b3` via `filesystem` confidence `deterministic` hash `d1518c9b8c7c`
- `file` `src/fmc_mcp/client.py` — [source://src/fmc_mcp/client.py#L1] — Provenance `prov:cb622961650cd965` via `filesystem` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `file` `src/fmc_mcp/config.py` — [source://src/fmc_mcp/config.py#L1] — Provenance `prov:7d40c661bae5592f` via `filesystem` confidence `deterministic` hash `f83817eb0668`

Redacted source signal:

```text
"""Configuration management for FMC MCP Server."""

import logging
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class FMCSettings(BaseSettings):
    """FMC connection settings lo
```
- `file` `src/fmc_mcp/resources.py` — [source://src/fmc_mcp/resources.py#L1] — Provenance `prov:6ef41542faabf575` via `filesystem` confidence `deterministic` hash `259e9b783053`
- `file` `src/fmc_mcp/server.py` — [source://src/fmc_mcp/server.py#L1] — Provenance `prov:e70425cf46124a60` via `filesystem` confidence `deterministic` hash `43a848b0fccc`
- `file` `src/fmc_mcp/tools.py` — [source://src/fmc_mcp/tools.py#L1] — Provenance `prov:0241ee750351f0de` via `filesystem` confidence `deterministic` hash `e9b53d858fde`

### markdown_section

- `markdown_section` `API Rate Limits` — symbol `README.md#API Rate Limits` — [source://README.md#L187] — Provenance `prov:b55c3d7c7e2ffa4e` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Claude Desktop Integration` — symbol `README.md#Claude Desktop Integration` — [source://README.md#L133] — Provenance `prov:880c5b5c0bb89d8a` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Clone the repository` — symbol `README.md#Clone the repository` — [source://README.md#L41] — Provenance `prov:0e3c8a6024baf1cd` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Code Quality` — symbol `README.md#Code Quality` — [source://README.md#L177] — Provenance `prov:de1084c7bd850c00` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Configuration` — symbol `README.md#Configuration` — [source://README.md#L55] — Provenance `prov:be98bfb144d0d63d` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Configuration Options` — symbol `README.md#Configuration Options` — [source://README.md#L71] — Provenance `prov:af37eea4aa81145f` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Development` — symbol `README.md#Development` — [source://README.md#L165] — Provenance `prov:b8550b04f85c10ae` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Features` — symbol `README.md#Features` — [source://README.md#L7] — Provenance `prov:f8094141a2ed40b5` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `HTTP/SSE Mode (for Integration Testing)` — symbol `README.md#HTTP/SSE Mode (for Integration Testing)` — [source://README.md#L99] — Provenance `prov:978c310bcf3a49ca` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Install MCP Inspector` — symbol `README.md#Install MCP Inspector` — [source://README.md#L158] — Provenance `prov:164c26df5c2d159f` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Install dependencies` — symbol `README.md#Install dependencies` — [source://README.md#L45] — Provenance `prov:9ef906fcab5d8f79` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Installation` — symbol `README.md#Installation` — [source://README.md#L30] — Provenance `prov:7e356052c87f12d3` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `License` — symbol `README.md#License` — [source://README.md#L210] — Provenance `prov:03af87b11885796d` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Linting` — symbol `README.md#Linting` — [source://README.md#L180] — Provenance `prov:55b0ade56178d875` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `MCP Inspector Testing` — symbol `README.md#MCP Inspector Testing` — [source://README.md#L155] — Provenance `prov:8e0ba711b181fcaf` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `MCP Resources` — symbol `README.md#MCP Resources` — [source://README.md#L14] — Provenance `prov:c0e6218dfe86ce99` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `MCP Server for Cisco FMC` — symbol `README.md#MCP Server for Cisco FMC` — [source://README.md#L1] — Provenance `prov:41d7a8327af85cd1` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `MCP Tools` — symbol `README.md#MCP Tools` — [source://README.md#L23] — Provenance `prov:2d1e84604968d61f` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Or using the CLI entry point` — symbol `README.md#Or using the CLI entry point` — [source://README.md#L95] — Provenance `prov:88928758b6659453` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Prerequisites` — symbol `README.md#Prerequisites` — [source://README.md#L32] — Provenance `prov:864129dbcae2656a` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Run all tests` — symbol `README.md#Run all tests` — [source://README.md#L170] — Provenance `prov:cae380c529d7841a` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Run the server` — symbol `README.md#Run the server` — [source://README.md#L161] — Provenance `prov:921a99dae2dce8ee` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Run with coverage` — symbol `README.md#Run with coverage` — [source://README.md#L173] — Provenance `prov:8cb3faea4b06e8a8` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Running Tests` — symbol `README.md#Running Tests` — [source://README.md#L167] — Provenance `prov:4178913db3eb6169` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Running the Server` — symbol `README.md#Running the Server` — [source://README.md#L87] — Provenance `prov:764c6e3a64aa9edc` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Security Notes` — symbol `README.md#Security Notes` — [source://README.md#L203] — Provenance `prov:7f1ebd28e645bb3d` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Set environment variable for HTTP mode` — symbol `README.md#Set environment variable for HTTP mode` — [source://README.md#L104] — Provenance `prov:e41e7452a8f0b407` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Testing Connection` — symbol `README.md#Testing Connection` — [source://README.md#L127] — Provenance `prov:299ba3c925929370` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Type checking` — symbol `README.md#Type checking` — [source://README.md#L183] — Provenance `prov:43249604ac7cf524` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Usage` — symbol `README.md#Usage` — [source://README.md#L85] — Provenance `prov:cbd206592b187cc9` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Using pip` — symbol `README.md#Using pip` — [source://README.md#L49] — Provenance `prov:119062338a0fcc11` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Using uv` — symbol `README.md#Using uv` — [source://README.md#L92] — Provenance `prov:8e8f768a903f897d` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `Using uv (Recommended)` — symbol `README.md#Using uv (Recommended)` — [source://README.md#L38] — Provenance `prov:533a54b24e6d2969` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `stdio Mode (Default - for Claude Desktop)` — symbol `README.md#stdio Mode (Default - for Claude Desktop)` — [source://README.md#L89] — Provenance `prov:a2f9a17e49e49eac` via `markdown_parser` confidence `deterministic` hash `4026ce04783d`

Redacted source signal:

```text
# MCP Server for Cisco FMC

A read-only Model Context Protocol (MCP) server for Cisco Firepower Management Center (FMC) 7.4.x.

This server allows LLMs like Claude to query your firewall configuration, search for network objects, and check deployment status—all through natural language.

## Features
```
- `markdown_section` `**1. MVP Objectives & Scope**` — symbol `fmc-mcp-spec.md#**1. MVP Objectives & Scope**` — [source://fmc-mcp-spec.md#L7] — Provenance `prov:0782e5f6e1b40692` via `markdown_parser` confidence `deterministic` hash `1709c8c43091`
- `markdown_section` `**2. Revised Constraints & Resiliency Strategy**` — symbol `fmc-mcp-spec.md#**2. Revised Constraints & Resiliency Strategy**` — [source://fmc-mcp-spec.md#L19] — Provenance `prov:714e1f0ad5615a0a` via `markdown_parser` confidence `deterministic` hash `1709c8c43091`
- `markdown_section` `**3. Authentication & Transport Architecture**` — symbol `fmc-mcp-spec.md#**3. Authentication & Transport Architecture**` — [source://fmc-mcp-spec.md#L34] — Provenance `prov:e089aca494c890dc` via `markdown_parser` confidence `deterministic` hash `1709c8c43091`
- `markdown_section` `**4. MCP Resource Mapping (Read-Only)**` — symbol `fmc-mcp-spec.md#**4. MCP Resource Mapping (Read-Only)**` — [source://fmc-mcp-spec.md#L78] — Provenance `prov:97da06ceced6d29a` via `markdown_parser` confidence `deterministic` hash `1709c8c43091`
- `markdown_section` `**5. MCP Tools (Read-Only Queries)**` — symbol `fmc-mcp-spec.md#**5. MCP Tools (Read-Only Queries)**` — [source://fmc-mcp-spec.md#L107] — Provenance `prov:0ab5485cf83e8e93` via `markdown_parser` confidence `deterministic` hash `1709c8c43091`
- `markdown_section` `**6. Project Structure (MVP)**` — symbol `fmc-mcp-spec.md#**6. Project Structure (MVP)**` — [source://fmc-mcp-spec.md#L123] — Provenance `prov:1c32b251bca16bcb` via `markdown_parser` confidence `deterministic` hash `1709c8c43091`
- `markdown_section` `**7. Implementation Plan (Step-by-Step)**` — symbol `fmc-mcp-spec.md#**7. Implementation Plan (Step-by-Step)**` — [source://fmc-mcp-spec.md#L140] — Provenance `prov:77e421b26123fa4b` via `markdown_parser` confidence `deterministic` hash `1709c8c43091`
- `markdown_section` `**Refined Code Snippet: The Pagination Logic**` — symbol `fmc-mcp-spec.md#**Refined Code Snippet: The Pagination Logic**` — [source://fmc-mcp-spec.md#L172] — Provenance `prov:da28d4d0cd63f372` via `markdown_parser` confidence `deterministic` hash `1709c8c43091`
- `markdown_section` `**Technical Design Document: Cisco FMC Read-Only MCP Server (MVP)**` — symbol `fmc-mcp-spec.md#**Technical Design Document: Cisco FMC Read-Only MCP Server (MVP)**` — [source://fmc-mcp-spec.md#L5] — Provenance `prov:8a4dacdab5c5bb9c` via `markdown_parser` confidence `deterministic` hash `1709c8c43091`
- `markdown_section` `Enforcing the 10-connection limit from feedback` — symbol `fmc-mcp-spec.md#Enforcing the 10-connection limit from feedback` — [source://fmc-mcp-spec.md#L65] — Provenance `prov:db1ae8af1e4ea3b2` via `markdown_parser` confidence `deterministic` hash `1709c8c43091`
- `markdown_section` `src/fmc.py` — symbol `fmc-mcp-spec.md#src/fmc.py` — [source://fmc-mcp-spec.md#L177] — Provenance `prov:d19d3d8e819cc977` via `markdown_parser` confidence `deterministic` hash `1709c8c43091`

### project

- `project` `fmc-mcp` — [source://project] — Provenance `prov:project:3c8e6d4b88f9a8b7` via `git` confidence `deterministic` hash `3c8e6d4b88f9`

### python_class

- `python_class` `FMCClient` — symbol `fmc_mcp.client.FMCClient` — [source://src/fmc_mcp/client.py#L65] — Provenance `prov:18b0c8871bdafce4` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_class` `RateLimiter` — symbol `fmc_mcp.client.RateLimiter` — [source://src/fmc_mcp/client.py#L16] — Provenance `prov:6922c4cbc76c847b` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_class` `FMCSettings` — symbol `fmc_mcp.config.FMCSettings` — [source://src/fmc_mcp/config.py#L12] — Provenance `prov:a9e9273cfe1c61b5` via `python_ast` confidence `deterministic` hash `f83817eb0668`

Redacted source signal:

```text
"""Configuration management for FMC MCP Server."""

import logging
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class FMCSettings(BaseSettings):
    """FMC connection settings lo
```
- `python_class` `TestFMCClient` — symbol `tests.test_client.TestFMCClient` — [source://tests/test_client.py#L29] — Provenance `prov:b9e960142dcb9ea5` via `python_ast` confidence `deterministic` hash `2b585e7273f0`

Redacted source signal:

```text
"""Tests for FMC client."""

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient, RateLimiter
from fmc_mcp.config import FMCSettings


class TestRateLimiter:
    """Tests for the RateLimiter class."""

    @pytest.mark.asyncio
    async def test_acquire_token(self)
```
- `python_class` `TestRateLimiter` — symbol `tests.test_client.TestRateLimiter` — [source://tests/test_client.py#L10] — Provenance `prov:6ee931714d574d45` via `python_ast` confidence `deterministic` hash `2b585e7273f0`

Redacted source signal:

```text
"""Tests for FMC client."""

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient, RateLimiter
from fmc_mcp.config import FMCSettings


class TestRateLimiter:
    """Tests for the RateLimiter class."""

    @pytest.mark.asyncio
    async def test_acquire_token(self)
```
- `python_class` `TestResources` — symbol `tests.test_resources.TestResources` — [source://tests/test_resources.py#L37] — Provenance `prov:35ebe3a05dfb61ea` via `python_ast` confidence `deterministic` hash `70e75562f3a1`
- `python_class` `TestTools` — symbol `tests.test_resources.TestTools` — [source://tests/test_resources.py#L82] — Provenance `prov:c57441decd9b395c` via `python_ast` confidence `deterministic` hash `70e75562f3a1`

### python_function

- `python_function` `__aenter__` — symbol `fmc_mcp.client.__aenter__` — [source://src/fmc_mcp/client.py#L97] — Provenance `prov:f7d930f9242cdf6b` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_function` `__aexit__` — symbol `fmc_mcp.client.__aexit__` — [source://src/fmc_mcp/client.py#L102] — Provenance `prov:1b3f2c1d7897a7d9` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_function` `__init__` — symbol `fmc_mcp.client.__init__` — [source://src/fmc_mcp/client.py#L68] — Provenance `prov:9734a80e5a0aa51f` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_function` `_authenticate` — symbol `fmc_mcp.client._authenticate` — [source://src/fmc_mcp/client.py#L136] — Provenance `prov:4a7607b917067ce1` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_function` `_refill` — symbol `fmc_mcp.client._refill` — [source://src/fmc_mcp/client.py#L57] — Provenance `prov:e6637d97bcb4c874` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_function` `_refresh_auth_token` — symbol `fmc_mcp.client._refresh_auth_token` — [source://src/fmc_mcp/client.py#L170] — Provenance `prov:911fe64a8a563f4a` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_function` `_request` — symbol `fmc_mcp.client._request` — [source://src/fmc_mcp/client.py#L219] — Provenance `prov:5ab061c5e7644b3b` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_function` `acquire` — symbol `fmc_mcp.client.acquire` — [source://src/fmc_mcp/client.py#L32] — Provenance `prov:1dcdb60f3cd2d9b7` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_function` `base_url` — symbol `fmc_mcp.client.base_url` — [source://src/fmc_mcp/client.py#L88] — Provenance `prov:762795fe8b07b883` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_function` `close` — symbol `fmc_mcp.client.close` — [source://src/fmc_mcp/client.py#L127] — Provenance `prov:5545b2c1b69e08a3` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_function` `connect` — symbol `fmc_mcp.client.connect` — [source://src/fmc_mcp/client.py#L106] — Provenance `prov:8ef0247e5bf6d05d` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_function` `domain_uuid` — symbol `fmc_mcp.client.domain_uuid` — [source://src/fmc_mcp/client.py#L93] — Provenance `prov:655157d7f34b01d3` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_function` `get` — symbol `fmc_mcp.client.get` — [source://src/fmc_mcp/client.py#L265] — Provenance `prov:50daf627e73eb5d4` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_function` `get_all_items` — symbol `fmc_mcp.client.get_all_items` — [source://src/fmc_mcp/client.py#L276] — Provenance `prov:8bc6b516dc0b436f` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_function` `get_deployable_devices` — symbol `fmc_mcp.client.get_deployable_devices` — [source://src/fmc_mcp/client.py#L350] — Provenance `prov:8b4e55af20732ac6` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_function` `get_devices` — symbol `fmc_mcp.client.get_devices` — [source://src/fmc_mcp/client.py#L335] — Provenance `prov:c7518e8eb39130cf` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_function` `get_domain_info` — symbol `fmc_mcp.client.get_domain_info` — [source://src/fmc_mcp/client.py#L331] — Provenance `prov:dcca6daf179a5f4c` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_function` `get_host_objects` — symbol `fmc_mcp.client.get_host_objects` — [source://src/fmc_mcp/client.py#L345] — Provenance `prov:df3a9487fe343323` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_function` `get_json` — symbol `fmc_mcp.client.get_json` — [source://src/fmc_mcp/client.py#L269] — Provenance `prov:bb311405d7893be6` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_function` `get_network_objects` — symbol `fmc_mcp.client.get_network_objects` — [source://src/fmc_mcp/client.py#L340] — Provenance `prov:870e595051701097` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_function` `get_server_version` — symbol `fmc_mcp.client.get_server_version` — [source://src/fmc_mcp/client.py#L327] — Provenance `prov:77f6ea0500ad864c` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_function` `test_connection` — symbol `fmc_mcp.client.test_connection` — [source://src/fmc_mcp/client.py#L365] — Provenance `prov:92742fc0a75e8da2` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_function` `get_settings` — symbol `fmc_mcp.config.get_settings` — [source://src/fmc_mcp/config.py#L55] — Provenance `prov:c8f5f3e6b252fc58` via `python_ast` confidence `deterministic` hash `f83817eb0668`

Redacted source signal:

```text
"""Configuration management for FMC MCP Server."""

import logging
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class FMCSettings(BaseSettings):
    """FMC connection settings lo
```
- `python_function` `log_config` — symbol `fmc_mcp.config.log_config` — [source://src/fmc_mcp/config.py#L36] — Provenance `prov:fd5b9444de7916dc` via `python_ast` confidence `deterministic` hash `f83817eb0668`

Redacted source signal:

```text
"""Configuration management for FMC MCP Server."""

import logging
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class FMCSettings(BaseSettings):
    """FMC connection settings lo
```
- `python_function` `get_client` — symbol `fmc_mcp.resources.get_client` — [source://src/fmc_mcp/resources.py#L22] — Provenance `prov:187cb860ee557503` via `python_ast` confidence `deterministic` hash `259e9b783053`
- `python_function` `get_deployment_status` — symbol `fmc_mcp.resources.get_deployment_status` — [source://src/fmc_mcp/resources.py#L92] — Provenance `prov:a77f09fd05b8d122` via `python_ast` confidence `deterministic` hash `259e9b783053`
- `python_function` `get_system_info` — symbol `fmc_mcp.resources.get_system_info` — [source://src/fmc_mcp/resources.py#L29] — Provenance `prov:f66191feea1cc687` via `python_ast` confidence `deterministic` hash `259e9b783053`
- `python_function` `list_devices` — symbol `fmc_mcp.resources.list_devices` — [source://src/fmc_mcp/resources.py#L40] — Provenance `prov:bec0ec8d4b515a01` via `python_ast` confidence `deterministic` hash `259e9b783053`
- `python_function` `list_network_objects` — symbol `fmc_mcp.resources.list_network_objects` — [source://src/fmc_mcp/resources.py#L67] — Provenance `prov:5432e12dd9b06188` via `python_ast` confidence `deterministic` hash `259e9b783053`
- `python_function` `set_client` — symbol `fmc_mcp.resources.set_client` — [source://src/fmc_mcp/resources.py#L16] — Provenance `prov:f38f20980d380538` via `python_ast` confidence `deterministic` hash `259e9b783053`
- `python_function` `deployment_status_resource` — symbol `fmc_mcp.server.deployment_status_resource` — [source://src/fmc_mcp/server.py#L85] — Provenance `prov:4de3689c602c27c8` via `python_ast` confidence `deterministic` hash `43a848b0fccc`
- `python_function` `devices_list_resource` — symbol `fmc_mcp.server.devices_list_resource` — [source://src/fmc_mcp/server.py#L73] — Provenance `prov:37ab6cf2892de795` via `python_ast` confidence `deterministic` hash `43a848b0fccc`
- `python_function` `get_deployment_status` — symbol `fmc_mcp.server.get_deployment_status` — [source://src/fmc_mcp/server.py#L105] — Provenance `prov:819e17895eea1040` via `python_ast` confidence `deterministic` hash `43a848b0fccc`
- `python_function` `lifespan` — symbol `fmc_mcp.server.lifespan` — [source://src/fmc_mcp/server.py#L27] — Provenance `prov:c6bbdfa1c267b0ff` via `python_ast` confidence `deterministic` hash `43a848b0fccc`
- `python_function` `main` — symbol `fmc_mcp.server.main` — [source://src/fmc_mcp/server.py#L117] — Provenance `prov:b5271f40f46ff232` via `python_ast` confidence `deterministic` hash `43a848b0fccc`
- `python_function` `network_objects_resource` — symbol `fmc_mcp.server.network_objects_resource` — [source://src/fmc_mcp/server.py#L79] — Provenance `prov:e4d3ef2280bcf7de` via `python_ast` confidence `deterministic` hash `43a848b0fccc`
- `python_function` `search_object_by_ip` — symbol `fmc_mcp.server.search_object_by_ip` — [source://src/fmc_mcp/server.py#L92] — Provenance `prov:85323dd67853d257` via `python_ast` confidence `deterministic` hash `43a848b0fccc`
- `python_function` `system_info_resource` — symbol `fmc_mcp.server.system_info_resource` — [source://src/fmc_mcp/server.py#L67] — Provenance `prov:9044166d96fafc27` via `python_ast` confidence `deterministic` hash `43a848b0fccc`
- `python_function` `check_deployment_status` — symbol `fmc_mcp.tools.check_deployment_status` — [source://src/fmc_mcp/tools.py#L93] — Provenance `prov:1908bb239917dc71` via `python_ast` confidence `deterministic` hash `e9b53d858fde`
- `python_function` `search_object_by_ip` — symbol `fmc_mcp.tools.search_object_by_ip` — [source://src/fmc_mcp/tools.py#L12] — Provenance `prov:1f43efdcff932aea` via `python_ast` confidence `deterministic` hash `e9b53d858fde`
- `python_function` `fmc_client` — symbol `tests.conftest.fmc_client` — [source://tests/conftest.py#L25] — Provenance `prov:f0de02958bc24ecb` via `python_ast` confidence `deterministic` hash `0d437b7a9fc1`

Redacted source signal:

```text
"""Pytest fixtures for FMC MCP tests."""

import re

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient
from fmc_mcp.config import FMCSettings


@pytest.fixture
def fmc_settings() -> FMCSettings:
    """Create test FMC settings."""
    return FMCSettings(
```
- `python_function` `fmc_settings` — symbol `tests.conftest.fmc_settings` — [source://tests/conftest.py#L13] — Provenance `prov:8fb0e3e063883119` via `python_ast` confidence `deterministic` hash `0d437b7a9fc1`

Redacted source signal:

```text
"""Pytest fixtures for FMC MCP tests."""

import re

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient
from fmc_mcp.config import FMCSettings


@pytest.fixture
def fmc_settings() -> FMCSettings:
    """Create test FMC settings."""
    return FMCSettings(
```
- `python_function` `mock_auth_response` — symbol `tests.conftest.mock_auth_response` — [source://tests/conftest.py#L31] — Provenance `prov:4f319b2cfae58f1b` via `python_ast` confidence `deterministic` hash `0d437b7a9fc1`

Redacted source signal:

```text
"""Pytest fixtures for FMC MCP tests."""

import re

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient
from fmc_mcp.config import FMCSettings


@pytest.fixture
def fmc_settings() -> FMCSettings:
    """Create test FMC settings."""
    return FMCSettings(
```
- `python_function` `mock_deployable_devices` — symbol `tests.conftest.mock_deployable_devices` — [source://tests/conftest.py#L141] — Provenance `prov:cba37443cecefc78` via `python_ast` confidence `deterministic` hash `0d437b7a9fc1`

Redacted source signal:

```text
"""Pytest fixtures for FMC MCP tests."""

import re

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient
from fmc_mcp.config import FMCSettings


@pytest.fixture
def fmc_settings() -> FMCSettings:
    """Create test FMC settings."""
    return FMCSettings(
```
- `python_function` `mock_devices` — symbol `tests.conftest.mock_devices` — [source://tests/conftest.py#L60] — Provenance `prov:46fe9767c5347ca4` via `python_ast` confidence `deterministic` hash `0d437b7a9fc1`

Redacted source signal:

```text
"""Pytest fixtures for FMC MCP tests."""

import re

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient
from fmc_mcp.config import FMCSettings


@pytest.fixture
def fmc_settings() -> FMCSettings:
    """Create test FMC settings."""
    return FMCSettings(
```
- `python_function` `mock_host_objects` — symbol `tests.conftest.mock_host_objects` — [source://tests/conftest.py#L120] — Provenance `prov:0c89e2ef46a22715` via `python_ast` confidence `deterministic` hash `0d437b7a9fc1`

Redacted source signal:

```text
"""Pytest fixtures for FMC MCP tests."""

import re

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient
from fmc_mcp.config import FMCSettings


@pytest.fixture
def fmc_settings() -> FMCSettings:
    """Create test FMC settings."""
    return FMCSettings(
```
- `python_function` `mock_network_objects` — symbol `tests.conftest.mock_network_objects` — [source://tests/conftest.py#L92] — Provenance `prov:ddd6f48cdc67467b` via `python_ast` confidence `deterministic` hash `0d437b7a9fc1`

Redacted source signal:

```text
"""Pytest fixtures for FMC MCP tests."""

import re

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient
from fmc_mcp.config import FMCSettings


@pytest.fixture
def fmc_settings() -> FMCSettings:
    """Create test FMC settings."""
    return FMCSettings(
```
- `python_function` `mock_server_version` — symbol `tests.conftest.mock_server_version` — [source://tests/conftest.py#L46] — Provenance `prov:6766d512b10bb683` via `python_ast` confidence `deterministic` hash `0d437b7a9fc1`

Redacted source signal:

```text
"""Pytest fixtures for FMC MCP tests."""

import re

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient
from fmc_mcp.config import FMCSettings


@pytest.fixture
def fmc_settings() -> FMCSettings:
    """Create test FMC settings."""
    return FMCSettings(
```
- `python_function` `test_acquire_token` — symbol `tests.test_client.test_acquire_token` — [source://tests/test_client.py#L14] — Provenance `prov:55c376cef7131912` via `python_ast` confidence `deterministic` hash `2b585e7273f0`

Redacted source signal:

```text
"""Tests for FMC client."""

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient, RateLimiter
from fmc_mcp.config import FMCSettings


class TestRateLimiter:
    """Tests for the RateLimiter class."""

    @pytest.mark.asyncio
    async def test_acquire_token(self)
```
- `python_function` `test_authentication` — symbol `tests.test_client.test_authentication` — [source://tests/test_client.py#L54] — Provenance `prov:15b0d9ea38dc8b30` via `python_ast` confidence `deterministic` hash `2b585e7273f0`

Redacted source signal:

```text
"""Tests for FMC client."""

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient, RateLimiter
from fmc_mcp.config import FMCSettings


class TestRateLimiter:
    """Tests for the RateLimiter class."""

    @pytest.mark.asyncio
    async def test_acquire_token(self)
```
- `python_function` `test_base_url` — symbol `tests.test_client.test_base_url` — [source://tests/test_client.py#L32] — Provenance `prov:f45e6d71592c9856` via `python_ast` confidence `deterministic` hash `2b585e7273f0`

Redacted source signal:

```text
"""Tests for FMC client."""

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient, RateLimiter
from fmc_mcp.config import FMCSettings


class TestRateLimiter:
    """Tests for the RateLimiter class."""

    @pytest.mark.asyncio
    async def test_acquire_token(self)
```
- `python_function` `test_context_manager` — symbol `tests.test_client.test_context_manager` — [source://tests/test_client.py#L154] — Provenance `prov:f06cf30b5c86d1c2` via `python_ast` confidence `deterministic` hash `2b585e7273f0`

Redacted source signal:

```text
"""Tests for FMC client."""

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient, RateLimiter
from fmc_mcp.config import FMCSettings


class TestRateLimiter:
    """Tests for the RateLimiter class."""

    @pytest.mark.asyncio
    async def test_acquire_token(self)
```
- `python_function` `test_domain_uuid_default` — symbol `tests.test_client.test_domain_uuid_default` — [source://tests/test_client.py#L42] — Provenance `prov:a71d2f3991b3dd12` via `python_ast` confidence `deterministic` hash `2b585e7273f0`

Redacted source signal:

```text
"""Tests for FMC client."""

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient, RateLimiter
from fmc_mcp.config import FMCSettings


class TestRateLimiter:
    """Tests for the RateLimiter class."""

    @pytest.mark.asyncio
    async def test_acquire_token(self)
```
- `python_function` `test_domain_uuid_from_settings` — symbol `tests.test_client.test_domain_uuid_from_settings` — [source://tests/test_client.py#L37] — Provenance `prov:6cbbcad30f824c02` via `python_ast` confidence `deterministic` hash `2b585e7273f0`

Redacted source signal:

```text
"""Tests for FMC client."""

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient, RateLimiter
from fmc_mcp.config import FMCSettings


class TestRateLimiter:
    """Tests for the RateLimiter class."""

    @pytest.mark.asyncio
    async def test_acquire_token(self)
```
- `python_function` `test_get_devices` — symbol `tests.test_client.test_get_devices` — [source://tests/test_client.py#L78] — Provenance `prov:74a62232073e2d4d` via `python_ast` confidence `deterministic` hash `2b585e7273f0`

Redacted source signal:

```text
"""Tests for FMC client."""

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient, RateLimiter
from fmc_mcp.config import FMCSettings


class TestRateLimiter:
    """Tests for the RateLimiter class."""

    @pytest.mark.asyncio
    async def test_acquire_token(self)
```
- `python_function` `test_get_network_objects` — symbol `tests.test_client.test_get_network_objects` — [source://tests/test_client.py#L92] — Provenance `prov:d2fa68e702a0336c` via `python_ast` confidence `deterministic` hash `2b585e7273f0`

Redacted source signal:

```text
"""Tests for FMC client."""

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient, RateLimiter
from fmc_mcp.config import FMCSettings


class TestRateLimiter:
    """Tests for the RateLimiter class."""

    @pytest.mark.asyncio
    async def test_acquire_token(self)
```
- `python_function` `test_get_server_version` — symbol `tests.test_client.test_get_server_version` — [source://tests/test_client.py#L66] — Provenance `prov:678dfaeef0318b9e` via `python_ast` confidence `deterministic` hash `2b585e7273f0`

Redacted source signal:

```text
"""Tests for FMC client."""

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient, RateLimiter
from fmc_mcp.config import FMCSettings


class TestRateLimiter:
    """Tests for the RateLimiter class."""

    @pytest.mark.asyncio
    async def test_acquire_token(self)
```
- `python_function` `test_multiple_acquires` — symbol `tests.test_client.test_multiple_acquires` — [source://tests/test_client.py#L21] — Provenance `prov:cd0d5846490d61ee` via `python_ast` confidence `deterministic` hash `2b585e7273f0`

Redacted source signal:

```text
"""Tests for FMC client."""

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient, RateLimiter
from fmc_mcp.config import FMCSettings


class TestRateLimiter:
    """Tests for the RateLimiter class."""

    @pytest.mark.asyncio
    async def test_acquire_token(self)
```
- `python_function` `test_token_refresh_on_401` — symbol `tests.test_client.test_token_refresh_on_401` — [source://tests/test_client.py#L105] — Provenance `prov:dbd8f33c88bc1bc7` via `python_ast` confidence `deterministic` hash `2b585e7273f0`

Redacted source signal:

```text
"""Tests for FMC client."""

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient, RateLimiter
from fmc_mcp.config import FMCSettings


class TestRateLimiter:
    """Tests for the RateLimiter class."""

    @pytest.mark.asyncio
    async def test_acquire_token(self)
```
- `python_function` `run_live_tests` — symbol `tests.test_live.run_live_tests` — [source://tests/test_live.py#L7] — Provenance `prov:ff6bd90548c917c9` via `python_ast` confidence `deterministic` hash `4d99c8f269d3`
- `python_function` `initialized_client` — symbol `tests.test_resources.initialized_client` — [source://tests/test_resources.py#L14] — Provenance `prov:33210c991062bd14` via `python_ast` confidence `deterministic` hash `70e75562f3a1`
- `python_function` `test_check_deployment_status` — symbol `tests.test_resources.test_check_deployment_status` — [source://tests/test_resources.py#L129] — Provenance `prov:8bc3f37c78ecc091` via `python_ast` confidence `deterministic` hash `70e75562f3a1`
- `python_function` `test_check_deployment_status_filtered` — symbol `tests.test_resources.test_check_deployment_status_filtered` — [source://tests/test_resources.py#L143] — Provenance `prov:e18356a7426b1c56` via `python_ast` confidence `deterministic` hash `70e75562f3a1`
- `python_function` `test_get_system_info` — symbol `tests.test_resources.test_get_system_info` — [source://tests/test_resources.py#L41] — Provenance `prov:8b510a4b6b46d7b9` via `python_ast` confidence `deterministic` hash `70e75562f3a1`
- `python_function` `test_list_devices` — symbol `tests.test_resources.test_list_devices` — [source://tests/test_resources.py#L58] — Provenance `prov:8be16bde66785662` via `python_ast` confidence `deterministic` hash `70e75562f3a1`
- `python_function` `test_list_network_objects` — symbol `tests.test_resources.test_list_network_objects` — [source://tests/test_resources.py#L70] — Provenance `prov:20e2b0c7e921513b` via `python_ast` confidence `deterministic` hash `70e75562f3a1`
- `python_function` `test_search_object_by_ip_found` — symbol `tests.test_resources.test_search_object_by_ip_found` — [source://tests/test_resources.py#L86] — Provenance `prov:45436d74f269afd8` via `python_ast` confidence `deterministic` hash `70e75562f3a1`
- `python_function` `test_search_object_by_ip_not_found` — symbol `tests.test_resources.test_search_object_by_ip_not_found` — [source://tests/test_resources.py#L104] — Provenance `prov:2864ea7baaeacc06` via `python_ast` confidence `deterministic` hash `70e75562f3a1`
- `python_function` `test_search_object_invalid_ip` — symbol `tests.test_resources.test_search_object_invalid_ip` — [source://tests/test_resources.py#L118] — Provenance `prov:1a9b1dd4e2694f13` via `python_ast` confidence `deterministic` hash `70e75562f3a1`

### python_import

- `python_import` `fmc_mcp.server` — symbol `fmc_mcp.server` — [source://src/fmc_mcp/__main__.py#L3] — Provenance `prov:e08d506150373eea` via `python_ast` confidence `deterministic` hash `d1518c9b8c7c`
- `python_import` `base64` — symbol `base64` — [source://src/fmc_mcp/client.py#L4] — Provenance `prov:aefc03705172d5d2` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_import` `httpx` — symbol `httpx` — [source://src/fmc_mcp/client.py#L9] — Provenance `prov:2b0e52ad10883e7c` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_import` `time` — symbol `time` — [source://src/fmc_mcp/client.py#L6] — Provenance `prov:4d9c0f2751d94893` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_import` `functools` — symbol `functools` — [source://src/fmc_mcp/config.py#L4] — Provenance `prov:b65ed2f73ad4b018` via `python_ast` confidence `deterministic` hash `f83817eb0668`

Redacted source signal:

```text
"""Configuration management for FMC MCP Server."""

import logging
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class FMCSettings(BaseSettings):
    """FMC connection settings lo
```
- `python_import` `pydantic` — symbol `pydantic` — [source://src/fmc_mcp/config.py#L6] — Provenance `prov:8725a89bbd7df351` via `python_ast` confidence `deterministic` hash `f83817eb0668`

Redacted source signal:

```text
"""Configuration management for FMC MCP Server."""

import logging
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class FMCSettings(BaseSettings):
    """FMC connection settings lo
```
- `python_import` `pydantic_settings` — symbol `pydantic_settings` — [source://src/fmc_mcp/config.py#L7] — Provenance `prov:9b83bc4546b8b4e1` via `python_ast` confidence `deterministic` hash `f83817eb0668`

Redacted source signal:

```text
"""Configuration management for FMC MCP Server."""

import logging
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class FMCSettings(BaseSettings):
    """FMC connection settings lo
```
- `python_import` `typing` — symbol `typing` — [source://src/fmc_mcp/resources.py#L5] — Provenance `prov:d144243cb5366326` via `python_ast` confidence `deterministic` hash `259e9b783053`
- `python_import` `collections.abc` — symbol `collections.abc` — [source://src/fmc_mcp/server.py#L6] — Provenance `prov:e89e94d1a731f1ff` via `python_ast` confidence `deterministic` hash `43a848b0fccc`
- `python_import` `contextlib` — symbol `contextlib` — [source://src/fmc_mcp/server.py#L7] — Provenance `prov:24bdbe0f3b14496c` via `python_ast` confidence `deterministic` hash `43a848b0fccc`
- `python_import` `mcp.server.fastmcp` — symbol `mcp.server.fastmcp` — [source://src/fmc_mcp/server.py#L9] — Provenance `prov:224f5fd127caa0f7` via `python_ast` confidence `deterministic` hash `43a848b0fccc`
- `python_import` `os` — symbol `os` — [source://src/fmc_mcp/server.py#L5] — Provenance `prov:c73e700453853f20` via `python_ast` confidence `deterministic` hash `43a848b0fccc`
- `python_import` `fmc_mcp.resources` — symbol `fmc_mcp.resources` — [source://src/fmc_mcp/tools.py#L7] — Provenance `prov:3dfa2aaf889c6db2` via `python_ast` confidence `deterministic` hash `e9b53d858fde`
- `python_import` `ipaddress` — symbol `ipaddress` — [source://src/fmc_mcp/tools.py#L3] — Provenance `prov:12c675fbe4c747a2` via `python_ast` confidence `deterministic` hash `e9b53d858fde`
- `python_import` `logging` — symbol `logging` — [source://src/fmc_mcp/tools.py#L5] — Provenance `prov:4feb4d0cf75bcc4f` via `python_ast` confidence `deterministic` hash `e9b53d858fde`
- `python_import` `re` — symbol `re` — [source://tests/conftest.py#L3] — Provenance `prov:ae87ab4ea45ccc08` via `python_ast` confidence `deterministic` hash `0d437b7a9fc1`

Redacted source signal:

```text
"""Pytest fixtures for FMC MCP tests."""

import re

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient
from fmc_mcp.config import FMCSettings


@pytest.fixture
def fmc_settings() -> FMCSettings:
    """Create test FMC settings."""
    return FMCSettings(
```
- `python_import` `asyncio` — symbol `asyncio` — [source://tests/test_live.py#L3] — Provenance `prov:e496bca825291938` via `python_ast` confidence `deterministic` hash `4d99c8f269d3`
- `python_import` `fmc_mcp` — symbol `fmc_mcp` — [source://tests/test_resources.py#L8] — Provenance `prov:a57ff323145ecac8` via `python_ast` confidence `deterministic` hash `70e75562f3a1`
- `python_import` `fmc_mcp.client` — symbol `fmc_mcp.client` — [source://tests/test_resources.py#L9] — Provenance `prov:83bfaa715796cf55` via `python_ast` confidence `deterministic` hash `70e75562f3a1`
- `python_import` `fmc_mcp.config` — symbol `fmc_mcp.config` — [source://tests/test_resources.py#L10] — Provenance `prov:aae72e2816907c8a` via `python_ast` confidence `deterministic` hash `70e75562f3a1`
- `python_import` `json` — symbol `json` — [source://tests/test_resources.py#L3] — Provenance `prov:f303603fb23efae7` via `python_ast` confidence `deterministic` hash `70e75562f3a1`
- `python_import` `pytest` — symbol `pytest` — [source://tests/test_resources.py#L5] — Provenance `prov:e21a2b29c8d4da4e` via `python_ast` confidence `deterministic` hash `70e75562f3a1`
- `python_import` `pytest_httpx` — symbol `pytest_httpx` — [source://tests/test_resources.py#L6] — Provenance `prov:7966cc91ad067962` via `python_ast` confidence `deterministic` hash `70e75562f3a1`

### python_module

- `python_module` `fmc_mcp` — symbol `fmc_mcp` — [source://src/fmc_mcp/__init__.py#L1] — Provenance `prov:aeec7a1dae758e4e` via `python_ast` confidence `deterministic` hash `e3b410a40e58`
- `python_module` `fmc_mcp.__main__` — symbol `fmc_mcp.__main__` — [source://src/fmc_mcp/__main__.py#L1] — Provenance `prov:da6e96a18d26d1cf` via `python_ast` confidence `deterministic` hash `d1518c9b8c7c`
- `python_module` `fmc_mcp.client` — symbol `fmc_mcp.client` — [source://src/fmc_mcp/client.py#L1] — Provenance `prov:bcfd8e782d7fe500` via `python_ast` confidence `deterministic` hash `a86716583c10`

Redacted source signal:

```text
"""FMC API Client with authentication, rate limiting, and pagination."""

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

from fmc_mcp.config import FMCSettings, get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket
```
- `python_module` `fmc_mcp.config` — symbol `fmc_mcp.config` — [source://src/fmc_mcp/config.py#L1] — Provenance `prov:b380701c2879efce` via `python_ast` confidence `deterministic` hash `f83817eb0668`

Redacted source signal:

```text
"""Configuration management for FMC MCP Server."""

import logging
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class FMCSettings(BaseSettings):
    """FMC connection settings lo
```
- `python_module` `fmc_mcp.resources` — symbol `fmc_mcp.resources` — [source://src/fmc_mcp/resources.py#L1] — Provenance `prov:4e62ae79d2c07a9c` via `python_ast` confidence `deterministic` hash `259e9b783053`
- `python_module` `fmc_mcp.server` — symbol `fmc_mcp.server` — [source://src/fmc_mcp/server.py#L1] — Provenance `prov:d10dbb159e6fb524` via `python_ast` confidence `deterministic` hash `43a848b0fccc`
- `python_module` `fmc_mcp.tools` — symbol `fmc_mcp.tools` — [source://src/fmc_mcp/tools.py#L1] — Provenance `prov:750d7fda533e438c` via `python_ast` confidence `deterministic` hash `e9b53d858fde`
- `python_module` `tests.conftest` — symbol `tests.conftest` — [source://tests/conftest.py#L1] — Provenance `prov:6194b3ec63deb31b` via `python_ast` confidence `deterministic` hash `0d437b7a9fc1`

Redacted source signal:

```text
"""Pytest fixtures for FMC MCP tests."""

import re

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient
from fmc_mcp.config import FMCSettings


@pytest.fixture
def fmc_settings() -> FMCSettings:
    """Create test FMC settings."""
    return FMCSettings(
```
- `python_module` `tests.test_client` — symbol `tests.test_client` — [source://tests/test_client.py#L1] — Provenance `prov:cf2e2af8a187bdfc` via `python_ast` confidence `deterministic` hash `2b585e7273f0`

Redacted source signal:

```text
"""Tests for FMC client."""

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient, RateLimiter
from fmc_mcp.config import FMCSettings


class TestRateLimiter:
    """Tests for the RateLimiter class."""

    @pytest.mark.asyncio
    async def test_acquire_token(self)
```
- `python_module` `tests.test_live` — symbol `tests.test_live` — [source://tests/test_live.py#L1] — Provenance `prov:d0c4ff32123f1070` via `python_ast` confidence `deterministic` hash `4d99c8f269d3`
- `python_module` `tests.test_resources` — symbol `tests.test_resources` — [source://tests/test_resources.py#L1] — Provenance `prov:ad7d6b890de863c8` via `python_ast` confidence `deterministic` hash `70e75562f3a1`

### test_file

- `test_file` `tests/conftest.py` — [source://tests/conftest.py#L1] — Provenance `prov:2ec577ac92faac85` via `filesystem` confidence `deterministic` hash `0d437b7a9fc1`

Redacted source signal:

```text
"""Pytest fixtures for FMC MCP tests."""

import re

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient
from fmc_mcp.config import FMCSettings


@pytest.fixture
def fmc_settings() -> FMCSettings:
    """Create test FMC settings."""
    return FMCSettings(
```
- `test_file` `tests/test_client.py` — [source://tests/test_client.py#L1] — Provenance `prov:f0afb0af699cae96` via `filesystem` confidence `deterministic` hash `2b585e7273f0`

Redacted source signal:

```text
"""Tests for FMC client."""

import pytest
from pytest_httpx import HTTPXMock

from fmc_mcp.client import FMCClient, RateLimiter
from fmc_mcp.config import FMCSettings


class TestRateLimiter:
    """Tests for the RateLimiter class."""

    @pytest.mark.asyncio
    async def test_acquire_token(self)
```
- `test_file` `tests/test_live.py` — [source://tests/test_live.py#L1] — Provenance `prov:de169aac696fc2e0` via `filesystem` confidence `deterministic` hash `4d99c8f269d3`
- `test_file` `tests/test_resources.py` — [source://tests/test_resources.py#L1] — Provenance `prov:36f0f61015ae8d33` via `filesystem` confidence `deterministic` hash `70e75562f3a1`
