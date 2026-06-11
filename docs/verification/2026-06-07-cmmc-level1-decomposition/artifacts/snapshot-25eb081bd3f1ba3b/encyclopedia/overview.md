# Project Encyclopedia

This generated encyclopedia is a provenance-backed navigation cache, not authoritative truth.
Accepted claims must trace through the ProjectGraph back to disk/git provenance.

## Source inventory

### config

- `config` `.github/workflows/ci.yml` — [source://.github/workflows/ci.yml#L1] — Provenance `prov:36f704e3958f671e` via `filesystem` confidence `deterministic` hash `8e33f96abfd0`
- `config` `app/Dockerfile` — [source://app/Dockerfile#L1] — Provenance `prov:77411b12becccc72` via `filesystem` confidence `deterministic` hash `7a901ec72f59`
- `config` `app/backend/Dockerfile` — [source://app/backend/Dockerfile#L1] — Provenance `prov:944fc72201ac9628` via `filesystem` confidence `deterministic` hash `1671b96f7bfa`
- `config` `app/backend/alembic.ini` — [source://app/backend/alembic.ini#L1] — Provenance `prov:630701ac2ce98b36` via `filesystem` confidence `deterministic` hash `2cee2be1c9cb`
- `config` `app/backend/pyproject.toml` — [source://app/backend/pyproject.toml#L1] — Provenance `prov:7ca29d04c604aa4b` via `filesystem` confidence `deterministic` hash `cac1d98c71d8`
- `config` `app/backend/uv.lock` — [source://app/backend/uv.lock#L1] — Provenance `prov:c64789dc2e90deaa` via `filesystem` confidence `deterministic` hash `b127e48c580f`
- `config` `app/control-library/cmmc_level_1_controls.json` — [source://app/control-library/cmmc_level_1_controls.json#L1] — Provenance `prov:a73fbccca0591d63` via `filesystem` confidence `deterministic` hash `ec1c5e5bd3c1`
- `config` `app/docker-compose.yml` — [source://app/docker-compose.yml#L1] — Provenance `prov:c84f229fb5b8026d` via `filesystem` confidence `deterministic` hash `6121948387c3`

Redacted source signal:

```text
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: cmmc
      POSTGRES_USER: cmmc
      POSTGRES_[REDACTED]
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379
```
- `config` `app/frontend/Dockerfile` — [source://app/frontend/Dockerfile#L1] — Provenance `prov:1f0eee3db2c6a848` via `filesystem` confidence `deterministic` hash `e3a793667967`
- `config` `app/frontend/package-lock.json` — [source://app/frontend/package-lock.json#L1] — Provenance `prov:458126f5dce04700` via `filesystem` confidence `deterministic` hash `fdc8084e8242`
- `config` `app/frontend/package.json` — [source://app/frontend/package.json#L1] — Provenance `prov:a7422b4e47542bbd` via `filesystem` confidence `deterministic` hash `6502eeb52ad7`
- `config` `app/frontend/tsconfig.json` — [source://app/frontend/tsconfig.json#L1] — Provenance `prov:84bed5620537e3f1` via `filesystem` confidence `deterministic` hash `17a48426c42e`
- `config` `app/frontend/wrangler.toml` — [source://app/frontend/wrangler.toml#L1] — Provenance `prov:0daaa22742716415` via `filesystem` confidence `deterministic` hash `560489705438`

### file

- `file` `.gitignore` — [source://.gitignore#L1] — Provenance `prov:43db4ebdccf08212` via `filesystem` confidence `deterministic` hash `a8c7d70a5d42`
- `file` `AGENTS.md` — [source://AGENTS.md#L1] — Provenance `prov:6d84fccfbe3e8053` via `filesystem` confidence `deterministic` hash `53a723759d3f`
- `file` `README.md` — [source://README.md#L1] — Provenance `prov:bcbb9b8d1dfd9e70` via `filesystem` confidence `deterministic` hash `74de9a637a54`
- `file` `app/.dockerignore` — [source://app/.dockerignore#L1] — Provenance `prov:31f593555a8c9e61` via `filesystem` confidence `deterministic` hash `29159ad688c3`
- `file` `app/.env` — [source://app/.env#L1] — Provenance `prov:c50cefab05a87d7f` via `filesystem` confidence `deterministic` hash `2414abba5456`

Redacted source signal:

```text
# Backend
DATABASE_URL=[REDACTED]
CORS_ORIGINS=http://localhost:5173,http://localhost:8080
AUTH_DEMO_USER_ID=demo-user
AUTH_DEMO_ORG_ID=demo-org
RATE_LIMIT=120/minute
CONTROL_LIBRARY_PATH=/app/control-library/cmmc_level_1_controls.json

# LLM provider abstracti
```
- `file` `app/.env.example` — [source://app/.env.example#L1] — Provenance `prov:bd9e5c41456922a2` via `filesystem` confidence `deterministic` hash `39339f2b5104`

Redacted source signal:

```text
# Development environment example for local Docker Compose.
# Copy to .env for local development only. This file is not a production template.

# Backend
ENVIRONMENT=development
DATABASE_URL=[REDACTED]
CORS_ORIGINS=http://localhost:5173,http://localhost:8080,ht
```
- `file` `app/.env.production.example` — [source://app/.env.production.example#L1] — Provenance `prov:a2e8f4683d538d84` via `filesystem` confidence `deterministic` hash `e4bdcdd9196d`

Redacted source signal:

```text
# Production environment template for architecture planning only.
# This is NOT sufficient to deploy: production auth is intentionally not implemented yet.
# Do not add real secrets to this file. Configure secrets in the selected hosting platform.

# Frontend / Cloudflare Pages build variables
# Con
```
- `file` `app/.gcloudignore` — [source://app/.gcloudignore#L1] — Provenance `prov:64503739ab5ea696` via `filesystem` confidence `deterministic` hash `d5882b3e7b21`
- `file` `app/README.md` — [source://app/README.md#L1] — Provenance `prov:b2de52a7d8b82ef6` via `filesystem` confidence `deterministic` hash `c2bd322911b5`

Redacted source signal:

```text
# CMMC Level 1 Self-Assessment Readiness Assistant

MVP web application for small DoD contractors preparing a CMMC Level 1 self-assessment readiness package for Federal Contract Information.

This is a readiness and self-assessment support tool. It does not certify the customer, does not submit to S
```
- `file` `app/backend/alembic/env.py` — [source://app/backend/alembic/env.py#L1] — Provenance `prov:ba0bd2c06958bc7b` via `filesystem` confidence `deterministic` hash `df239fcd8a00`
- `file` `app/backend/alembic/versions/0001_initial.py` — [source://app/backend/alembic/versions/0001_initial.py#L1] — Provenance `prov:07e9af3773357e2a` via `filesystem` confidence `deterministic` hash `b9a82ba6452a`
- `file` `app/backend/alembic/versions/0002_audit_event_organization_id.py` — [source://app/backend/alembic/versions/0002_audit_event_organization_id.py#L1] — Provenance `prov:0ed6be78bc13a2dd` via `filesystem` confidence `deterministic` hash `0077daca005a`
- `file` `app/backend/alembic/versions/0003_lock_down_supabase_public_table_grants.py` — [source://app/backend/alembic/versions/0003_lock_down_supabase_public_table_grants.py#L1] — Provenance `prov:5be7fa9a8f3ff777` via `filesystem` confidence `deterministic` hash `f8d102a94cee`
- `file` `app/backend/alembic/versions/0004_cmmc_app_rls_policies.py` — [source://app/backend/alembic/versions/0004_cmmc_app_rls_policies.py#L1] — Provenance `prov:5f2807c2a1509f75` via `filesystem` confidence `deterministic` hash `581de9538af5`
- `file` `app/backend/alembic/versions/0005_audit_events_append_only.py` — [source://app/backend/alembic/versions/0005_audit_events_append_only.py#L1] — Provenance `prov:d8a55df2a3373452` via `filesystem` confidence `deterministic` hash `ab3203863f37`
- `file` `app/backend/alembic/versions/0006_auth_access_grants.py` — [source://app/backend/alembic/versions/0006_auth_access_grants.py#L1] — Provenance `prov:18aab3d3bc040aa1` via `filesystem` confidence `deterministic` hash `5c03e5e2eb9a`
- `file` `app/backend/src/__init__.py` — [source://app/backend/src/__init__.py#L1] — Provenance `prov:de6e321536b47865` via `filesystem` confidence `deterministic` hash `e3b0c44298fc`
- `file` `app/backend/src/api/__init__.py` — [source://app/backend/src/api/__init__.py#L1] — Provenance `prov:010671fe1976e4eb` via `filesystem` confidence `deterministic` hash `e3b0c44298fc`
- `file` `app/backend/src/assessment/__init__.py` — [source://app/backend/src/assessment/__init__.py#L1] — Provenance `prov:ac60255313a07280` via `filesystem` confidence `deterministic` hash `e3b0c44298fc`
- `file` `app/backend/src/assessment/confirmation.py` — [source://app/backend/src/assessment/confirmation.py#L1] — Provenance `prov:145e679758f65f42` via `filesystem` confidence `deterministic` hash `4be7bcac76c0`
- `file` `app/backend/src/assessment/schemas.py` — [source://app/backend/src/assessment/schemas.py#L1] — Provenance `prov:aa55c621b9dd78ca` via `filesystem` confidence `deterministic` hash `711cffe52aae`

Redacted source signal:

```text
from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Annotated, Literal
from urllib.parse import parse_qsl, urlsplit
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator, model_validator


SENSITIVE_EXTERNAL_REFERENCE_QUERY_K
```
- `file` `app/backend/src/assessment/scope_parser.py` — [source://app/backend/src/assessment/scope_parser.py#L1] — Provenance `prov:0c26a2c0aae6db35` via `filesystem` confidence `deterministic` hash `ee57f4af7744`
- `file` `app/backend/src/assessment/state_machine.py` — [source://app/backend/src/assessment/state_machine.py#L1] — Provenance `prov:5282996faed3a572` via `filesystem` confidence `deterministic` hash `e775d84f4f5b`
- `file` `app/backend/src/assessment/text_analysis.py` — [source://app/backend/src/assessment/text_analysis.py#L1] — Provenance `prov:28b0348a40e11b2a` via `filesystem` confidence `deterministic` hash `bde2b7bcb7dc`
- `file` `app/backend/src/audit/__init__.py` — [source://app/backend/src/audit/__init__.py#L1] — Provenance `prov:068103396b37c369` via `filesystem` confidence `deterministic` hash `e3b0c44298fc`
- `file` `app/backend/src/audit/events.py` — [source://app/backend/src/audit/events.py#L1] — Provenance `prov:8ae353d62342d40d` via `filesystem` confidence `deterministic` hash `f7f9a7793f84`
- `file` `app/backend/src/auth/__init__.py` — [source://app/backend/src/auth/__init__.py#L1] — Provenance `prov:6515df72383901c3` via `filesystem` confidence `deterministic` hash `e3b0c44298fc`
- `file` `app/backend/src/auth/dependencies.py` — [source://app/backend/src/auth/dependencies.py#L1] — Provenance `prov:2813737ed437aafc` via `filesystem` confidence `deterministic` hash `d5edc52e827b`

Redacted source signal:

```text
from dataclasses import dataclass
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from config.settings import get_settings
from database.base import get_db
from database.models import AuthAccessGrant, Organization, User, AssessmentSession, now_utc
from audit.ev
```
- `file` `app/backend/src/auth/public_beta.py` — [source://app/backend/src/auth/public_beta.py#L1] — Provenance `prov:88752517dfd0e284` via `filesystem` confidence `deterministic` hash `77b86338d3da`

Redacted source signal:

```text
import base64
import hashlib
import hmac
import json
from dataclasses import dataclass


class PublicBetaTokenError(ValueError):
    pass


@dataclass(frozen=True)
class PublicBetaClaims:
    organization_id: str
    user_id: str
    email: str
    organization_name: str


def _b64encode(raw: bytes)
```
- `file` `app/backend/src/auth/supabase.py` — [source://app/backend/src/auth/supabase.py#L1] — Provenance `prov:7e8407e69e4f973a` via `filesystem` confidence `deterministic` hash `e5b0506670d2`

Redacted source signal:

```text
from dataclasses import dataclass
from functools import lru_cache
from ipaddress import ip_address
from socket import inet_aton
from urllib.parse import urlparse

import jwt
from jwt import PyJWKClient, PyJWTError


class SupabaseTokenError(ValueError):
    pass


@dataclass(frozen=True)
class Supab
```
- `file` `app/backend/src/config/__init__.py` — [source://app/backend/src/config/__init__.py#L1] — Provenance `prov:715241e975a5b443` via `filesystem` confidence `deterministic` hash `e3b0c44298fc`
- `file` `app/backend/src/config/settings.py` — [source://app/backend/src/config/settings.py#L1] — Provenance `prov:b043a9809df0398a` via `filesystem` confidence `deterministic` hash `a7f19740b398`

Redacted source signal:

```text
from functools import lru_cache
from ipaddress import ip_address
from socket import inet_aton
from urllib.parse import urlparse

from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigurationError(RuntimeError):
    pass


class Settings(BaseSettings):
    app_name: str = "CMMC
```
- `file` `app/backend/src/controls/__init__.py` — [source://app/backend/src/controls/__init__.py#L1] — Provenance `prov:1ee627a311d5cb33` via `filesystem` confidence `deterministic` hash `e3b0c44298fc`
- `file` `app/backend/src/controls/library.py` — [source://app/backend/src/controls/library.py#L1] — Provenance `prov:30d187e32f93a50e` via `filesystem` confidence `deterministic` hash `611f90f5e7eb`
- `file` `app/backend/src/controls/seed.py` — [source://app/backend/src/controls/seed.py#L1] — Provenance `prov:afaacc6b80c4a561` via `filesystem` confidence `deterministic` hash `ded57d70dafb`
- `file` `app/backend/src/database/__init__.py` — [source://app/backend/src/database/__init__.py#L1] — Provenance `prov:09f75adf2d3e5c7a` via `filesystem` confidence `deterministic` hash `e3b0c44298fc`
- `file` `app/backend/src/database/base.py` — [source://app/backend/src/database/base.py#L1] — Provenance `prov:2555e3439da84190` via `filesystem` confidence `deterministic` hash `17ab4e8d2bd7`
- `file` `app/backend/src/database/models.py` — [source://app/backend/src/database/models.py#L1] — Provenance `prov:7e4a332a93d794a6` via `filesystem` confidence `deterministic` hash `fcb520456941`
- `file` `app/backend/src/evidence/__init__.py` — [source://app/backend/src/evidence/__init__.py#L1] — Provenance `prov:cee6ba6fc6e5c243` via `filesystem` confidence `deterministic` hash `e3b0c44298fc`
- `file` `app/backend/src/llm/__init__.py` — [source://app/backend/src/llm/__init__.py#L1] — Provenance `prov:df5b5342a7b4d4ba` via `filesystem` confidence `deterministic` hash `e3b0c44298fc`
- `file` `app/backend/src/llm/client.py` — [source://app/backend/src/llm/client.py#L1] — Provenance `prov:a32a5a13681fddc7` via `filesystem` confidence `deterministic` hash `31ae98c2afd4`

Redacted source signal:

```text
import json
import logging
from time import perf_counter
from abc import ABC, abstractmethod

import httpx

from assessment.schemas import FindingStatus, LLMAnswerEvaluation
from assessment.text_analysis import classify_stub_answer, extract_evidence_references
from config.settings import get_setting
```
- `file` `app/backend/src/llm/data_boundary.py` — [source://app/backend/src/llm/data_boundary.py#L1] — Provenance `prov:8616d4f0eaf4e436` via `filesystem` confidence `deterministic` hash `804f9a44dec1`
- `file` `app/backend/src/llm/policy.py` — [source://app/backend/src/llm/policy.py#L1] — Provenance `prov:48db8849e262ab9e` via `filesystem` confidence `deterministic` hash `0351fa64b528`
- `file` `app/backend/src/llm/schemas.py` — [source://app/backend/src/llm/schemas.py#L1] — Provenance `prov:72c43004332e9dce` via `filesystem` confidence `deterministic` hash `797672e10df9`
- `file` `app/backend/src/main.py` — [source://app/backend/src/main.py#L1] — Provenance `prov:797d9d7057b1447d` via `filesystem` confidence `deterministic` hash `5a10ae600ecc`
- `file` `app/backend/src/reports/__init__.py` — [source://app/backend/src/reports/__init__.py#L1] — Provenance `prov:f1ad393e9111288a` via `filesystem` confidence `deterministic` hash `e3b0c44298fc`
- `file` `app/backend/src/reports/generator.py` — [source://app/backend/src/reports/generator.py#L1] — Provenance `prov:f142e6aa29cef7e1` via `filesystem` confidence `deterministic` hash `f7e929ccdd20`
- `file` `app/backend/src/reports/readiness.py` — [source://app/backend/src/reports/readiness.py#L1] — Provenance `prov:c921e243698c9f80` via `filesystem` confidence `deterministic` hash `321de5e54dc9`
- `file` `app/backend/src/security/__init__.py` — [source://app/backend/src/security/__init__.py#L1] — Provenance `prov:fef5e603e251200c` via `filesystem` confidence `deterministic` hash `e3b0c44298fc`
- `file` `app/backend/src/security/information_boundary.py` — [source://app/backend/src/security/information_boundary.py#L1] — Provenance `prov:8768aaa927c94cf1` via `filesystem` confidence `deterministic` hash `8bdcd77295de`
- `file` `app/backend/src/security/language.py` — [source://app/backend/src/security/language.py#L1] — Provenance `prov:b07e8a8be6024229` via `filesystem` confidence `deterministic` hash `decb66545081`
- `file` `app/backend/src/security/prompt_injection.py` — [source://app/backend/src/security/prompt_injection.py#L1] — Provenance `prov:77db1db87d960954` via `filesystem` confidence `deterministic` hash `7788ec023a36`

Redacted source signal:

```text
import re

BLOCKED_PATTERNS = [
    re.compile(r"\bignore\s+(?:all\s+)?(?:previous|prior)\s+instructions\b", re.I),
    re.compile(r"\bdisregard\s+(?:the\s+)?(?:rules|instructions)\b", re.I),
    re.compile(r"\bskip\s+(?:the\s+)?(?:rest|remaining\s+controls|controls)\b", re.I),
    re.compile(r"\bma
```
- `file` `app/backend/src/testing/db_safety.py` — [source://app/backend/src/testing/db_safety.py#L1] — Provenance `prov:a4749c3727fe8426` via `filesystem` confidence `deterministic` hash `32e1b5615896`
- `file` `app/backend/tests/conftest.py` — [source://app/backend/tests/conftest.py#L1] — Provenance `prov:2a225b2a6b2e1ce0` via `filesystem` confidence `deterministic` hash `19d2248048a7`
- `file` `app/frontend/.env.production.example` — [source://app/frontend/.env.production.example#L1] — Provenance `prov:cb656ca8838f2ee8` via `filesystem` confidence `deterministic` hash `8fdb0c038d7d`
- `file` `app/frontend/index.html` — [source://app/frontend/index.html#L1] — Provenance `prov:a7780d16c548ae2b` via `filesystem` confidence `deterministic` hash `0b456941e952`
- `file` `app/frontend/scripts/deploy-production.mjs` — [source://app/frontend/scripts/deploy-production.mjs#L1] — Provenance `prov:cdd8e7f486bc82bb` via `filesystem` confidence `deterministic` hash `a6c98dadf4b7`
- `file` `app/frontend/scripts/deploy-production.test.mjs` — [source://app/frontend/scripts/deploy-production.test.mjs#L1] — Provenance `prov:f5abd7dcd5d7c19f` via `filesystem` confidence `deterministic` hash `e71396c1ebbe`
- `file` `app/frontend/scripts/verify-production-deploy.mjs` — [source://app/frontend/scripts/verify-production-deploy.mjs#L1] — Provenance `prov:ad0f2e9e4a1b76d1` via `filesystem` confidence `deterministic` hash `baac50dad534`
- `file` `app/frontend/scripts/verify-production-deploy.test.mjs` — [source://app/frontend/scripts/verify-production-deploy.test.mjs#L1] — Provenance `prov:83ca419bade2ead0` via `filesystem` confidence `deterministic` hash `e66c87dee719`
- `file` `app/frontend/src/api/auth.test.ts` — [source://app/frontend/src/api/auth.test.ts#L1] — Provenance `prov:b488a0024f1b8fd4` via `filesystem` confidence `deterministic` hash `fbef41a899c6`

Redacted source signal:

```text
import { describe, expect, it, vi } from 'vitest';

import { buildGoogleOAuthRedirectTo, getApiAuthorizationHeader, type SupabaseAuthClientLike } from './auth';

function supabaseClientWithToken([REDACTED] | null): SupabaseAuthClientLike {
  return {
    auth: {
      getSession: vi.fn(async () => (
```
- `file` `app/frontend/src/api/auth.ts` — [source://app/frontend/src/api/auth.ts#L1] — Provenance `prov:bb3053d8fda3fb7e` via `filesystem` confidence `deterministic` hash `0e8b8999c9e2`

Redacted source signal:

```text
import { createClient } from '@supabase/supabase-js';
import { resolveAuthMode, resolveSupabaseAnonKey, resolveSupabaseUrl } from './config';
import { getPublicBetaAuthorizationHeader } from './publicBetaAuth';

export interface SupabaseAuthClientLike {
  auth: {
    getSession: () => Promise<{ data
```
- `file` `app/frontend/src/api/betaRequest.test.ts` — [source://app/frontend/src/api/betaRequest.test.ts#L1] — Provenance `prov:990b4fd54439ed4d` via `filesystem` confidence `deterministic` hash `f5213fdb9372`
- `file` `app/frontend/src/api/betaRequest.ts` — [source://app/frontend/src/api/betaRequest.ts#L1] — Provenance `prov:2864cd1bf497e333` via `filesystem` confidence `deterministic` hash `d79cf845ef17`
- `file` `app/frontend/src/api/client.ts` — [source://app/frontend/src/api/client.ts#L1] — Provenance `prov:bdfd2011586f209a` via `filesystem` confidence `deterministic` hash `553e58ddff02`
- `file` `app/frontend/src/api/config.test.ts` — [source://app/frontend/src/api/config.test.ts#L1] — Provenance `prov:a70e6db2cbd173f3` via `filesystem` confidence `deterministic` hash `9f06808271b2`
- `file` `app/frontend/src/api/config.ts` — [source://app/frontend/src/api/config.ts#L1] — Provenance `prov:033a0faaa0ff2be6` via `filesystem` confidence `deterministic` hash `9559378d31c4`
- `file` `app/frontend/src/api/publicBetaAuth.test.ts` — [source://app/frontend/src/api/publicBetaAuth.test.ts#L1] — Provenance `prov:b03fb198e5285e8a` via `filesystem` confidence `deterministic` hash `c2c34ffcea76`

Redacted source signal:

```text
import { describe, expect, it, vi } from 'vitest';

import { getPublicBetaAuthorizationHeader, type TokenStorage } from './publicBetaAuth';

function memoryStorage(initial: Record<string, string> = {}): TokenStorage {
  const values = new Map(Object.entries(initial));
  return {
    getItem: (key: s
```
- `file` `app/frontend/src/api/publicBetaAuth.ts` — [source://app/frontend/src/api/publicBetaAuth.ts#L1] — Provenance `prov:512c859816865dc9` via `filesystem` confidence `deterministic` hash `cb7c848e1c4b`

Redacted source signal:

```text
export const PUBLIC_BETA_TOKEN_STORAGE_KEY = 'cmmc_public_beta_token';

export type TokenStorage = Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>;

type Fetch[REDACTED] string) => Promise<string>;

interface PublicBetaAuthOptions {
  prod: boolean;
  apiBase: string;
  storage?: TokenStorage;
```
- `file` `app/frontend/src/components/AuthGate.tsx` — [source://app/frontend/src/components/AuthGate.tsx#L1] — Provenance `prov:52e6ebb3f4c548b0` via `filesystem` confidence `deterministic` hash `a8c74418470a`
- `file` `app/frontend/src/components/ChatPanel.tsx` — [source://app/frontend/src/components/ChatPanel.tsx#L1] — Provenance `prov:2a7c3a6a79a27e3c` via `filesystem` confidence `deterministic` hash `16c9b4cc8afd`
- `file` `app/frontend/src/components/EvidenceDrawer.tsx` — [source://app/frontend/src/components/EvidenceDrawer.tsx#L1] — Provenance `prov:87c8d8d27ada84b3` via `filesystem` confidence `deterministic` hash `9f0dcfb97225`
- `file` `app/frontend/src/components/FindingReviewPanel.tsx` — [source://app/frontend/src/components/FindingReviewPanel.tsx#L1] — Provenance `prov:1d26b7e8e474ce8c` via `filesystem` confidence `deterministic` hash `e1ed62950bb5`
- `file` `app/frontend/src/components/ProgressSidebar.tsx` — [source://app/frontend/src/components/ProgressSidebar.tsx#L1] — Provenance `prov:48514e1d8c540a6d` via `filesystem` confidence `deterministic` hash `84ebf4bd70e1`
- `file` `app/frontend/src/components/RemediationDashboard.tsx` — [source://app/frontend/src/components/RemediationDashboard.tsx#L1] — Provenance `prov:27de7fe45158123c` via `filesystem` confidence `deterministic` hash `11fe48ade8b4`
- `file` `app/frontend/src/components/ReportPreview.tsx` — [source://app/frontend/src/components/ReportPreview.tsx#L1] — Provenance `prov:b8effc5e04028187` via `filesystem` confidence `deterministic` hash `e4d4c9b499d8`
- `file` `app/frontend/src/components/ScopePanel.test.ts` — [source://app/frontend/src/components/ScopePanel.test.ts#L1] — Provenance `prov:f95e1570ece60e04` via `filesystem` confidence `deterministic` hash `97d54c44ae8d`
- `file` `app/frontend/src/components/ScopePanel.tsx` — [source://app/frontend/src/components/ScopePanel.tsx#L1] — Provenance `prov:1f83f3d3f75ed7db` via `filesystem` confidence `deterministic` hash `544643d58f7b`
- `file` `app/frontend/src/components/accessible-form-controls.test.tsx` — [source://app/frontend/src/components/accessible-form-controls.test.tsx#L1] — Provenance `prov:8f0a8c2244ee2b74` via `filesystem` confidence `deterministic` hash `916e8636f6b1`
- `file` `app/frontend/src/main.tsx` — [source://app/frontend/src/main.tsx#L1] — Provenance `prov:3d188723af895997` via `filesystem` confidence `deterministic` hash `d907d5339aa1`

### javascript_function

- `javascript_function` `ensureCleanTrackedWorktree` — symbol `app.frontend.scripts.deploy-production.ensureCleanTrackedWorktree` — [source://app/frontend/scripts/deploy-production.mjs#L67] — Provenance `prov:c4140267f90de731` via `javascript_regex` confidence `deterministic` hash `a6c98dadf4b7`
- `javascript_function` `fail` — symbol `app.frontend.scripts.deploy-production.fail` — [source://app/frontend/scripts/deploy-production.mjs#L15] — Provenance `prov:81e9559dc7eb64e7` via `javascript_regex` confidence `deterministic` hash `a6c98dadf4b7`
- `javascript_function` `main` — symbol `app.frontend.scripts.deploy-production.main` — [source://app/frontend/scripts/deploy-production.mjs#L74] — Provenance `prov:93411422685a0302` via `javascript_regex` confidence `deterministic` hash `a6c98dadf4b7`
- `javascript_function` `output` — symbol `app.frontend.scripts.deploy-production.output` — [source://app/frontend/scripts/deploy-production.mjs#L31] — Provenance `prov:457c3c5a0f80f8f9` via `javascript_regex` confidence `deterministic` hash `a6c98dadf4b7`
- `javascript_function` `run` — symbol `app.frontend.scripts.deploy-production.run` — [source://app/frontend/scripts/deploy-production.mjs#L20] — Provenance `prov:457e8d94ee4f4ae9` via `javascript_regex` confidence `deterministic` hash `a6c98dadf4b7`
- `javascript_function` `validateEnvironment` — symbol `app.frontend.scripts.deploy-production.validateEnvironment` — [source://app/frontend/scripts/deploy-production.mjs#L60] — Provenance `prov:daf7e2b4f0217bbf` via `javascript_regex` confidence `deterministic` hash `a6c98dadf4b7`
- `javascript_function` `validateProductionDeploymentEnv` — symbol `app.frontend.scripts.deploy-production.validateProductionDeploymentEnv` — [source://app/frontend/scripts/deploy-production.mjs#L42] — Provenance `prov:faa18b850da4715a` via `javascript_regex` confidence `deterministic` hash `a6c98dadf4b7`
- `javascript_function` `collectTextFiles` — symbol `app.frontend.scripts.verify-production-deploy.collectTextFiles` — [source://app/frontend/scripts/verify-production-deploy.mjs#L25] — Provenance `prov:86d97683cc8a1a4c` via `javascript_regex` confidence `deterministic` hash `baac50dad534`
- `javascript_function` `main` — symbol `app.frontend.scripts.verify-production-deploy.main` — [source://app/frontend/scripts/verify-production-deploy.mjs#L74] — Provenance `prov:59562b3a542bff8e` via `javascript_regex` confidence `deterministic` hash `baac50dad534`
- `javascript_function` `validateProductionDeployBundle` — symbol `app.frontend.scripts.verify-production-deploy.validateProductionDeployBundle` — [source://app/frontend/scripts/verify-production-deploy.mjs#L40] — Provenance `prov:a0ffac0c0380d884` via `javascript_regex` confidence `deterministic` hash `baac50dad534`
- `javascript_function` `cleanup` — symbol `app.frontend.scripts.verify-production-deploy.test.cleanup` — [source://app/frontend/scripts/verify-production-deploy.test.mjs#L38] — Provenance `prov:052a59f19eec75e7` via `javascript_regex` confidence `deterministic` hash `e66c87dee719`
- `javascript_function` `makeDist` — symbol `app.frontend.scripts.verify-production-deploy.test.makeDist` — [source://app/frontend/scripts/verify-production-deploy.test.mjs#L27] — Provenance `prov:80e720cd53ce6366` via `javascript_regex` confidence `deterministic` hash `e66c87dee719`
- `javascript_function` `productionBundleLines` — symbol `app.frontend.scripts.verify-production-deploy.test.productionBundleLines` — [source://app/frontend/scripts/verify-production-deploy.test.mjs#L12] — Provenance `prov:05b3a24239a07534` via `javascript_regex` confidence `deterministic` hash `e66c87dee719`
- `javascript_function` `supabaseClientWithToken` — symbol `app.frontend.src.api.auth.test.supabaseClientWithToken` — [source://app/frontend/src/api/auth.test.ts#L6] — Provenance `prov:c2d7dfe4ceebe616` via `javascript_regex` confidence `deterministic` hash `fbef41a899c6`

Redacted source signal:

```text
import { describe, expect, it, vi } from 'vitest';

import { buildGoogleOAuthRedirectTo, getApiAuthorizationHeader, type SupabaseAuthClientLike } from './auth';

function supabaseClientWithToken([REDACTED] | null): SupabaseAuthClientLike {
  return {
    auth: {
      getSession: vi.fn(async () => (
```
- `javascript_function` `buildGoogleOAuthRedirectTo` — symbol `app.frontend.src.api.auth.buildGoogleOAuthRedirectTo` — [source://app/frontend/src/api/auth.ts#L63] — Provenance `prov:fc4495ee3e48b4f3` via `javascript_regex` confidence `deterministic` hash `0e8b8999c9e2`

Redacted source signal:

```text
import { createClient } from '@supabase/supabase-js';
import { resolveAuthMode, resolveSupabaseAnonKey, resolveSupabaseUrl } from './config';
import { getPublicBetaAuthorizationHeader } from './publicBetaAuth';

export interface SupabaseAuthClientLike {
  auth: {
    getSession: () => Promise<{ data
```
- `javascript_function` `fetchAuthenticatedUser` — symbol `app.frontend.src.api.auth.fetchAuthenticatedUser` — [source://app/frontend/src/api/auth.ts#L92] — Provenance `prov:416e496c7529b49d` via `javascript_regex` confidence `deterministic` hash `0e8b8999c9e2`

Redacted source signal:

```text
import { createClient } from '@supabase/supabase-js';
import { resolveAuthMode, resolveSupabaseAnonKey, resolveSupabaseUrl } from './config';
import { getPublicBetaAuthorizationHeader } from './publicBetaAuth';

export interface SupabaseAuthClientLike {
  auth: {
    getSession: () => Promise<{ data
```
- `javascript_function` `getApiAuthorizationHeader` — symbol `app.frontend.src.api.auth.getApiAuthorizationHeader` — [source://app/frontend/src/api/auth.ts#L48] — Provenance `prov:1b16eaae9e5b038f` via `javascript_regex` confidence `deterministic` hash `0e8b8999c9e2`

Redacted source signal:

```text
import { createClient } from '@supabase/supabase-js';
import { resolveAuthMode, resolveSupabaseAnonKey, resolveSupabaseUrl } from './config';
import { getPublicBetaAuthorizationHeader } from './publicBetaAuth';

export interface SupabaseAuthClientLike {
  auth: {
    getSession: () => Promise<{ data
```
- `javascript_function` `getBrowserSupabaseClient` — symbol `app.frontend.src.api.auth.getBrowserSupabaseClient` — [source://app/frontend/src/api/auth.ts#L41] — Provenance `prov:f412f98d630ad5a2` via `javascript_regex` confidence `deterministic` hash `0e8b8999c9e2`

Redacted source signal:

```text
import { createClient } from '@supabase/supabase-js';
import { resolveAuthMode, resolveSupabaseAnonKey, resolveSupabaseUrl } from './config';
import { getPublicBetaAuthorizationHeader } from './publicBetaAuth';

export interface SupabaseAuthClientLike {
  auth: {
    getSession: () => Promise<{ data
```
- `javascript_function` `getSupabaseSessionEmail` — symbol `app.frontend.src.api.auth.getSupabaseSessionEmail` — [source://app/frontend/src/api/auth.ts#L86] — Provenance `prov:7ae0ef8e522aa2af` via `javascript_regex` confidence `deterministic` hash `0e8b8999c9e2`

Redacted source signal:

```text
import { createClient } from '@supabase/supabase-js';
import { resolveAuthMode, resolveSupabaseAnonKey, resolveSupabaseUrl } from './config';
import { getPublicBetaAuthorizationHeader } from './publicBetaAuth';

export interface SupabaseAuthClientLike {
  auth: {
    getSession: () => Promise<{ data
```
- `javascript_function` `signInWithGoogle` — symbol `app.frontend.src.api.auth.signInWithGoogle` — [source://app/frontend/src/api/auth.ts#L70] — Provenance `prov:07e99a4a9a5bb828` via `javascript_regex` confidence `deterministic` hash `0e8b8999c9e2`

Redacted source signal:

```text
import { createClient } from '@supabase/supabase-js';
import { resolveAuthMode, resolveSupabaseAnonKey, resolveSupabaseUrl } from './config';
import { getPublicBetaAuthorizationHeader } from './publicBetaAuth';

export interface SupabaseAuthClientLike {
  auth: {
    getSession: () => Promise<{ data
```
- `javascript_function` `signOutOfGoogle` — symbol `app.frontend.src.api.auth.signOutOfGoogle` — [source://app/frontend/src/api/auth.ts#L80] — Provenance `prov:646ae4d2d9202b90` via `javascript_regex` confidence `deterministic` hash `0e8b8999c9e2`

Redacted source signal:

```text
import { createClient } from '@supabase/supabase-js';
import { resolveAuthMode, resolveSupabaseAnonKey, resolveSupabaseUrl } from './config';
import { getPublicBetaAuthorizationHeader } from './publicBetaAuth';

export interface SupabaseAuthClientLike {
  auth: {
    getSession: () => Promise<{ data
```
- `javascript_function` `buildBetaRequestBody` — symbol `app.frontend.src.api.betaRequest.buildBetaRequestBody` — [source://app/frontend/src/api/betaRequest.ts#L10] — Provenance `prov:63dee71cc7758acc` via `javascript_regex` confidence `deterministic` hash `d79cf845ef17`
- `javascript_function` `buildBetaRequestEmailHref` — symbol `app.frontend.src.api.betaRequest.buildBetaRequestEmailHref` — [source://app/frontend/src/api/betaRequest.ts#L30] — Provenance `prov:474121da29e81e21` via `javascript_regex` confidence `deterministic` hash `d79cf845ef17`
- `javascript_function` `assertSafeProductionOrigin` — symbol `app.frontend.src.api.config.assertSafeProductionOrigin` — [source://app/frontend/src/api/config.ts#L46] — Provenance `prov:396ae0c67b22f4a6` via `javascript_regex` confidence `deterministic` hash `9559378d31c4`
- `javascript_function` `isLoopbackHost` — symbol `app.frontend.src.api.config.isLoopbackHost` — [source://app/frontend/src/api/config.ts#L15] — Provenance `prov:8743b899c69ea5ef` via `javascript_regex` confidence `deterministic` hash `9559378d31c4`
- `javascript_function` `isSelfServeAssessmentEnabled` — symbol `app.frontend.src.api.config.isSelfServeAssessmentEnabled` — [source://app/frontend/src/api/config.ts#L72] — Provenance `prov:0898f4d499668afe` via `javascript_regex` confidence `deterministic` hash `9559378d31c4`
- `javascript_function` `isSupabaseAuthMode` — symbol `app.frontend.src.api.config.isSupabaseAuthMode` — [source://app/frontend/src/api/config.ts#L103] — Provenance `prov:aafc4e85ee79f9e8` via `javascript_regex` confidence `deterministic` hash `9559378d31c4`
- `javascript_function` `normalizeOrigin` — symbol `app.frontend.src.api.config.normalizeOrigin` — [source://app/frontend/src/api/config.ts#L38] — Provenance `prov:e189ff3ee1971d09` via `javascript_regex` confidence `deterministic` hash `9559378d31c4`
- `javascript_function` `parseApiBase` — symbol `app.frontend.src.api.config.parseApiBase` — [source://app/frontend/src/api/config.ts#L34] — Provenance `prov:6b2cbf4f7128e2c9` via `javascript_regex` confidence `deterministic` hash `9559378d31c4`
- `javascript_function` `parseOrigin` — symbol `app.frontend.src.api.config.parseOrigin` — [source://app/frontend/src/api/config.ts#L26] — Provenance `prov:94641d4047452e91` via `javascript_regex` confidence `deterministic` hash `9559378d31c4`
- `javascript_function` `resolveApiBase` — symbol `app.frontend.src.api.config.resolveApiBase` — [source://app/frontend/src/api/config.ts#L54] — Provenance `prov:b3038f32730f7f82` via `javascript_regex` confidence `deterministic` hash `9559378d31c4`
- `javascript_function` `resolveAuthMode` — symbol `app.frontend.src.api.config.resolveAuthMode` — [source://app/frontend/src/api/config.ts#L76] — Provenance `prov:82d18f1bada10f49` via `javascript_regex` confidence `deterministic` hash `9559378d31c4`
- `javascript_function` `resolveSupabaseAnonKey` — symbol `app.frontend.src.api.config.resolveSupabaseAnonKey` — [source://app/frontend/src/api/config.ts#L95] — Provenance `prov:f1de4d21e8f22082` via `javascript_regex` confidence `deterministic` hash `9559378d31c4`
- `javascript_function` `resolveSupabaseUrl` — symbol `app.frontend.src.api.config.resolveSupabaseUrl` — [source://app/frontend/src/api/config.ts#L84] — Provenance `prov:638a15f65946e679` via `javascript_regex` confidence `deterministic` hash `9559378d31c4`
- `javascript_function` `validateFrontendBuildConfig` — symbol `app.frontend.src.api.config.validateFrontendBuildConfig` — [source://app/frontend/src/api/config.ts#L107] — Provenance `prov:fec77a8917607c78` via `javascript_regex` confidence `deterministic` hash `9559378d31c4`
- `javascript_function` `memoryStorage` — symbol `app.frontend.src.api.publicBetaAuth.test.memoryStorage` — [source://app/frontend/src/api/publicBetaAuth.test.ts#L6] — Provenance `prov:d4061fd93573a8f2` via `javascript_regex` confidence `deterministic` hash `c2c34ffcea76`

Redacted source signal:

```text
import { describe, expect, it, vi } from 'vitest';

import { getPublicBetaAuthorizationHeader, type TokenStorage } from './publicBetaAuth';

function memoryStorage(initial: Record<string, string> = {}): TokenStorage {
  const values = new Map(Object.entries(initial));
  return {
    getItem: (key: s
```
- `javascript_function` `browserStorage` — symbol `app.frontend.src.api.publicBetaAuth.browserStorage` — [source://app/frontend/src/api/publicBetaAuth.ts#L27] — Provenance `prov:3c38a591984184e2` via `javascript_regex` confidence `deterministic` hash `cb7c848e1c4b`

Redacted source signal:

```text
export const PUBLIC_BETA_TOKEN_STORAGE_KEY = 'cmmc_public_beta_token';

export type TokenStorage = Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>;

type Fetch[REDACTED] string) => Promise<string>;

interface PublicBetaAuthOptions {
  prod: boolean;
  apiBase: string;
  storage?: TokenStorage;
```
- `javascript_function` `getPublicBetaAuthorizationHeader` — symbol `app.frontend.src.api.publicBetaAuth.getPublicBetaAuthorizationHeader` — [source://app/frontend/src/api/publicBetaAuth.ts#L35] — Provenance `prov:3633031e1c3b8a27` via `javascript_regex` confidence `deterministic` hash `cb7c848e1c4b`

Redacted source signal:

```text
export const PUBLIC_BETA_TOKEN_STORAGE_KEY = 'cmmc_public_beta_token';

export type TokenStorage = Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>;

type Fetch[REDACTED] string) => Promise<string>;

interface PublicBetaAuthOptions {
  prod: boolean;
  apiBase: string;
  storage?: TokenStorage;
```
- `javascript_function` `requestPublicBetaToken` — symbol `app.frontend.src.api.publicBetaAuth.requestPublicBetaToken` — [source://app/frontend/src/api/publicBetaAuth.ts#L15] — Provenance `prov:4c957cab3add8253` via `javascript_regex` confidence `deterministic` hash `cb7c848e1c4b`

Redacted source signal:

```text
export const PUBLIC_BETA_TOKEN_STORAGE_KEY = 'cmmc_public_beta_token';

export type TokenStorage = Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>;

type Fetch[REDACTED] string) => Promise<string>;

interface PublicBetaAuthOptions {
  prod: boolean;
  apiBase: string;
  storage?: TokenStorage;
```
- `javascript_function` `AuthGate` — symbol `app.frontend.src.components.AuthGate.AuthGate` — [source://app/frontend/src/components/AuthGate.tsx#L18] — Provenance `prov:0195def73f2fffac` via `javascript_regex` confidence `deterministic` hash `a8c74418470a`
- `javascript_function` `beginGoogleLogin` — symbol `app.frontend.src.components.AuthGate.beginGoogleLogin` — [source://app/frontend/src/components/AuthGate.tsx#L55] — Provenance `prov:505c2fd074631f63` via `javascript_regex` confidence `deterministic` hash `a8c74418470a`
- `javascript_function` `errorStatus` — symbol `app.frontend.src.components.AuthGate.errorStatus` — [source://app/frontend/src/components/AuthGate.tsx#L11] — Provenance `prov:37b1ef35d225d945` via `javascript_regex` confidence `deterministic` hash `a8c74418470a`
- `javascript_function` `refreshAuth` — symbol `app.frontend.src.components.AuthGate.refreshAuth` — [source://app/frontend/src/components/AuthGate.tsx#L25] — Provenance `prov:c279795d441e3ed4` via `javascript_regex` confidence `deterministic` hash `a8c74418470a`
- `javascript_function` `signOut` — symbol `app.frontend.src.components.AuthGate.signOut` — [source://app/frontend/src/components/AuthGate.tsx#L60] — Provenance `prov:99a7e68f9eeaaf50` via `javascript_regex` confidence `deterministic` hash `a8c74418470a`
- `javascript_function` `ChatPanel` — symbol `app.frontend.src.components.ChatPanel.ChatPanel` — [source://app/frontend/src/components/ChatPanel.tsx#L6] — Provenance `prov:76172ed59ae63adc` via `javascript_regex` confidence `deterministic` hash `16c9b4cc8afd`
- `javascript_function` `updateInput` — symbol `app.frontend.src.components.ChatPanel.updateInput` — [source://app/frontend/src/components/ChatPanel.tsx#L9] — Provenance `prov:8ab678c52cfd9dff` via `javascript_regex` confidence `deterministic` hash `16c9b4cc8afd`
- `javascript_function` `EvidenceDrawer` — symbol `app.frontend.src.components.EvidenceDrawer.EvidenceDrawer` — [source://app/frontend/src/components/EvidenceDrawer.tsx#L5] — Provenance `prov:f25b5137f1570085` via `javascript_regex` confidence `deterministic` hash `9f0dcfb97225`
- `javascript_function` `submit` — symbol `app.frontend.src.components.EvidenceDrawer.submit` — [source://app/frontend/src/components/EvidenceDrawer.tsx#L13] — Provenance `prov:1e3f7453cf316372` via `javascript_regex` confidence `deterministic` hash `9f0dcfb97225`
- `javascript_function` `FindingReviewPanel` — symbol `app.frontend.src.components.FindingReviewPanel.FindingReviewPanel` — [source://app/frontend/src/components/FindingReviewPanel.tsx#L6] — Provenance `prov:2926426d41dfaea7` via `javascript_regex` confidence `deterministic` hash `e1ed62950bb5`
- `javascript_function` `confirm` — symbol `app.frontend.src.components.FindingReviewPanel.confirm` — [source://app/frontend/src/components/FindingReviewPanel.tsx#L18] — Provenance `prov:09654334607b7313` via `javascript_regex` confidence `deterministic` hash `e1ed62950bb5`
- `javascript_function` `refresh` — symbol `app.frontend.src.components.FindingReviewPanel.refresh` — [source://app/frontend/src/components/FindingReviewPanel.tsx#L9] — Provenance `prov:cd7c281aca30b9d9` via `javascript_regex` confidence `deterministic` hash `e1ed62950bb5`
- `javascript_function` `revise` — symbol `app.frontend.src.components.FindingReviewPanel.revise` — [source://app/frontend/src/components/FindingReviewPanel.tsx#L28] — Provenance `prov:4c46ce0dbe04776a` via `javascript_regex` confidence `deterministic` hash `e1ed62950bb5`
- `javascript_function` `ProgressSidebar` — symbol `app.frontend.src.components.ProgressSidebar.ProgressSidebar` — [source://app/frontend/src/components/ProgressSidebar.tsx#L4] — Provenance `prov:46bb6b27c5dcdfd1` via `javascript_regex` confidence `deterministic` hash `84ebf4bd70e1`
- `javascript_function` `RemediationDashboard` — symbol `app.frontend.src.components.RemediationDashboard.RemediationDashboard` — [source://app/frontend/src/components/RemediationDashboard.tsx#L6] — Provenance `prov:5954a0f33f5c5e00` via `javascript_regex` confidence `deterministic` hash `11fe48ade8b4`
- `javascript_function` `ReportPreview` — symbol `app.frontend.src.components.ReportPreview.ReportPreview` — [source://app/frontend/src/components/ReportPreview.tsx#L18] — Provenance `prov:e0aeeab5885044d4` via `javascript_regex` confidence `deterministic` hash `e4d4c9b499d8`
- `javascript_function` `downloadPdf` — symbol `app.frontend.src.components.ReportPreview.downloadPdf` — [source://app/frontend/src/components/ReportPreview.tsx#L28] — Provenance `prov:e4031e084592a15e` via `javascript_regex` confidence `deterministic` hash `e4d4c9b499d8`
- `javascript_function` `generate` — symbol `app.frontend.src.components.ReportPreview.generate` — [source://app/frontend/src/components/ReportPreview.tsx#L23] — Provenance `prov:b5ab4ae552e16b00` via `javascript_regex` confidence `deterministic` hash `e4d4c9b499d8`
- `javascript_function` `humanReadableReportStatus` — symbol `app.frontend.src.components.ReportPreview.humanReadableReportStatus` — [source://app/frontend/src/components/ReportPreview.tsx#L6] — Provenance `prov:c7e82be1f36fb8f5` via `javascript_regex` confidence `deterministic` hash `e4d4c9b499d8`
- `javascript_function` `ScopePanel` — symbol `app.frontend.src.components.ScopePanel.ScopePanel` — [source://app/frontend/src/components/ScopePanel.tsx#L92] — Provenance `prov:5d45edfe9ec0a4c6` via `javascript_regex` confidence `deterministic` hash `544643d58f7b`
- `javascript_function` `scopePanelViewModel` — symbol `app.frontend.src.components.ScopePanel.scopePanelViewModel` — [source://app/frontend/src/components/ScopePanel.tsx#L57] — Provenance `prov:f5e7513c41445b6b` via `javascript_regex` confidence `deterministic` hash `544643d58f7b`
- `javascript_function` `valuesFor` — symbol `app.frontend.src.components.ScopePanel.valuesFor` — [source://app/frontend/src/components/ScopePanel.tsx#L39] — Provenance `prov:8b96492967dfd76c` via `javascript_regex` confidence `deterministic` hash `544643d58f7b`
- `javascript_function` `App` — symbol `app.frontend.src.pages.App.App` — [source://app/frontend/src/pages/App.tsx#L11] — Provenance `prov:a0aba8ca4a3d090b` via `javascript_regex` confidence `deterministic` hash `5afe17041c1e`
- `javascript_function` `AiDisclosure` — symbol `app.frontend.src.pages.AssessmentApp.AiDisclosure` — [source://app/frontend/src/pages/AssessmentApp.tsx#L25] — Provenance `prov:4f9ec750e3b087e9` via `javascript_regex` confidence `deterministic` hash `b4093c13c7e7`
- `javascript_function` `AssessmentApp` — symbol `app.frontend.src.pages.AssessmentApp.AssessmentApp` — [source://app/frontend/src/pages/AssessmentApp.tsx#L29] — Provenance `prov:4ac72f15acf2712b` via `javascript_regex` confidence `deterministic` hash `b4093c13c7e7`
- `javascript_function` `buildAiDisclosureText` — symbol `app.frontend.src.pages.AssessmentApp.buildAiDisclosureText` — [source://app/frontend/src/pages/AssessmentApp.tsx#L15] — Provenance `prov:8f3ec0e258f25d35` via `javascript_regex` confidence `deterministic` hash `b4093c13c7e7`
- `javascript_function` `loadSession` — symbol `app.frontend.src.pages.AssessmentApp.loadSession` — [source://app/frontend/src/pages/AssessmentApp.tsx#L58] — Provenance `prov:c260bac85df9798c` via `javascript_regex` confidence `deterministic` hash `b4093c13c7e7`
- `javascript_function` `send` — symbol `app.frontend.src.pages.AssessmentApp.send` — [source://app/frontend/src/pages/AssessmentApp.tsx#L85] — Provenance `prov:e0b2203ae6a092a8` via `javascript_regex` confidence `deterministic` hash `b4093c13c7e7`
- `javascript_function` `start` — symbol `app.frontend.src.pages.AssessmentApp.start` — [source://app/frontend/src/pages/AssessmentApp.tsx#L74] — Provenance `prov:e93b1911c9350c02` via `javascript_regex` confidence `deterministic` hash `b4093c13c7e7`
- `javascript_function` `readFileSync` — symbol `app.frontend.src.vite-env.d.readFileSync` — [source://app/frontend/src/vite-env.d.ts#L7] — Provenance `prov:b8bd01d3f1d61cb8` via `javascript_regex` confidence `deterministic` hash `5641777f2204`

### javascript_import

- `javascript_import` `node:child_process` — symbol `node:child_process` — [source://app/frontend/scripts/deploy-production.mjs#L3] — Provenance `prov:afd2a44e2bb64885` via `javascript_regex` confidence `deterministic` hash `a6c98dadf4b7`
- `javascript_import` `app.frontend.scripts.deploy-production` — symbol `app.frontend.scripts.deploy-production` — [source://app/frontend/scripts/deploy-production.test.mjs#L4] — Provenance `prov:2163e10fa87ed1f7` via `javascript_regex` confidence `deterministic` hash `e71396c1ebbe`
- `javascript_import` `node:url` — symbol `node:url` — [source://app/frontend/scripts/verify-production-deploy.mjs#L5] — Provenance `prov:1ba8d01dabb36df1` via `javascript_regex` confidence `deterministic` hash `baac50dad534`
- `javascript_import` `app.frontend.scripts.verify-production-deploy` — symbol `app.frontend.scripts.verify-production-deploy` — [source://app/frontend/scripts/verify-production-deploy.test.mjs#L8] — Provenance `prov:272dc6804bb1f868` via `javascript_regex` confidence `deterministic` hash `e66c87dee719`
- `javascript_import` `node:os` — symbol `node:os` — [source://app/frontend/scripts/verify-production-deploy.test.mjs#L4] — Provenance `prov:9471e985e1127410` via `javascript_regex` confidence `deterministic` hash `e66c87dee719`
- `javascript_import` `node:path` — symbol `node:path` — [source://app/frontend/scripts/verify-production-deploy.test.mjs#L3] — Provenance `prov:6bba025b15992d91` via `javascript_regex` confidence `deterministic` hash `e66c87dee719`
- `javascript_import` `@supabase/supabase-js` — symbol `@supabase/supabase-js` — [source://app/frontend/src/api/auth.ts#L2] — Provenance `prov:48411cb9efacac22` via `javascript_regex` confidence `deterministic` hash `0e8b8999c9e2`

Redacted source signal:

```text
import { createClient } from '@supabase/supabase-js';
import { resolveAuthMode, resolveSupabaseAnonKey, resolveSupabaseUrl } from './config';
import { getPublicBetaAuthorizationHeader } from './publicBetaAuth';

export interface SupabaseAuthClientLike {
  auth: {
    getSession: () => Promise<{ data
```
- `javascript_import` `app.frontend.src.api.publicBetaAuth` — symbol `app.frontend.src.api.publicBetaAuth` — [source://app/frontend/src/api/publicBetaAuth.test.ts#L4] — Provenance `prov:3338d9369994f66b` via `javascript_regex` confidence `deterministic` hash `c2c34ffcea76`

Redacted source signal:

```text
import { describe, expect, it, vi } from 'vitest';

import { getPublicBetaAuthorizationHeader, type TokenStorage } from './publicBetaAuth';

function memoryStorage(initial: Record<string, string> = {}): TokenStorage {
  const values = new Map(Object.entries(initial));
  return {
    getItem: (key: s
```
- `javascript_import` `app.frontend.src.api.auth` — symbol `app.frontend.src.api.auth` — [source://app/frontend/src/components/AuthGate.tsx#L3] — Provenance `prov:cbba324be2c57d22` via `javascript_regex` confidence `deterministic` hash `a8c74418470a`
- `javascript_import` `react-dom/server` — symbol `react-dom/server` — [source://app/frontend/src/components/accessible-form-controls.test.tsx#L2] — Provenance `prov:93eddaa238360856` via `javascript_regex` confidence `deterministic` hash `916e8636f6b1`
- `javascript_import` `app.frontend.src.pages.App` — symbol `app.frontend.src.pages.App` — [source://app/frontend/src/main.tsx#L4] — Provenance `prov:176899853bc48986` via `javascript_regex` confidence `deterministic` hash `d907d5339aa1`
- `javascript_import` `app.frontend.src.styles.main.css` — symbol `app.frontend.src.styles.main.css` — [source://app/frontend/src/main.tsx#L5] — Provenance `prov:676382a76ae2af10` via `javascript_regex` confidence `deterministic` hash `d907d5339aa1`
- `javascript_import` `react-dom/client` — symbol `react-dom/client` — [source://app/frontend/src/main.tsx#L3] — Provenance `prov:c6b6aaa7cb7e6740` via `javascript_regex` confidence `deterministic` hash `d907d5339aa1`
- `javascript_import` `app.frontend.src.api.betaRequest.ts?raw` — symbol `app.frontend.src.api.betaRequest.ts?raw` — [source://app/frontend/src/pages/App.test.ts#L12] — Provenance `prov:571b742de6d124bc` via `javascript_regex` confidence `deterministic` hash `386edbbe2d0a`
- `javascript_import` `app.frontend.src.api.client.ts?raw` — symbol `app.frontend.src.api.client.ts?raw` — [source://app/frontend/src/pages/App.test.ts#L13] — Provenance `prov:dc8be9f9322cdd1f` via `javascript_regex` confidence `deterministic` hash `386edbbe2d0a`
- `javascript_import` `app.frontend.src.components.AuthGate.tsx?raw` — symbol `app.frontend.src.components.AuthGate.tsx?raw` — [source://app/frontend/src/pages/App.test.ts#L7] — Provenance `prov:ac55d7887f2accd1` via `javascript_regex` confidence `deterministic` hash `386edbbe2d0a`
- `javascript_import` `app.frontend.src.components.ChatPanel.tsx?raw` — symbol `app.frontend.src.components.ChatPanel.tsx?raw` — [source://app/frontend/src/pages/App.test.ts#L10] — Provenance `prov:0318373b7f4f0d53` via `javascript_regex` confidence `deterministic` hash `386edbbe2d0a`
- `javascript_import` `app.frontend.src.components.EvidenceDrawer.tsx?raw` — symbol `app.frontend.src.components.EvidenceDrawer.tsx?raw` — [source://app/frontend/src/pages/App.test.ts#L11] — Provenance `prov:bbab603af70ae02e` via `javascript_regex` confidence `deterministic` hash `386edbbe2d0a`
- `javascript_import` `app.frontend.src.components.RemediationDashboard.tsx?raw` — symbol `app.frontend.src.components.RemediationDashboard.tsx?raw` — [source://app/frontend/src/pages/App.test.ts#L9] — Provenance `prov:6d3e0e6a0b516902` via `javascript_regex` confidence `deterministic` hash `386edbbe2d0a`
- `javascript_import` `app.frontend.src.components.ReportPreview.tsx?raw` — symbol `app.frontend.src.components.ReportPreview.tsx?raw` — [source://app/frontend/src/pages/App.test.ts#L8] — Provenance `prov:6e0db3f19ffa6d20` via `javascript_regex` confidence `deterministic` hash `386edbbe2d0a`
- `javascript_import` `app.frontend.src.pages.App.tsx?raw` — symbol `app.frontend.src.pages.App.tsx?raw` — [source://app/frontend/src/pages/App.test.ts#L5] — Provenance `prov:d49e927e36316b73` via `javascript_regex` confidence `deterministic` hash `386edbbe2d0a`
- `javascript_import` `app.frontend.src.pages.AssessmentApp.tsx?raw` — symbol `app.frontend.src.pages.AssessmentApp.tsx?raw` — [source://app/frontend/src/pages/App.test.ts#L6] — Provenance `prov:5afbe6ac07da25c4` via `javascript_regex` confidence `deterministic` hash `386edbbe2d0a`
- `javascript_import` `node:fs` — symbol `node:fs` — [source://app/frontend/src/pages/App.test.ts#L2] — Provenance `prov:68643ba4e09fe961` via `javascript_regex` confidence `deterministic` hash `386edbbe2d0a`
- `javascript_import` `vitest` — symbol `vitest` — [source://app/frontend/src/pages/App.test.ts#L3] — Provenance `prov:8b6bbcefcff0d6a8` via `javascript_regex` confidence `deterministic` hash `386edbbe2d0a`
- `javascript_import` `app.frontend.src.api.betaRequest` — symbol `app.frontend.src.api.betaRequest` — [source://app/frontend/src/pages/App.tsx#L3] — Provenance `prov:e2e7fd34dcbf112b` via `javascript_regex` confidence `deterministic` hash `5afe17041c1e`
- `javascript_import` `app.frontend.src.components.AuthGate` — symbol `app.frontend.src.components.AuthGate` — [source://app/frontend/src/pages/App.tsx#L5] — Provenance `prov:fe3ce5c0d5a6334a` via `javascript_regex` confidence `deterministic` hash `5afe17041c1e`
- `javascript_import` `app.frontend.src.api.client` — symbol `app.frontend.src.api.client` — [source://app/frontend/src/pages/AssessmentApp.tsx#L3] — Provenance `prov:7a452fe7fb8dd402` via `javascript_regex` confidence `deterministic` hash `b4093c13c7e7`
- `javascript_import` `app.frontend.src.components.ChatPanel` — symbol `app.frontend.src.components.ChatPanel` — [source://app/frontend/src/pages/AssessmentApp.tsx#L4] — Provenance `prov:88079e2ce47364de` via `javascript_regex` confidence `deterministic` hash `b4093c13c7e7`
- `javascript_import` `app.frontend.src.components.EvidenceDrawer` — symbol `app.frontend.src.components.EvidenceDrawer` — [source://app/frontend/src/pages/AssessmentApp.tsx#L5] — Provenance `prov:a71b5bfa7f53215a` via `javascript_regex` confidence `deterministic` hash `b4093c13c7e7`
- `javascript_import` `app.frontend.src.components.FindingReviewPanel` — symbol `app.frontend.src.components.FindingReviewPanel` — [source://app/frontend/src/pages/AssessmentApp.tsx#L6] — Provenance `prov:d8c4312ce3a84629` via `javascript_regex` confidence `deterministic` hash `b4093c13c7e7`
- `javascript_import` `app.frontend.src.components.ProgressSidebar` — symbol `app.frontend.src.components.ProgressSidebar` — [source://app/frontend/src/pages/AssessmentApp.tsx#L7] — Provenance `prov:7b6723ca53948640` via `javascript_regex` confidence `deterministic` hash `b4093c13c7e7`
- `javascript_import` `app.frontend.src.components.RemediationDashboard` — symbol `app.frontend.src.components.RemediationDashboard` — [source://app/frontend/src/pages/AssessmentApp.tsx#L8] — Provenance `prov:583054b506354315` via `javascript_regex` confidence `deterministic` hash `b4093c13c7e7`
- `javascript_import` `app.frontend.src.components.ReportPreview` — symbol `app.frontend.src.components.ReportPreview` — [source://app/frontend/src/pages/AssessmentApp.tsx#L9] — Provenance `prov:f1d659810a815f76` via `javascript_regex` confidence `deterministic` hash `b4093c13c7e7`
- `javascript_import` `app.frontend.src.components.ScopePanel` — symbol `app.frontend.src.components.ScopePanel` — [source://app/frontend/src/pages/AssessmentApp.tsx#L10] — Provenance `prov:8fb12235a4658245` via `javascript_regex` confidence `deterministic` hash `b4093c13c7e7`
- `javascript_import` `app.frontend.src.types` — symbol `app.frontend.src.types` — [source://app/frontend/src/pages/AssessmentApp.tsx#L11] — Provenance `prov:9940d49bc71d408d` via `javascript_regex` confidence `deterministic` hash `b4093c13c7e7`
- `javascript_import` `react` — symbol `react` — [source://app/frontend/src/pages/AssessmentApp.tsx#L2] — Provenance `prov:23633d81095fc401` via `javascript_regex` confidence `deterministic` hash `b4093c13c7e7`
- `javascript_import` `@vitejs/plugin-react` — symbol `@vitejs/plugin-react` — [source://app/frontend/vite.config.ts#L3] — Provenance `prov:9611ce50c451950d` via `javascript_regex` confidence `deterministic` hash `ee6e02042635`
- `javascript_import` `app.frontend.src.api.config` — symbol `app.frontend.src.api.config` — [source://app/frontend/vite.config.ts#L5] — Provenance `prov:1d1e7d6f48755fa7` via `javascript_regex` confidence `deterministic` hash `ee6e02042635`
- `javascript_import` `vite` — symbol `vite` — [source://app/frontend/vite.config.ts#L2] — Provenance `prov:776fc69cd0965486` via `javascript_regex` confidence `deterministic` hash `ee6e02042635`

### javascript_module

- `javascript_module` `app.frontend.scripts.deploy-production` — symbol `app.frontend.scripts.deploy-production` — [source://app/frontend/scripts/deploy-production.mjs#L1] — Provenance `prov:7816661085a81509` via `javascript_regex` confidence `deterministic` hash `a6c98dadf4b7`
- `javascript_module` `app.frontend.scripts.deploy-production.test` — symbol `app.frontend.scripts.deploy-production.test` — [source://app/frontend/scripts/deploy-production.test.mjs#L1] — Provenance `prov:8743d5594c7041f5` via `javascript_regex` confidence `deterministic` hash `e71396c1ebbe`
- `javascript_module` `app.frontend.scripts.verify-production-deploy` — symbol `app.frontend.scripts.verify-production-deploy` — [source://app/frontend/scripts/verify-production-deploy.mjs#L1] — Provenance `prov:7aa242f62de5590f` via `javascript_regex` confidence `deterministic` hash `baac50dad534`
- `javascript_module` `app.frontend.scripts.verify-production-deploy.test` — symbol `app.frontend.scripts.verify-production-deploy.test` — [source://app/frontend/scripts/verify-production-deploy.test.mjs#L1] — Provenance `prov:2f02da4778b41a30` via `javascript_regex` confidence `deterministic` hash `e66c87dee719`
- `javascript_module` `app.frontend.src.api.auth.test` — symbol `app.frontend.src.api.auth.test` — [source://app/frontend/src/api/auth.test.ts#L1] — Provenance `prov:ef4b023bb7d7820f` via `javascript_regex` confidence `deterministic` hash `fbef41a899c6`

Redacted source signal:

```text
import { describe, expect, it, vi } from 'vitest';

import { buildGoogleOAuthRedirectTo, getApiAuthorizationHeader, type SupabaseAuthClientLike } from './auth';

function supabaseClientWithToken([REDACTED] | null): SupabaseAuthClientLike {
  return {
    auth: {
      getSession: vi.fn(async () => (
```
- `javascript_module` `app.frontend.src.api.auth` — symbol `app.frontend.src.api.auth` — [source://app/frontend/src/api/auth.ts#L1] — Provenance `prov:bc9a9c52f62e90db` via `javascript_regex` confidence `deterministic` hash `0e8b8999c9e2`

Redacted source signal:

```text
import { createClient } from '@supabase/supabase-js';
import { resolveAuthMode, resolveSupabaseAnonKey, resolveSupabaseUrl } from './config';
import { getPublicBetaAuthorizationHeader } from './publicBetaAuth';

export interface SupabaseAuthClientLike {
  auth: {
    getSession: () => Promise<{ data
```
- `javascript_module` `app.frontend.src.api.betaRequest.test` — symbol `app.frontend.src.api.betaRequest.test` — [source://app/frontend/src/api/betaRequest.test.ts#L1] — Provenance `prov:da91686ec1e6502b` via `javascript_regex` confidence `deterministic` hash `f5213fdb9372`
- `javascript_module` `app.frontend.src.api.betaRequest` — symbol `app.frontend.src.api.betaRequest` — [source://app/frontend/src/api/betaRequest.ts#L1] — Provenance `prov:a2dcc314744c42a8` via `javascript_regex` confidence `deterministic` hash `d79cf845ef17`
- `javascript_module` `app.frontend.src.api.client` — symbol `app.frontend.src.api.client` — [source://app/frontend/src/api/client.ts#L1] — Provenance `prov:b6300a099cdd9dd5` via `javascript_regex` confidence `deterministic` hash `553e58ddff02`
- `javascript_module` `app.frontend.src.api.config.test` — symbol `app.frontend.src.api.config.test` — [source://app/frontend/src/api/config.test.ts#L1] — Provenance `prov:65144d4febf25c72` via `javascript_regex` confidence `deterministic` hash `9f06808271b2`
- `javascript_module` `app.frontend.src.api.config` — symbol `app.frontend.src.api.config` — [source://app/frontend/src/api/config.ts#L1] — Provenance `prov:e7d1d07cfc78a4ba` via `javascript_regex` confidence `deterministic` hash `9559378d31c4`
- `javascript_module` `app.frontend.src.api.publicBetaAuth.test` — symbol `app.frontend.src.api.publicBetaAuth.test` — [source://app/frontend/src/api/publicBetaAuth.test.ts#L1] — Provenance `prov:f614dc5bdf4687e0` via `javascript_regex` confidence `deterministic` hash `c2c34ffcea76`

Redacted source signal:

```text
import { describe, expect, it, vi } from 'vitest';

import { getPublicBetaAuthorizationHeader, type TokenStorage } from './publicBetaAuth';

function memoryStorage(initial: Record<string, string> = {}): TokenStorage {
  const values = new Map(Object.entries(initial));
  return {
    getItem: (key: s
```
- `javascript_module` `app.frontend.src.api.publicBetaAuth` — symbol `app.frontend.src.api.publicBetaAuth` — [source://app/frontend/src/api/publicBetaAuth.ts#L1] — Provenance `prov:2d6e6f7149eef780` via `javascript_regex` confidence `deterministic` hash `cb7c848e1c4b`

Redacted source signal:

```text
export const PUBLIC_BETA_TOKEN_STORAGE_KEY = 'cmmc_public_beta_token';

export type TokenStorage = Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>;

type Fetch[REDACTED] string) => Promise<string>;

interface PublicBetaAuthOptions {
  prod: boolean;
  apiBase: string;
  storage?: TokenStorage;
```
- `javascript_module` `app.frontend.src.components.AuthGate` — symbol `app.frontend.src.components.AuthGate` — [source://app/frontend/src/components/AuthGate.tsx#L1] — Provenance `prov:4cec088386c59776` via `javascript_regex` confidence `deterministic` hash `a8c74418470a`
- `javascript_module` `app.frontend.src.components.ChatPanel` — symbol `app.frontend.src.components.ChatPanel` — [source://app/frontend/src/components/ChatPanel.tsx#L1] — Provenance `prov:5eeaac9b98438918` via `javascript_regex` confidence `deterministic` hash `16c9b4cc8afd`
- `javascript_module` `app.frontend.src.components.EvidenceDrawer` — symbol `app.frontend.src.components.EvidenceDrawer` — [source://app/frontend/src/components/EvidenceDrawer.tsx#L1] — Provenance `prov:f5eed107cad71fc9` via `javascript_regex` confidence `deterministic` hash `9f0dcfb97225`
- `javascript_module` `app.frontend.src.components.FindingReviewPanel` — symbol `app.frontend.src.components.FindingReviewPanel` — [source://app/frontend/src/components/FindingReviewPanel.tsx#L1] — Provenance `prov:ef88733b31595c91` via `javascript_regex` confidence `deterministic` hash `e1ed62950bb5`
- `javascript_module` `app.frontend.src.components.ProgressSidebar` — symbol `app.frontend.src.components.ProgressSidebar` — [source://app/frontend/src/components/ProgressSidebar.tsx#L1] — Provenance `prov:9c0f18d2e826e570` via `javascript_regex` confidence `deterministic` hash `84ebf4bd70e1`
- `javascript_module` `app.frontend.src.components.RemediationDashboard` — symbol `app.frontend.src.components.RemediationDashboard` — [source://app/frontend/src/components/RemediationDashboard.tsx#L1] — Provenance `prov:dacadb8586edce63` via `javascript_regex` confidence `deterministic` hash `11fe48ade8b4`
- `javascript_module` `app.frontend.src.components.ReportPreview` — symbol `app.frontend.src.components.ReportPreview` — [source://app/frontend/src/components/ReportPreview.tsx#L1] — Provenance `prov:a69c2974d3de5a47` via `javascript_regex` confidence `deterministic` hash `e4d4c9b499d8`
- `javascript_module` `app.frontend.src.components.ScopePanel.test` — symbol `app.frontend.src.components.ScopePanel.test` — [source://app/frontend/src/components/ScopePanel.test.ts#L1] — Provenance `prov:d09f799d5bd61b62` via `javascript_regex` confidence `deterministic` hash `97d54c44ae8d`
- `javascript_module` `app.frontend.src.components.ScopePanel` — symbol `app.frontend.src.components.ScopePanel` — [source://app/frontend/src/components/ScopePanel.tsx#L1] — Provenance `prov:692175c97b95728b` via `javascript_regex` confidence `deterministic` hash `544643d58f7b`
- `javascript_module` `app.frontend.src.components.accessible-form-controls.test` — symbol `app.frontend.src.components.accessible-form-controls.test` — [source://app/frontend/src/components/accessible-form-controls.test.tsx#L1] — Provenance `prov:ed5143dbf80d2715` via `javascript_regex` confidence `deterministic` hash `916e8636f6b1`
- `javascript_module` `app.frontend.src.main` — symbol `app.frontend.src.main` — [source://app/frontend/src/main.tsx#L1] — Provenance `prov:c11d731ce192f355` via `javascript_regex` confidence `deterministic` hash `d907d5339aa1`
- `javascript_module` `app.frontend.src.pages.App.test` — symbol `app.frontend.src.pages.App.test` — [source://app/frontend/src/pages/App.test.ts#L1] — Provenance `prov:e841631ee57a7ea3` via `javascript_regex` confidence `deterministic` hash `386edbbe2d0a`
- `javascript_module` `app.frontend.src.pages.App` — symbol `app.frontend.src.pages.App` — [source://app/frontend/src/pages/App.tsx#L1] — Provenance `prov:33fe3900a676f6c9` via `javascript_regex` confidence `deterministic` hash `5afe17041c1e`
- `javascript_module` `app.frontend.src.pages.AssessmentApp` — symbol `app.frontend.src.pages.AssessmentApp` — [source://app/frontend/src/pages/AssessmentApp.tsx#L1] — Provenance `prov:82651a96ecdaf386` via `javascript_regex` confidence `deterministic` hash `b4093c13c7e7`
- `javascript_module` `app.frontend.src.types` — symbol `app.frontend.src.types` — [source://app/frontend/src/types/index.ts#L1] — Provenance `prov:334ff6a24dab372c` via `javascript_regex` confidence `deterministic` hash `5242fa64e679`
- `javascript_module` `app.frontend.src.vite-env.d` — symbol `app.frontend.src.vite-env.d` — [source://app/frontend/src/vite-env.d.ts#L1] — Provenance `prov:7e7d31dbfeeb12e0` via `javascript_regex` confidence `deterministic` hash `5641777f2204`
- `javascript_module` `app.frontend.vite.config` — symbol `app.frontend.vite.config` — [source://app/frontend/vite.config.ts#L1] — Provenance `prov:759c0b61f383e8d9` via `javascript_regex` confidence `deterministic` hash `ee6e02042635`

### markdown_section

- `markdown_section` `CMMC Level 1 Readiness Assistant - Agent Workflow` — symbol `AGENTS.md#CMMC Level 1 Readiness Assistant - Agent Workflow` — [source://AGENTS.md#L1] — Provenance `prov:89e60ba0223db3b0` via `markdown_parser` confidence `deterministic` hash `53a723759d3f`
- `markdown_section` `CMMC-Specific Quality Gates` — symbol `AGENTS.md#CMMC-Specific Quality Gates` — [source://AGENTS.md#L62] — Provenance `prov:c68833dc77005312` via `markdown_parser` confidence `deterministic` hash `53a723759d3f`
- `markdown_section` `Common Verification Commands` — symbol `AGENTS.md#Common Verification Commands` — [source://AGENTS.md#L78] — Provenance `prov:5f8a9c7362771b95` via `markdown_parser` confidence `deterministic` hash `53a723759d3f`
- `markdown_section` `Default Operating Mode` — symbol `AGENTS.md#Default Operating Mode` — [source://AGENTS.md#L5] — Provenance `prov:e9fdccc922577abb` via `markdown_parser` confidence `deterministic` hash `53a723759d3f`
- `markdown_section` `Handoff Standard` — symbol `AGENTS.md#Handoff Standard` — [source://AGENTS.md#L86] — Provenance `prov:78bbf08440b19cee` via `markdown_parser` confidence `deterministic` hash `53a723759d3f`
- `markdown_section` `Required Skills / Workflow` — symbol `AGENTS.md#Required Skills / Workflow` — [source://AGENTS.md#L15] — Provenance `prov:ebfdf9285fc4f2ed` via `markdown_parser` confidence `deterministic` hash `53a723759d3f`
- `markdown_section` `Architecture` — symbol `README.md#Architecture` — [source://README.md#L57] — Provenance `prov:11ccb644a5552792` via `markdown_parser` confidence `deterministic` hash `74de9a637a54`
- `markdown_section` `Backend` — symbol `README.md#Backend` — [source://README.md#L114] — Provenance `prov:c250df2b6935a6b8` via `markdown_parser` confidence `deterministic` hash `74de9a637a54`
- `markdown_section` `CMMC Level 1 Readiness Assistant` — symbol `README.md#CMMC Level 1 Readiness Assistant` — [source://README.md#L1] — Provenance `prov:5e013c21a2e4d0fe` via `markdown_parser` confidence `deterministic` hash `74de9a637a54`
- `markdown_section` `Configuration overview` — symbol `README.md#Configuration overview` — [source://README.md#L161] — Provenance `prov:479bc69e0f6788fd` via `markdown_parser` confidence `deterministic` hash `74de9a637a54`
- `markdown_section` `Contribution / agent workflow` — symbol `README.md#Contribution / agent workflow` — [source://README.md#L238] — Provenance `prov:0096e4ee3913d037` via `markdown_parser` confidence `deterministic` hash `74de9a637a54`
- `markdown_section` `Current status snapshot` — symbol `README.md#Current status snapshot` — [source://README.md#L19] — Provenance `prov:a66cc0b9d3dc425f` via `markdown_parser` confidence `deterministic` hash `74de9a637a54`
- `markdown_section` `Frontend` — symbol `README.md#Frontend` — [source://README.md#L133] — Provenance `prov:5dcbc91575e92361` via `markdown_parser` confidence `deterministic` hash `74de9a637a54`
- `markdown_section` `Full stack with Docker Compose` — symbol `README.md#Full stack with Docker Compose` — [source://README.md#L152] — Provenance `prov:3cc460c337167346` via `markdown_parser` confidence `deterministic` hash `74de9a637a54`
- `markdown_section` `Implemented / verified locally but not all landed or deployed` — symbol `README.md#Implemented / verified locally but not all landed or deployed` — [source://README.md#L35] — Provenance `prov:4f946e03fe3585c8` via `markdown_parser` confidence `deterministic` hash `74de9a637a54`
- `markdown_section` `Live / deployed` — symbol `README.md#Live / deployed` — [source://README.md#L25] — Provenance `prov:0a7d0e6fc87b64e6` via `markdown_parser` confidence `deterministic` hash `74de9a637a54`
- `markdown_section` `Local development` — symbol `README.md#Local development` — [source://README.md#L105] — Provenance `prov:935842ee7aceb58f` via `markdown_parser` confidence `deterministic` hash `74de9a637a54`
- `markdown_section` `Open product gates` — symbol `README.md#Open product gates` — [source://README.md#L47] — Provenance `prov:67751fa19b77b5cb` via `markdown_parser` confidence `deterministic` hash `74de9a637a54`
- `markdown_section` `Production deployment notes` — symbol `README.md#Production deployment notes` — [source://README.md#L212] — Provenance `prov:bfa496cb4c8e8629` via `markdown_parser` confidence `deterministic` hash `74de9a637a54`
- `markdown_section` `Repository layout` — symbol `README.md#Repository layout` — [source://README.md#L82] — Provenance `prov:c4eb3b6aa2a70137` via `markdown_parser` confidence `deterministic` hash `74de9a637a54`
- `markdown_section` `Safety and compliance boundaries` — symbol `README.md#Safety and compliance boundaries` — [source://README.md#L7] — Provenance `prov:17d795f24f6b10a9` via `markdown_parser` confidence `deterministic` hash `74de9a637a54`
- `markdown_section` `Verification commands` — symbol `README.md#Verification commands` — [source://README.md#L185] — Provenance `prov:3340f6ffce502788` via `markdown_parser` confidence `deterministic` hash `74de9a637a54`
- `markdown_section` `Architecture` — symbol `app/README.md#Architecture` — [source://app/README.md#L7] — Provenance `prov:ae8110abd8ec9820` via `markdown_parser` confidence `deterministic` hash `c2bd322911b5`

Redacted source signal:

```text
# CMMC Level 1 Self-Assessment Readiness Assistant

MVP web application for small DoD contractors preparing a CMMC Level 1 self-assessment readiness package for Federal Contract Information.

This is a readiness and self-assessment support tool. It does not certify the customer, does not submit to S
```
- `markdown_section` `Authentication boundary` — symbol `app/README.md#Authentication boundary` — [source://app/README.md#L173] — Provenance `prov:dcad4611db3d9640` via `markdown_parser` confidence `deterministic` hash `c2bd322911b5`

Redacted source signal:

```text
# CMMC Level 1 Self-Assessment Readiness Assistant

MVP web application for small DoD contractors preparing a CMMC Level 1 self-assessment readiness package for Federal Contract Information.

This is a readiness and self-assessment support tool. It does not certify the customer, does not submit to S
```
- `markdown_section` `CMMC Level 1 Self-Assessment Readiness Assistant` — symbol `app/README.md#CMMC Level 1 Self-Assessment Readiness Assistant` — [source://app/README.md#L1] — Provenance `prov:79797db9ca8d2a6b` via `markdown_parser` confidence `deterministic` hash `c2bd322911b5`

Redacted source signal:

```text
# CMMC Level 1 Self-Assessment Readiness Assistant

MVP web application for small DoD contractors preparing a CMMC Level 1 self-assessment readiness package for Federal Contract Information.

This is a readiness and self-assessment support tool. It does not certify the customer, does not submit to S
```
- `markdown_section` `Database setup and migrations` — symbol `app/README.md#Database setup and migrations` — [source://app/README.md#L85] — Provenance `prov:6eaf4ec58a2f9b19` via `markdown_parser` confidence `deterministic` hash `c2bd322911b5`

Redacted source signal:

```text
# CMMC Level 1 Self-Assessment Readiness Assistant

MVP web application for small DoD contractors preparing a CMMC Level 1 self-assessment readiness package for Federal Contract Information.

This is a readiness and self-assessment support tool. It does not certify the customer, does not submit to S
```
- `markdown_section` `Implemented API routes` — symbol `app/README.md#Implemented API routes` — [source://app/README.md#L141] — Provenance `prov:e1380122456f6ad2` via `markdown_parser` confidence `deterministic` hash `c2bd322911b5`

Redacted source signal:

```text
# CMMC Level 1 Self-Assessment Readiness Assistant

MVP web application for small DoD contractors preparing a CMMC Level 1 self-assessment readiness package for Federal Contract Information.

This is a readiness and self-assessment support tool. It does not certify the customer, does not submit to S
```
- `markdown_section` `LLM configuration` — symbol `app/README.md#LLM configuration` — [source://app/README.md#L106] — Provenance `prov:54373153445e6d1a` via `markdown_parser` confidence `deterministic` hash `c2bd322911b5`

Redacted source signal:

```text
# CMMC Level 1 Self-Assessment Readiness Assistant

MVP web application for small DoD contractors preparing a CMMC Level 1 self-assessment readiness package for Federal Contract Information.

This is a readiness and self-assessment support tool. It does not certify the customer, does not submit to S
```
- `markdown_section` `Local backend tests` — symbol `app/README.md#Local backend tests` — [source://app/README.md#L77] — Provenance `prov:03217518689afcaf` via `markdown_parser` confidence `deterministic` hash `c2bd322911b5`

Redacted source signal:

```text
# CMMC Level 1 Self-Assessment Readiness Assistant

MVP web application for small DoD contractors preparing a CMMC Level 1 self-assessment readiness package for Federal Contract Information.

This is a readiness and self-assessment support tool. It does not certify the customer, does not submit to S
```
- `markdown_section` `Local development with Docker` — symbol `app/README.md#Local development with Docker` — [source://app/README.md#L58] — Provenance `prov:3ad505713337da91` via `markdown_parser` confidence `deterministic` hash `c2bd322911b5`

Redacted source signal:

```text
# CMMC Level 1 Self-Assessment Readiness Assistant

MVP web application for small DoD contractors preparing a CMMC Level 1 self-assessment readiness package for Federal Contract Information.

This is a readiness and self-assessment support tool. It does not certify the customer, does not submit to S
```
- `markdown_section` `Local frontend development` — symbol `app/README.md#Local frontend development` — [source://app/README.md#L96] — Provenance `prov:ef1447711fe03a88` via `markdown_parser` confidence `deterministic` hash `c2bd322911b5`

Redacted source signal:

```text
# CMMC Level 1 Self-Assessment Readiness Assistant

MVP web application for small DoD contractors preparing a CMMC Level 1 self-assessment readiness package for Federal Contract Information.

This is a readiness and self-assessment support tool. It does not certify the customer, does not submit to S
```
- `markdown_section` `Project layout` — symbol `app/README.md#Project layout` — [source://app/README.md#L18] — Provenance `prov:195033054a9aa06a` via `markdown_parser` confidence `deterministic` hash `c2bd322911b5`

Redacted source signal:

```text
# CMMC Level 1 Self-Assessment Readiness Assistant

MVP web application for small DoD contractors preparing a CMMC Level 1 self-assessment readiness package for Federal Contract Information.

This is a readiness and self-assessment support tool. It does not certify the customer, does not submit to S
```
- `markdown_section` `Report language constraints` — symbol `app/README.md#Report language constraints` — [source://app/README.md#L179] — Provenance `prov:6eea9268511f313e` via `markdown_parser` confidence `deterministic` hash `c2bd322911b5`

Redacted source signal:

```text
# CMMC Level 1 Self-Assessment Readiness Assistant

MVP web application for small DoD contractors preparing a CMMC Level 1 self-assessment readiness package for Federal Contract Information.

This is a readiness and self-assessment support tool. It does not certify the customer, does not submit to S
```
- `markdown_section` `Security notes` — symbol `app/README.md#Security notes` — [source://app/README.md#L158] — Provenance `prov:9c3dc6a7adc6b797` via `markdown_parser` confidence `deterministic` hash `c2bd322911b5`

Redacted source signal:

```text
# CMMC Level 1 Self-Assessment Readiness Assistant

MVP web application for small DoD contractors preparing a CMMC Level 1 self-assessment readiness package for Federal Contract Information.

This is a readiness and self-assessment support tool. It does not certify the customer, does not submit to S
```
- `markdown_section` `Workflow controls` — symbol `app/README.md#Workflow controls` — [source://app/README.md#L128] — Provenance `prov:17753a8832152bb2` via `markdown_parser` confidence `deterministic` hash `c2bd322911b5`

Redacted source signal:

```text
# CMMC Level 1 Self-Assessment Readiness Assistant

MVP web application for small DoD contractors preparing a CMMC Level 1 self-assessment readiness package for Federal Contract Information.

This is a readiness and self-assessment support tool. It does not certify the customer, does not submit to S
```
- `markdown_section` `Backend hosting requirements` — symbol `docs/operations/cloudflare-deployment.md#Backend hosting requirements` — [source://docs/operations/cloudflare-deployment.md#L73] — Provenance `prov:5779d792ae942003` via `markdown_parser` confidence `deterministic` hash `f9e9366684cc`
- `markdown_section` `CORS and preview policy` — symbol `docs/operations/cloudflare-deployment.md#CORS and preview policy` — [source://docs/operations/cloudflare-deployment.md#L107] — Provenance `prov:cba8810876fdc47d` via `markdown_parser` confidence `deterministic` hash `f9e9366684cc`
- `markdown_section` `Cloudflare API proxy/TLS requirements` — symbol `docs/operations/cloudflare-deployment.md#Cloudflare API proxy/TLS requirements` — [source://docs/operations/cloudflare-deployment.md#L96] — Provenance `prov:92a902d6b57c3b51` via `markdown_parser` confidence `deterministic` hash `f9e9366684cc`
- `markdown_section` `Cloudflare Deployment Runbook` — symbol `docs/operations/cloudflare-deployment.md#Cloudflare Deployment Runbook` — [source://docs/operations/cloudflare-deployment.md#L1] — Provenance `prov:1cfa5289319d10f1` via `markdown_parser` confidence `deterministic` hash `f9e9366684cc`
- `markdown_section` `Current accidental Cloudflare Pages project` — symbol `docs/operations/cloudflare-deployment.md#Current accidental Cloudflare Pages project` — [source://docs/operations/cloudflare-deployment.md#L17] — Provenance `prov:28fd68d2ffe19f62` via `markdown_parser` confidence `deterministic` hash `f9e9366684cc`
- `markdown_section` `Database migrations` — symbol `docs/operations/cloudflare-deployment.md#Database migrations` — [source://docs/operations/cloudflare-deployment.md#L125] — Provenance `prov:290268480c886549` via `markdown_parser` confidence `deterministic` hash `f9e9366684cc`
- `markdown_section` `Deployment blockers remaining` — symbol `docs/operations/cloudflare-deployment.md#Deployment blockers remaining` — [source://docs/operations/cloudflare-deployment.md#L179] — Provenance `prov:8f2b7dedce55e08a` via `markdown_parser` confidence `deterministic` hash `f9e9366684cc`
- `markdown_section` `Frontend Pages configuration` — symbol `docs/operations/cloudflare-deployment.md#Frontend Pages configuration` — [source://docs/operations/cloudflare-deployment.md#L34] — Provenance `prov:271f3e9df9bde4e3` via `markdown_parser` confidence `deterministic` hash `f9e9366684cc`
- `markdown_section` `Recommended architecture` — symbol `docs/operations/cloudflare-deployment.md#Recommended architecture` — [source://docs/operations/cloudflare-deployment.md#L5] — Provenance `prov:f109e9f22f5c540f` via `markdown_parser` confidence `deterministic` hash `f9e9366684cc`
- `markdown_section` `Required smoke tests before announcing any deployment` — symbol `docs/operations/cloudflare-deployment.md#Required smoke tests before announcing any deployment` — [source://docs/operations/cloudflare-deployment.md#L144] — Provenance `prov:167b03c725d5f024` via `markdown_parser` confidence `deterministic` hash `f9e9366684cc`
- `markdown_section` `Rollback guidance` — symbol `docs/operations/cloudflare-deployment.md#Rollback guidance` — [source://docs/operations/cloudflare-deployment.md#L161] — Provenance `prov:94a8124604934a8d` via `markdown_parser` confidence `deterministic` hash `f9e9366684cc`
- `markdown_section` `Database Migrations` — symbol `docs/operations/database-migrations.md#Database Migrations` — [source://docs/operations/database-migrations.md#L1] — Provenance `prov:19a61c0cea5887a5` via `markdown_parser` confidence `deterministic` hash `5d042c16dcc1`
- `markdown_section` `Docker/Postgres development` — symbol `docs/operations/database-migrations.md#Docker/Postgres development` — [source://docs/operations/database-migrations.md#L16] — Provenance `prov:778084d57d771729` via `markdown_parser` confidence `deterministic` hash `5d042c16dcc1`
- `markdown_section` `Downgrade caveats` — symbol `docs/operations/database-migrations.md#Downgrade caveats` — [source://docs/operations/database-migrations.md#L99] — Provenance `prov:865f4bdc810ec548` via `markdown_parser` confidence `deterministic` hash `5d042c16dcc1`
- `markdown_section` `Generate a migration after model changes` — symbol `docs/operations/database-migrations.md#Generate a migration after model changes` — [source://docs/operations/database-migrations.md#L89] — Provenance `prov:880d71aa38eab828` via `markdown_parser` confidence `deterministic` hash `5d042c16dcc1`
- `markdown_section` `Inspect current migration version` — symbol `docs/operations/database-migrations.md#Inspect current migration version` — [source://docs/operations/database-migrations.md#L80] — Provenance `prov:c3c61c9918f7c504` via `markdown_parser` confidence `deterministic` hash `5d042c16dcc1`
- `markdown_section` `Local SQLite development` — symbol `docs/operations/database-migrations.md#Local SQLite development` — [source://docs/operations/database-migrations.md#L5] — Provenance `prov:4cb1843723ab259c` via `markdown_parser` confidence `deterministic` hash `5d042c16dcc1`
- `markdown_section` `Production requirements` — symbol `docs/operations/database-migrations.md#Production requirements` — [source://docs/operations/database-migrations.md#L61] — Provenance `prov:ad673a807e0ffae8` via `markdown_parser` confidence `deterministic` hash `5d042c16dcc1`
- `markdown_section` `Stale local volume recovery` — symbol `docs/operations/database-migrations.md#Stale local volume recovery` — [source://docs/operations/database-migrations.md#L35] — Provenance `prov:be4ee7c807dba445` via `markdown_parser` confidence `deterministic` hash `5d042c16dcc1`
- `markdown_section` `Upgrade to the latest migration` — symbol `docs/operations/database-migrations.md#Upgrade to the latest migration` — [source://docs/operations/database-migrations.md#L73] — Provenance `prov:afdc38acd9e66421` via `markdown_parser` confidence `deterministic` hash `5d042c16dcc1`
- `markdown_section` `Commands for ongoing verification` — symbol `docs/operations/maintenance-plan.md#Commands for ongoing verification` — [source://docs/operations/maintenance-plan.md#L90] — Provenance `prov:906e7445e089944a` via `markdown_parser` confidence `deterministic` hash `a4e93bbdf226`
- `markdown_section` `Cron job policy` — symbol `docs/operations/maintenance-plan.md#Cron job policy` — [source://docs/operations/maintenance-plan.md#L86] — Provenance `prov:e35077af433acf08` via `markdown_parser` confidence `deterministic` hash `a4e93bbdf226`
- `markdown_section` `Current verdict` — symbol `docs/operations/maintenance-plan.md#Current verdict` — [source://docs/operations/maintenance-plan.md#L6] — Provenance `prov:ee9a448b8cdd3e39` via `markdown_parser` confidence `deterministic` hash `a4e93bbdf226`
- `markdown_section` `Maintenance and Housekeeping Plan` — symbol `docs/operations/maintenance-plan.md#Maintenance and Housekeeping Plan` — [source://docs/operations/maintenance-plan.md#L1] — Provenance `prov:df71429255a18acb` via `markdown_parser` confidence `deterministic` hash `a4e93bbdf226`
- `markdown_section` `P0: Make the dirty tree reviewable` — symbol `docs/operations/maintenance-plan.md#P0: Make the dirty tree reviewable` — [source://docs/operations/maintenance-plan.md#L19] — Provenance `prov:f438ae8ed2f1211d` via `markdown_parser` confidence `deterministic` hash `a4e93bbdf226`
- `markdown_section` `P1: Close release-blocking production-readiness gaps` — symbol `docs/operations/maintenance-plan.md#P1: Close release-blocking production-readiness gaps` — [source://docs/operations/maintenance-plan.md#L37] — Provenance `prov:9f2abb54c26a01e8` via `markdown_parser` confidence `deterministic` hash `a4e93bbdf226`
- `markdown_section` `P2: Pre-merge release gates` — symbol `docs/operations/maintenance-plan.md#P2: Pre-merge release gates` — [source://docs/operations/maintenance-plan.md#L68] — Provenance `prov:6cd7c3bb19334d53` via `markdown_parser` confidence `deterministic` hash `a4e93bbdf226`
- `markdown_section` `P3: Follow-up maintenance` — symbol `docs/operations/maintenance-plan.md#P3: Follow-up maintenance` — [source://docs/operations/maintenance-plan.md#L80] — Provenance `prov:cf4cd25d4963c128` via `markdown_parser` confidence `deterministic` hash `a4e93bbdf226`
- `markdown_section` `Priority key` — symbol `docs/operations/maintenance-plan.md#Priority key` — [source://docs/operations/maintenance-plan.md#L12] — Provenance `prov:f155c3f42c74264e` via `markdown_parser` confidence `deterministic` hash `a4e93bbdf226`
- `markdown_section` `Docker Compose healthcheck note` — symbol `docs/operations/operational-readiness.md#Docker Compose healthcheck note` — [source://docs/operations/operational-readiness.md#L9] — Provenance `prov:68ec8e405741ae0e` via `markdown_parser` confidence `deterministic` hash `fbbd3a872841`
- `markdown_section` `Operational Readiness Checks` — symbol `docs/operations/operational-readiness.md#Operational Readiness Checks` — [source://docs/operations/operational-readiness.md#L1] — Provenance `prov:39fad8fee6ce9ba7` via `markdown_parser` confidence `deterministic` hash `fbbd3a872841`
- `markdown_section` `Executive Summary` — symbol `docs/opus-red-team-report-2026-04-29.md#Executive Summary` — [source://docs/opus-red-team-report-2026-04-29.md#L3] — Provenance `prov:d403f0f114c79c4f` via `markdown_parser` confidence `deterministic` hash `68a92746a497`
- `markdown_section` `Findings` — symbol `docs/opus-red-team-report-2026-04-29.md#Findings` — [source://docs/opus-red-team-report-2026-04-29.md#L29] — Provenance `prov:0b312cf9306a25f4` via `markdown_parser` confidence `deterministic` hash `68a92746a497`
- `markdown_section` `Positive Findings` — symbol `docs/opus-red-team-report-2026-04-29.md#Positive Findings` — [source://docs/opus-red-team-report-2026-04-29.md#L33] — Provenance `prov:4080a8151e91a4da` via `markdown_parser` confidence `deterministic` hash `68a92746a497`
- `markdown_section` `Recommended Fix Priority` — symbol `docs/opus-red-team-report-2026-04-29.md#Recommended Fix Priority` — [source://docs/opus-red-team-report-2026-04-29.md#L43] — Provenance `prov:b227367da11ff6b2` via `markdown_parser` confidence `deterministic` hash `68a92746a497`
- `markdown_section` `Red-Team Report` — symbol `docs/opus-red-team-report-2026-04-29.md#Red-Team Report` — [source://docs/opus-red-team-report-2026-04-29.md#L1] — Provenance `prov:917e0105bf35a5ee` via `markdown_parser` confidence `deterministic` hash `68a92746a497`
- `markdown_section` `Top Findings Table` — symbol `docs/opus-red-team-report-2026-04-29.md#Top Findings Table` — [source://docs/opus-red-team-report-2026-04-29.md#L7] — Provenance `prov:c5dc47a874b08994` via `markdown_parser` confidence `deterministic` hash `68a92746a497`
- `markdown_section` `CMMC Level 1 Readiness Assistant MVP Implementation Plan` — symbol `docs/plans/2026-04-28-cmmc-level1-readiness-assistant.md#CMMC Level 1 Readiness Assistant MVP Implementation Plan` — [source://docs/plans/2026-04-28-cmmc-level1-readiness-assistant.md#L1] — Provenance `prov:daa1fa18d0d50ddf` via `markdown_parser` confidence `deterministic` hash `c8c02099816a`
- `markdown_section` `CMMC Level 1 Readiness Assistant Next-Level Fix Plan` — symbol `docs/plans/2026-04-29-next-level-ux-and-assessment-fixes.md#CMMC Level 1 Readiness Assistant Next-Level Fix Plan` — [source://docs/plans/2026-04-29-next-level-ux-and-assessment-fixes.md#L1] — Provenance `prov:8769b10e3f09be97` via `markdown_parser` confidence `deterministic` hash `2c32a219019e`

Redacted source signal:

```text
# CMMC Level 1 Readiness Assistant Next-Level Fix Plan

> For Hermes: Use subagent-driven-development skill to implement this plan ta[REDACTED] after user approval.

Goal: Fix the usability and assessment-quality issues found during persona testing so a non-IT operations manager can complete, resume
```
- `markdown_section` `Final Verification Commands` — symbol `docs/plans/2026-04-29-next-level-ux-and-assessment-fixes.md#Final Verification Commands` — [source://docs/plans/2026-04-29-next-level-ux-and-assessment-fixes.md#L369] — Provenance `prov:3cc3ba9689158207` via `markdown_parser` confidence `deterministic` hash `2c32a219019e`

Redacted source signal:

```text
# CMMC Level 1 Readiness Assistant Next-Level Fix Plan

> For Hermes: Use subagent-driven-development skill to implement this plan ta[REDACTED] after user approval.

Goal: Fix the usability and assessment-quality issues found during persona testing so a non-IT operations manager can complete, resume
```
- `markdown_section` `Priority Order` — symbol `docs/plans/2026-04-29-next-level-ux-and-assessment-fixes.md#Priority Order` — [source://docs/plans/2026-04-29-next-level-ux-and-assessment-fixes.md#L351] — Provenance `prov:acc4537ddf2d1794` via `markdown_parser` confidence `deterministic` hash `2c32a219019e`

Redacted source signal:

```text
# CMMC Level 1 Readiness Assistant Next-Level Fix Plan

> For Hermes: Use subagent-driven-development skill to implement this plan ta[REDACTED] after user approval.

Goal: Fix the usability and assessment-quality issues found during persona testing so a non-IT operations manager can complete, resume
```
- `markdown_section` `Task 10: Add automated browser/e2e smoke test option` — symbol `docs/plans/2026-04-29-next-level-ux-and-assessment-fixes.md#Task 10: Add automated browser/e2e smoke test option` — [source://docs/plans/2026-04-29-next-level-ux-and-assessment-fixes.md#L333] — Provenance `prov:fdf22115c4c5e968` via `markdown_parser` confidence `deterministic` hash `2c32a219019e`

Redacted source signal:

```text
# CMMC Level 1 Readiness Assistant Next-Level Fix Plan

> For Hermes: Use subagent-driven-development skill to implement this plan ta[REDACTED] after user approval.

Goal: Fix the usability and assessment-quality issues found during persona testing so a non-IT operations manager can complete, resume
```
- `markdown_section` `Task 1: Add regression tests for reported assessment-quality bugs` — symbol `docs/plans/2026-04-29-next-level-ux-and-assessment-fixes.md#Task 1: Add regression tests for reported assessment-quality bugs` — [source://docs/plans/2026-04-29-next-level-ux-and-assessment-fixes.md#L36] — Provenance `prov:2e5f648647e291c1` via `markdown_parser` confidence `deterministic` hash `2c32a219019e`

Redacted source signal:

```text
# CMMC Level 1 Readiness Assistant Next-Level Fix Plan

> For Hermes: Use subagent-driven-development skill to implement this plan ta[REDACTED] after user approval.

Goal: Fix the usability and assessment-quality issues found during persona testing so a non-IT operations manager can complete, resume
```
- `markdown_section` `Task 2: Improve deterministic stub evaluator and evidence extraction` — symbol `docs/plans/2026-04-29-next-level-ux-and-assessment-fixes.md#Task 2: Improve deterministic stub evaluator and evidence extraction` — [source://docs/plans/2026-04-29-next-level-ux-and-assessment-fixes.md#L76] — Provenance `prov:0abb383db1fab0d0` via `markdown_parser` confidence `deterministic` hash `2c32a219019e`

Redacted source signal:

```text
# CMMC Level 1 Readiness Assistant Next-Level Fix Plan

> For Hermes: Use subagent-driven-development skill to implement this plan ta[REDACTED] after user approval.

Goal: Fix the usability and assessment-quality issues found during persona testing so a non-IT operations manager can complete, resume
```
- `markdown_section` `Task 3: Add chat intent parsing for finding review confirmation and revision` — symbol `docs/plans/2026-04-29-next-level-ux-and-assessment-fixes.md#Task 3: Add chat intent parsing for finding review confirmation and revision` — [source://docs/plans/2026-04-29-next-level-ux-and-assessment-fixes.md#L108] — Provenance `prov:f4ee4a86c5079e8b` via `markdown_parser` confidence `deterministic` hash `2c32a219019e`

Redacted source signal:

```text
# CMMC Level 1 Readiness Assistant Next-Level Fix Plan

> For Hermes: Use subagent-driven-development skill to implement this plan ta[REDACTED] after user approval.

Goal: Fix the usability and assessment-quality issues found during persona testing so a non-IT operations manager can complete, resume
```

### project

- `project` `cmmc-level1-readiness-assistant` — [source://project] — Provenance `prov:project:b39b000254b798e5` via `git` confidence `deterministic` hash `b39b000254b7`

### python_class

- `python_class` `AssistantResponse` — symbol `app.backend.src.assessment.schemas.AssistantResponse` — [source://app/backend/src/assessment/schemas.py#L209] — Provenance `prov:64194fadd85c2ef0` via `python_ast` confidence `deterministic` hash `711cffe52aae`

Redacted source signal:

```text
from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Annotated, Literal
from urllib.parse import parse_qsl, urlsplit
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator, model_validator


SENSITIVE_EXTERNAL_REFERENCE_QUERY_K
```
- `python_class` `ConfirmFindingRequest` — symbol `app.backend.src.assessment.schemas.ConfirmFindingRequest` — [source://app/backend/src/assessment/schemas.py#L174] — Provenance `prov:4098a4c97fc3b1f2` via `python_ast` confidence `deterministic` hash `711cffe52aae`

Redacted source signal:

```text
from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Annotated, Literal
from urllib.parse import parse_qsl, urlsplit
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator, model_validator


SENSITIVE_EXTERNAL_REFERENCE_QUERY_K
```
- `python_class` `ControlFindingInput` — symbol `app.backend.src.assessment.schemas.ControlFindingInput` — [source://app/backend/src/assessment/schemas.py#L93] — Provenance `prov:17ff714b33b865a6` via `python_ast` confidence `deterministic` hash `711cffe52aae`

Redacted source signal:

```text
from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Annotated, Literal
from urllib.parse import parse_qsl, urlsplit
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator, model_validator


SENSITIVE_EXTERNAL_REFERENCE_QUERY_K
```
- `python_class` `EvidenceCreate` — symbol `app.backend.src.assessment.schemas.EvidenceCreate` — [source://app/backend/src/assessment/schemas.py#L116] — Provenance `prov:ee6440965a2a4a6d` via `python_ast` confidence `deterministic` hash `711cffe52aae`

Redacted source signal:

```text
from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Annotated, Literal
from urllib.parse import parse_qsl, urlsplit
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator, model_validator


SENSITIVE_EXTERNAL_REFERENCE_QUERY_K
```
- `python_class` `FindingStatus` — symbol `app.backend.src.assessment.schemas.FindingStatus` — [source://app/backend/src/assessment/schemas.py#L72] — Provenance `prov:bba59a7f1febf51b` via `python_ast` confidence `deterministic` hash `711cffe52aae`

Redacted source signal:

```text
from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Annotated, Literal
from urllib.parse import parse_qsl, urlsplit
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator, model_validator


SENSITIVE_EXTERNAL_REFERENCE_QUERY_K
```
- `python_class` `LLMAnswerEvaluation` — symbol `app.backend.src.assessment.schemas.LLMAnswerEvaluation` — [source://app/backend/src/assessment/schemas.py#L79] — Provenance `prov:5edee65f768845cd` via `python_ast` confidence `deterministic` hash `711cffe52aae`

Redacted source signal:

```text
from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Annotated, Literal
from urllib.parse import parse_qsl, urlsplit
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator, model_validator


SENSITIVE_EXTERNAL_REFERENCE_QUERY_K
```
- `python_class` `MessageIn` — symbol `app.backend.src.assessment.schemas.MessageIn` — [source://app/backend/src/assessment/schemas.py#L167] — Provenance `prov:c8fd6c72d7fc935c` via `python_ast` confidence `deterministic` hash `711cffe52aae`

Redacted source signal:

```text
from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Annotated, Literal
from urllib.parse import parse_qsl, urlsplit
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator, model_validator


SENSITIVE_EXTERNAL_REFERENCE_QUERY_K
```
- `python_class` `Phase` — symbol `app.backend.src.assessment.schemas.Phase` — [source://app/backend/src/assessment/schemas.py#L55] — Provenance `prov:ae57f10e8cc99f24` via `python_ast` confidence `deterministic` hash `711cffe52aae`

Redacted source signal:

```text
from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Annotated, Literal
from urllib.parse import parse_qsl, urlsplit
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator, model_validator


SENSITIVE_EXTERNAL_REFERENCE_QUERY_K
```
- `python_class` `ScopePatch` — symbol `app.backend.src.assessment.schemas.ScopePatch` — [source://app/backend/src/assessment/schemas.py#L202] — Provenance `prov:c2d0b70795846614` via `python_ast` confidence `deterministic` hash `711cffe52aae`

Redacted source signal:

```text
from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Annotated, Literal
from urllib.parse import parse_qsl, urlsplit
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator, model_validator


SENSITIVE_EXTERNAL_REFERENCE_QUERY_K
```
- `python_class` `ScopePatchBody` — symbol `app.backend.src.assessment.schemas.ScopePatchBody` — [source://app/backend/src/assessment/schemas.py#L182] — Provenance `prov:9909ad3b7427121c` via `python_ast` confidence `deterministic` hash `711cffe52aae`

Redacted source signal:

```text
from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Annotated, Literal
from urllib.parse import parse_qsl, urlsplit
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator, model_validator


SENSITIVE_EXTERNAL_REFERENCE_QUERY_K
```
- `python_class` `SessionCreate` — symbol `app.backend.src.assessment.schemas.SessionCreate` — [source://app/backend/src/assessment/schemas.py#L163] — Provenance `prov:49a9c70fe18b1ef5` via `python_ast` confidence `deterministic` hash `711cffe52aae`

Redacted source signal:

```text
from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Annotated, Literal
from urllib.parse import parse_qsl, urlsplit
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator, model_validator


SENSITIVE_EXTERNAL_REFERENCE_QUERY_K
```
- `python_class` `AuthContext` — symbol `app.backend.src.auth.dependencies.AuthContext` — [source://app/backend/src/auth/dependencies.py#L13] — Provenance `prov:d23f22ea15f84ebd` via `python_ast` confidence `deterministic` hash `d5edc52e827b`

Redacted source signal:

```text
from dataclasses import dataclass
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from config.settings import get_settings
from database.base import get_db
from database.models import AuthAccessGrant, Organization, User, AssessmentSession, now_utc
from audit.ev
```
- `python_class` `PublicBetaClaims` — symbol `app.backend.src.auth.public_beta.PublicBetaClaims` — [source://app/backend/src/auth/public_beta.py#L13] — Provenance `prov:63323d9764b6837a` via `python_ast` confidence `deterministic` hash `77b86338d3da`

Redacted source signal:

```text
import base64
import hashlib
import hmac
import json
from dataclasses import dataclass


class PublicBetaTokenError(ValueError):
    pass


@dataclass(frozen=True)
class PublicBetaClaims:
    organization_id: str
    user_id: str
    email: str
    organization_name: str


def _b64encode(raw: bytes)
```
- `python_class` `PublicBetaTokenError` — symbol `app.backend.src.auth.public_beta.PublicBetaTokenError` — [source://app/backend/src/auth/public_beta.py#L8] — Provenance `prov:968f2ca5a7718393` via `python_ast` confidence `deterministic` hash `77b86338d3da`

Redacted source signal:

```text
import base64
import hashlib
import hmac
import json
from dataclasses import dataclass


class PublicBetaTokenError(ValueError):
    pass


@dataclass(frozen=True)
class PublicBetaClaims:
    organization_id: str
    user_id: str
    email: str
    organization_name: str


def _b64encode(raw: bytes)
```
- `python_class` `SupabaseClaims` — symbol `app.backend.src.auth.supabase.SupabaseClaims` — [source://app/backend/src/auth/supabase.py#L16] — Provenance `prov:964940a050e4fa01` via `python_ast` confidence `deterministic` hash `e5b0506670d2`

Redacted source signal:

```text
from dataclasses import dataclass
from functools import lru_cache
from ipaddress import ip_address
from socket import inet_aton
from urllib.parse import urlparse

import jwt
from jwt import PyJWKClient, PyJWTError


class SupabaseTokenError(ValueError):
    pass


@dataclass(frozen=True)
class Supab
```
- `python_class` `SupabaseTokenError` — symbol `app.backend.src.auth.supabase.SupabaseTokenError` — [source://app/backend/src/auth/supabase.py#L11] — Provenance `prov:07532ee7f00dacfb` via `python_ast` confidence `deterministic` hash `e5b0506670d2`

Redacted source signal:

```text
from dataclasses import dataclass
from functools import lru_cache
from ipaddress import ip_address
from socket import inet_aton
from urllib.parse import urlparse

import jwt
from jwt import PyJWKClient, PyJWTError


class SupabaseTokenError(ValueError):
    pass


@dataclass(frozen=True)
class Supab
```
- `python_class` `ConfigurationError` — symbol `app.backend.src.config.settings.ConfigurationError` — [source://app/backend/src/config/settings.py#L9] — Provenance `prov:cd4cb31798052f10` via `python_ast` confidence `deterministic` hash `a7f19740b398`

Redacted source signal:

```text
from functools import lru_cache
from ipaddress import ip_address
from socket import inet_aton
from urllib.parse import urlparse

from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigurationError(RuntimeError):
    pass


class Settings(BaseSettings):
    app_name: str = "CMMC
```
- `python_class` `Settings` — symbol `app.backend.src.config.settings.Settings` — [source://app/backend/src/config/settings.py#L13] — Provenance `prov:742e79454839969f` via `python_ast` confidence `deterministic` hash `a7f19740b398`

Redacted source signal:

```text
from functools import lru_cache
from ipaddress import ip_address
from socket import inet_aton
from urllib.parse import urlparse

from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigurationError(RuntimeError):
    pass


class Settings(BaseSettings):
    app_name: str = "CMMC
```
- `python_class` `Control` — symbol `app.backend.src.controls.library.Control` — [source://app/backend/src/controls/library.py#L8] — Provenance `prov:1b70be23bb52290e` via `python_ast` confidence `deterministic` hash `611f90f5e7eb`
- `python_class` `Base` — symbol `app.backend.src.database.base.Base` — [source://app/backend/src/database/base.py#L7] — Provenance `prov:0f70b9228e75418a` via `python_ast` confidence `deterministic` hash `17ab4e8d2bd7`
- `python_class` `AssessmentMessage` — symbol `app.backend.src.database.models.AssessmentMessage` — [source://app/backend/src/database/models.py#L75] — Provenance `prov:54c44fcc8f9106bc` via `python_ast` confidence `deterministic` hash `fcb520456941`
- `python_class` `AssessmentScope` — symbol `app.backend.src.database.models.AssessmentScope` — [source://app/backend/src/database/models.py#L85] — Provenance `prov:7e96442599fe7606` via `python_ast` confidence `deterministic` hash `fcb520456941`
- `python_class` `AssessmentSession` — symbol `app.backend.src.database.models.AssessmentSession` — [source://app/backend/src/database/models.py#L54] — Provenance `prov:eb06f7fb623e350f` via `python_ast` confidence `deterministic` hash `fcb520456941`
- `python_class` `AuditEvent` — symbol `app.backend.src.database.models.AuditEvent` — [source://app/backend/src/database/models.py#L148] — Provenance `prov:86ff0c612783e1c3` via `python_ast` confidence `deterministic` hash `fcb520456941`
- `python_class` `AuthAccessGrant` — symbol `app.backend.src.database.models.AuthAccessGrant` — [source://app/backend/src/database/models.py#L32] — Provenance `prov:c427af705d0bc170` via `python_ast` confidence `deterministic` hash `fcb520456941`
- `python_class` `ControlFinding` — symbol `app.backend.src.database.models.ControlFinding` — [source://app/backend/src/database/models.py#L94] — Provenance `prov:01e22f796d08df6a` via `python_ast` confidence `deterministic` hash `fcb520456941`
- `python_class` `EvidenceReference` — symbol `app.backend.src.database.models.EvidenceReference` — [source://app/backend/src/database/models.py#L113] — Provenance `prov:7b49f2e89749a544` via `python_ast` confidence `deterministic` hash `fcb520456941`
- `python_class` `GeneratedReport` — symbol `app.backend.src.database.models.GeneratedReport` — [source://app/backend/src/database/models.py#L139] — Provenance `prov:3d1c9f53137d7a7f` via `python_ast` confidence `deterministic` hash `fcb520456941`
- `python_class` `Organization` — symbol `app.backend.src.database.models.Organization` — [source://app/backend/src/database/models.py#L25] — Provenance `prov:38de1414b90cf691` via `python_ast` confidence `deterministic` hash `fcb520456941`
- `python_class` `RemediationItem` — symbol `app.backend.src.database.models.RemediationItem` — [source://app/backend/src/database/models.py#L128] — Provenance `prov:d0326c621ccf1ed3` via `python_ast` confidence `deterministic` hash `fcb520456941`
- `python_class` `User` — symbol `app.backend.src.database.models.User` — [source://app/backend/src/database/models.py#L16] — Provenance `prov:fc0babb380c532e1` via `python_ast` confidence `deterministic` hash `fcb520456941`
- `python_class` `LLMClient` — symbol `app.backend.src.llm.client.LLMClient` — [source://app/backend/src/llm/client.py#L23] — Provenance `prov:4d2efe364d661b68` via `python_ast` confidence `deterministic` hash `31ae98c2afd4`

Redacted source signal:

```text
import json
import logging
from time import perf_counter
from abc import ABC, abstractmethod

import httpx

from assessment.schemas import FindingStatus, LLMAnswerEvaluation
from assessment.text_analysis import classify_stub_answer, extract_evidence_references
from config.settings import get_setting
```
- `python_class` `OpenAICompatibleLLMClient` — symbol `app.backend.src.llm.client.OpenAICompatibleLLMClient` — [source://app/backend/src/llm/client.py#L93] — Provenance `prov:6e7208878caab605` via `python_ast` confidence `deterministic` hash `31ae98c2afd4`

Redacted source signal:

```text
import json
import logging
from time import perf_counter
from abc import ABC, abstractmethod

import httpx

from assessment.schemas import FindingStatus, LLMAnswerEvaluation
from assessment.text_analysis import classify_stub_answer, extract_evidence_references
from config.settings import get_setting
```
- `python_class` `StubLLMClient` — symbol `app.backend.src.llm.client.StubLLMClient` — [source://app/backend/src/llm/client.py#L46] — Provenance `prov:e3979cb5722eeffd` via `python_ast` confidence `deterministic` hash `31ae98c2afd4`

Redacted source signal:

```text
import json
import logging
from time import perf_counter
from abc import ABC, abstractmethod

import httpx

from assessment.schemas import FindingStatus, LLMAnswerEvaluation
from assessment.text_analysis import classify_stub_answer, extract_evidence_references
from config.settings import get_setting
```
- `python_class` `LLMDataBoundaryViolation` — symbol `app.backend.src.llm.data_boundary.LLMDataBoundaryViolation` — [source://app/backend/src/llm/data_boundary.py#L56] — Provenance `prov:8a2059993135bf76` via `python_ast` confidence `deterministic` hash `804f9a44dec1`
- `python_class` `LLMTextSource` — symbol `app.backend.src.llm.data_boundary.LLMTextSource` — [source://app/backend/src/llm/data_boundary.py#L51] — Provenance `prov:7444cf3cfc306708` via `python_ast` confidence `deterministic` hash `804f9a44dec1`
- `python_class` `LLMPolicyError` — symbol `app.backend.src.llm.policy.LLMPolicyError` — [source://app/backend/src/llm/policy.py#L34] — Provenance `prov:18b36fd66f239f06` via `python_ast` confidence `deterministic` hash `0351fa64b528`
- `python_class` `LLMTaskRequest` — symbol `app.backend.src.llm.schemas.LLMTaskRequest` — [source://app/backend/src/llm/schemas.py#L14] — Provenance `prov:8574d270de0b4165` via `python_ast` confidence `deterministic` hash `797672e10df9`
- `python_class` `LLMTaskType` — symbol `app.backend.src.llm.schemas.LLMTaskType` — [source://app/backend/src/llm/schemas.py#L9] — Provenance `prov:447aadea4c3fb085` via `python_ast` confidence `deterministic` hash `797672e10df9`
- `python_class` `PublicBetaTokenCreate` — symbol `app.backend.src.main.PublicBetaTokenCreate` — [source://app/backend/src/main.py#L47] — Provenance `prov:0b1c9110efb02c7a` via `python_ast` confidence `deterministic` hash `5a10ae600ecc`
- `python_class` `ReportEligibility` — symbol `app.backend.src.reports.readiness.ReportEligibility` — [source://app/backend/src/reports/readiness.py#L56] — Provenance `prov:265dc0da91d65d91` via `python_ast` confidence `deterministic` hash `321de5e54dc9`
- `python_class` `InformationBoundarySignal` — symbol `app.backend.src.security.information_boundary.InformationBoundarySignal` — [source://app/backend/src/security/information_boundary.py#L27] — Provenance `prov:ad5dde324eb6ec11` via `python_ast` confidence `deterministic` hash `8bdcd77295de`
- `python_class` `InformationBoundaryViolation` — symbol `app.backend.src.security.information_boundary.InformationBoundaryViolation` — [source://app/backend/src/security/information_boundary.py#L33] — Provenance `prov:7e7213f9c9837104` via `python_ast` confidence `deterministic` hash `8bdcd77295de`
- `python_class` `BiasedMetLLM` — symbol `app.backend.tests.test_browser_persona_qa_regressions.BiasedMetLLM` — [source://app/backend/tests/test_browser_persona_qa_regressions.py#L99] — Provenance `prov:b5accd030569a2f2` via `python_ast` confidence `deterministic` hash `9e566b1d543f`
- `python_class` `FailingSession` — symbol `app.backend.tests.test_health.FailingSession` — [source://app/backend/tests/test_health.py#L42] — Provenance `prov:7f012d598813e074` via `python_ast` confidence `deterministic` hash `68b71454bc84`
- `python_class` `FriendlyPromptLLM` — symbol `app.backend.tests.test_llm_assisted_interview.FriendlyPromptLLM` — [source://app/backend/tests/test_llm_assisted_interview.py#L20] — Provenance `prov:b37114347bdf34af` via `python_ast` confidence `deterministic` hash `16c46f705d11`
- `python_class` `HumanizingControlLLM` — symbol `app.backend.tests.test_llm_assisted_interview.HumanizingControlLLM` — [source://app/backend/tests/test_llm_assisted_interview.py#L30] — Provenance `prov:16ebae3f1a7f3726` via `python_ast` confidence `deterministic` hash `16c46f705d11`
- `python_class` `InventedEvidenceLLM` — symbol `app.backend.tests.test_llm_assisted_interview.InventedEvidenceLLM` — [source://app/backend/tests/test_llm_assisted_interview.py#L75] — Provenance `prov:367248335cb5a6fd` via `python_ast` confidence `deterministic` hash `16c46f705d11`
- `python_class` `MetNoEvidenceLLM` — symbol `app.backend.tests.test_llm_assisted_interview.MetNoEvidenceLLM` — [source://app/backend/tests/test_llm_assisted_interview.py#L58] — Provenance `prov:d682afe99c03f80a` via `python_ast` confidence `deterministic` hash `16c46f705d11`
- `python_class` `OutageLLM` — symbol `app.backend.tests.test_llm_assisted_interview.OutageLLM` — [source://app/backend/tests/test_llm_assisted_interview.py#L109] — Provenance `prov:9ce24c936dbab164` via `python_ast` confidence `deterministic` hash `16c46f705d11`
- `python_class` `OverclaimRationaleLLM` — symbol `app.backend.tests.test_llm_assisted_interview.OverclaimRationaleLLM` — [source://app/backend/tests/test_llm_assisted_interview.py#L92] — Provenance `prov:a0f7acab53b55071` via `python_ast` confidence `deterministic` hash `16c46f705d11`
- `python_class` `SpyPromptInjectionLLM` — symbol `app.backend.tests.test_llm_assisted_interview.SpyPromptInjectionLLM` — [source://app/backend/tests/test_llm_assisted_interview.py#L44] — Provenance `prov:c6f3a93ef9006b2d` via `python_ast` confidence `deterministic` hash `16c46f705d11`
- `python_class` `TinyPayloadSettings` — symbol `app.backend.tests.test_llm_assisted_interview.TinyPayloadSettings` — [source://app/backend/tests/test_llm_assisted_interview.py#L289] — Provenance `prov:835e11e1244ce432` via `python_ast` confidence `deterministic` hash `16c46f705d11`
- `python_class` `UnsafePromptLLM` — symbol `app.backend.tests.test_llm_assisted_interview.UnsafePromptLLM` — [source://app/backend/tests/test_llm_assisted_interview.py#L25] — Provenance `prov:aeda608e927d1da4` via `python_ast` confidence `deterministic` hash `16c46f705d11`
- `python_class` `FailingAsyncClient` — symbol `app.backend.tests.test_llm_provider_config.FailingAsyncClient` — [source://app/backend/tests/test_llm_provider_config.py#L416] — Provenance `prov:396345783a68d757` via `python_ast` confidence `deterministic` hash `099e306e55ea`
- `python_class` `FakeAsyncClient` — symbol `app.backend.tests.test_llm_provider_config.FakeAsyncClient` — [source://app/backend/tests/test_llm_provider_config.py#L514] — Provenance `prov:8b305cbe1feb14c0` via `python_ast` confidence `deterministic` hash `099e306e55ea`
- `python_class` `FakeResponse` — symbol `app.backend.tests.test_llm_provider_config.FakeResponse` — [source://app/backend/tests/test_llm_provider_config.py#L507] — Provenance `prov:72eaf979c9d75dc9` via `python_ast` confidence `deterministic` hash `099e306e55ea`
- `python_class` `Settings` — symbol `app.backend.tests.test_red_team_hardening.Settings` — [source://app/backend/tests/test_red_team_hardening.py#L479] — Provenance `prov:a0b04148a2fe4d7e` via `python_ast` confidence `deterministic` hash `b3e85247912f`

Redacted source signal:

```text
import os
import importlib

import pytest
from fastapi.testclient import TestClient

from assessment.schemas import FindingStatus
from assessment.scope_parser import parse_scope
from assessment.text_analysis import extract_evidence_references, classify_stub_answer
from assessment.state_machine impor
```
- `python_class` `FakeJwksClient` — symbol `app.backend.tests.test_supabase_auth.FakeJwksClient` — [source://app/backend/tests/test_supabase_auth.py#L214] — Provenance `prov:a338e03aa36c50d5` via `python_ast` confidence `deterministic` hash `62ccec601269`

Redacted source signal:

```text
import json
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import jwt
import pytest
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric imp
```
- `python_class` `JwksHandler` — symbol `app.backend.tests.test_supabase_auth.JwksHandler` — [source://app/backend/tests/test_supabase_auth.py#L174] — Provenance `prov:df3f0003498e8143` via `python_ast` confidence `deterministic` hash `62ccec601269`

Redacted source signal:

```text
import json
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import jwt
import pytest
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric imp
```

### python_function

- `python_function` `_database_url` — symbol `app.backend.alembic.env._database_url` — [source://app/backend/alembic/env.py#L18] — Provenance `prov:466b86195f34f132` via `python_ast` confidence `deterministic` hash `df239fcd8a00`
- `python_function` `run_migrations_offline` — symbol `app.backend.alembic.env.run_migrations_offline` — [source://app/backend/alembic/env.py#L22] — Provenance `prov:c307cecf258b4bb7` via `python_ast` confidence `deterministic` hash `df239fcd8a00`
- `python_function` `run_migrations_online` — symbol `app.backend.alembic.env.run_migrations_online` — [source://app/backend/alembic/env.py#L28] — Provenance `prov:d0dd51543ede77ed` via `python_ast` confidence `deterministic` hash `df239fcd8a00`
- `python_function` `downgrade` — symbol `app.backend.alembic.versions.0001_initial.downgrade` — [source://app/backend/alembic/versions/0001_initial.py#L33] — Provenance `prov:521feecb6b36fa50` via `python_ast` confidence `deterministic` hash `b9a82ba6452a`
- `python_function` `upgrade` — symbol `app.backend.alembic.versions.0001_initial.upgrade` — [source://app/backend/alembic/versions/0001_initial.py#L16] — Provenance `prov:cc526270fa6c89b6` via `python_ast` confidence `deterministic` hash `b9a82ba6452a`
- `python_function` `downgrade` — symbol `app.backend.alembic.versions.0002_audit_event_organization_id.downgrade` — [source://app/backend/alembic/versions/0002_audit_event_organization_id.py#L21] — Provenance `prov:34e142a55071263b` via `python_ast` confidence `deterministic` hash `0077daca005a`
- `python_function` `upgrade` — symbol `app.backend.alembic.versions.0002_audit_event_organization_id.upgrade` — [source://app/backend/alembic/versions/0002_audit_event_organization_id.py#L16] — Provenance `prov:a42aaaf90e668fd0` via `python_ast` confidence `deterministic` hash `0077daca005a`
- `python_function` `_revoke_from_supabase_api_roles` — symbol `app.backend.alembic.versions.0003_lock_down_supabase_public_table_grants._revoke_from_supabase_api_roles` — [source://app/backend/alembic/versions/0003_lock_down_supabase_public_table_grants.py#L17] — Provenance `prov:3f03c93c29b3c8c3` via `python_ast` confidence `deterministic` hash `f8d102a94cee`
- `python_function` `downgrade` — symbol `app.backend.alembic.versions.0003_lock_down_supabase_public_table_grants.downgrade` — [source://app/backend/alembic/versions/0003_lock_down_supabase_public_table_grants.py#L67] — Provenance `prov:deb4c231f09d928d` via `python_ast` confidence `deterministic` hash `f8d102a94cee`
- `python_function` `upgrade` — symbol `app.backend.alembic.versions.0003_lock_down_supabase_public_table_grants.upgrade` — [source://app/backend/alembic/versions/0003_lock_down_supabase_public_table_grants.py#L38] — Provenance `prov:ef2aa863df0d6590` via `python_ast` confidence `deterministic` hash `f8d102a94cee`
- `python_function` `downgrade` — symbol `app.backend.alembic.versions.0004_cmmc_app_rls_policies.downgrade` — [source://app/backend/alembic/versions/0004_cmmc_app_rls_policies.py#L54] — Provenance `prov:06e0f1988734be41` via `python_ast` confidence `deterministic` hash `581de9538af5`
- `python_function` `upgrade` — symbol `app.backend.alembic.versions.0004_cmmc_app_rls_policies.upgrade` — [source://app/backend/alembic/versions/0004_cmmc_app_rls_policies.py#L17] — Provenance `prov:5f593445f6c3ce0e` via `python_ast` confidence `deterministic` hash `581de9538af5`
- `python_function` `downgrade` — symbol `app.backend.alembic.versions.0005_audit_events_append_only.downgrade` — [source://app/backend/alembic/versions/0005_audit_events_append_only.py#L27] — Provenance `prov:35f0eeb853b5832f` via `python_ast` confidence `deterministic` hash `ab3203863f37`
- `python_function` `upgrade` — symbol `app.backend.alembic.versions.0005_audit_events_append_only.upgrade` — [source://app/backend/alembic/versions/0005_audit_events_append_only.py#L17] — Provenance `prov:3b8f8d67dff2e728` via `python_ast` confidence `deterministic` hash `ab3203863f37`
- `python_function` `_revoke_from_supabase_api_roles` — symbol `app.backend.alembic.versions.0006_auth_access_grants._revoke_from_supabase_api_roles` — [source://app/backend/alembic/versions/0006_auth_access_grants.py#L18] — Provenance `prov:aeaec990d6b0b1d3` via `python_ast` confidence `deterministic` hash `5c03e5e2eb9a`
- `python_function` `downgrade` — symbol `app.backend.alembic.versions.0006_auth_access_grants.downgrade` — [source://app/backend/alembic/versions/0006_auth_access_grants.py#L64] — Provenance `prov:cf5c8f389f7ccafe` via `python_ast` confidence `deterministic` hash `5c03e5e2eb9a`
- `python_function` `upgrade` — symbol `app.backend.alembic.versions.0006_auth_access_grants.upgrade` — [source://app/backend/alembic/versions/0006_auth_access_grants.py#L37] — Provenance `prov:7e314de5ba4654e1` via `python_ast` confidence `deterministic` hash `5c03e5e2eb9a`
- `python_function` `_met_revision_has_new_facts` — symbol `app.backend.src.assessment.confirmation._met_revision_has_new_facts` — [source://app/backend/src/assessment/confirmation.py#L12] — Provenance `prov:23ac1eb134c098cd` via `python_ast` confidence `deterministic` hash `4be7bcac76c0`
- `python_function` `advance_after_confirmation` — symbol `app.backend.src.assessment.confirmation.advance_after_confirmation` — [source://app/backend/src/assessment/confirmation.py#L86] — Provenance `prov:de403db3e96eb5fe` via `python_ast` confidence `deterministic` hash `4be7bcac76c0`
- `python_function` `apply_revision_to_finding` — symbol `app.backend.src.assessment.confirmation.apply_revision_to_finding` — [source://app/backend/src/assessment/confirmation.py#L37] — Provenance `prov:1baeffc6dff2256b` via `python_ast` confidence `deterministic` hash `4be7bcac76c0`
- `python_function` `confirm_current_finding` — symbol `app.backend.src.assessment.confirmation.confirm_current_finding` — [source://app/backend/src/assessment/confirmation.py#L68] — Provenance `prov:84c3032bac8b74ae` via `python_ast` confidence `deterministic` hash `4be7bcac76c0`
- `python_function` `_parse_reference_params` — symbol `app.backend.src.assessment.schemas._parse_reference_params` — [source://app/backend/src/assessment/schemas.py#L51] — Provenance `prov:cf062399483ff908` via `python_ast` confidence `deterministic` hash `711cffe52aae`

Redacted source signal:

```text
from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Annotated, Literal
from urllib.parse import parse_qsl, urlsplit
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator, model_validator


SENSITIVE_EXTERNAL_REFERENCE_QUERY_K
```
- `python_function` `_query_key_is_credential_bearing` — symbol `app.backend.src.assessment.schemas._query_key_is_credential_bearing` — [source://app/backend/src/assessment/schemas.py#L35] — Provenance `prov:fdc52e7b76f83b3b` via `python_ast` confidence `deterministic` hash `711cffe52aae`

Redacted source signal:

```text
from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Annotated, Literal
from urllib.parse import parse_qsl, urlsplit
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator, model_validator


SENSITIVE_EXTERNAL_REFERENCE_QUERY_K
```
- `python_function` `validate_external_reference` — symbol `app.backend.src.assessment.schemas.validate_external_reference` — [source://app/backend/src/assessment/schemas.py#L149] — Provenance `prov:9a93ea26ecbec5b6` via `python_ast` confidence `deterministic` hash `711cffe52aae`

Redacted source signal:

```text
from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Annotated, Literal
from urllib.parse import parse_qsl, urlsplit
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator, model_validator


SENSITIVE_EXTERNAL_REFERENCE_QUERY_K
```
- `python_function` `validate_redacted_file_path` — symbol `app.backend.src.assessment.schemas.validate_redacted_file_path` — [source://app/backend/src/assessment/schemas.py#L130] — Provenance `prov:498d2df51bd9cc92` via `python_ast` confidence `deterministic` hash `711cffe52aae`

Redacted source signal:

```text
from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Annotated, Literal
from urllib.parse import parse_qsl, urlsplit
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator, model_validator


SENSITIVE_EXTERNAL_REFERENCE_QUERY_K
```
- `python_function` `validate_requirements` — symbol `app.backend.src.assessment.schemas.validate_requirements` — [source://app/backend/src/assessment/schemas.py#L104] — Provenance `prov:6226e8dd54b9b716` via `python_ast` confidence `deterministic` hash `711cffe52aae`

Redacted source signal:

```text
from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Annotated, Literal
from urllib.parse import parse_qsl, urlsplit
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator, model_validator


SENSITIVE_EXTERNAL_REFERENCE_QUERY_K
```
- `python_function` `_clause_for_match` — symbol `app.backend.src.assessment.scope_parser._clause_for_match` — [source://app/backend/src/assessment/scope_parser.py#L132] — Provenance `prov:dc979d2d5ec32048` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_contains` — symbol `app.backend.src.assessment.scope_parser._contains` — [source://app/backend/src/assessment/scope_parser.py#L123] — Provenance `prov:403d6b58fff98c99` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_coordinated_negated_segment_bounds` — symbol `app.backend.src.assessment.scope_parser._coordinated_negated_segment_bounds` — [source://app/backend/src/assessment/scope_parser.py#L293] — Provenance `prov:02075022dd608432` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_coordinated_segments` — symbol `app.backend.src.assessment.scope_parser._coordinated_segments` — [source://app/backend/src/assessment/scope_parser.py#L156] — Provenance `prov:66ee1d4841bacb21` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_direct_negated_match_span` — symbol `app.backend.src.assessment.scope_parser._direct_negated_match_span` — [source://app/backend/src/assessment/scope_parser.py#L401] — Provenance `prov:7e937727b3fb49fd` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_disjunctive_negated_clause_spans` — symbol `app.backend.src.assessment.scope_parser._disjunctive_negated_clause_spans` — [source://app/backend/src/assessment/scope_parser.py#L210] — Provenance `prov:61d3dd29a2375cf6` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_hard_clause_bounds` — symbol `app.backend.src.assessment.scope_parser._hard_clause_bounds` — [source://app/backend/src/assessment/scope_parser.py#L144] — Provenance `prov:2b03e06a85cc1f24` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_hard_clause_segments` — symbol `app.backend.src.assessment.scope_parser._hard_clause_segments` — [source://app/backend/src/assessment/scope_parser.py#L200] — Provenance `prov:2a835410c4bf5c0a` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_has_positive_scope_mention` — symbol `app.backend.src.assessment.scope_parser._has_positive_scope_mention` — [source://app/backend/src/assessment/scope_parser.py#L394] — Provenance `prov:4fc3bdb84e4dbca6` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_is_coordinated_negated` — symbol `app.backend.src.assessment.scope_parser._is_coordinated_negated` — [source://app/backend/src/assessment/scope_parser.py#L330] — Provenance `prov:73d018b0f8e52906` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_is_meaningful_other_item` — symbol `app.backend.src.assessment.scope_parser._is_meaningful_other_item` — [source://app/backend/src/assessment/scope_parser.py#L496] — Provenance `prov:9a0cca0e93661f57` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_is_negated` — symbol `app.backend.src.assessment.scope_parser._is_negated` — [source://app/backend/src/assessment/scope_parser.py#L374] — Provenance `prov:1f8acb2bf00adfd1` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_is_negated_match` — symbol `app.backend.src.assessment.scope_parser._is_negated_match` — [source://app/backend/src/assessment/scope_parser.py#L378] — Provenance `prov:f89395ae59a4a2bb` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_iter_scope_mentions` — symbol `app.backend.src.assessment.scope_parser._iter_scope_mentions` — [source://app/backend/src/assessment/scope_parser.py#L387] — Provenance `prov:c62d8f5c29bc72df` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_merge_spans` — symbol `app.backend.src.assessment.scope_parser._merge_spans` — [source://app/backend/src/assessment/scope_parser.py#L417] — Provenance `prov:217aaea970356138` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_negated_match_span` — symbol `app.backend.src.assessment.scope_parser._negated_match_span` — [source://app/backend/src/assessment/scope_parser.py#L409] — Provenance `prov:704f2686f2d2101e` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_negated_reference_patterns` — symbol `app.backend.src.assessment.scope_parser._negated_reference_patterns` — [source://app/backend/src/assessment/scope_parser.py#L334] — Provenance `prov:4a9e152d37272fa1` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_provider_boundary_separator_releases_negation` — symbol `app.backend.src.assessment.scope_parser._provider_boundary_separator_releases_negation` — [source://app/backend/src/assessment/scope_parser.py#L289] — Provenance `prov:d5077e7a54cf3dd8` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_remove_spans` — symbol `app.backend.src.assessment.scope_parser._remove_spans` — [source://app/backend/src/assessment/scope_parser.py#L429] — Provenance `prov:8e669538e9db9f96` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_segment_has_asset_scope_cue` — symbol `app.backend.src.assessment.scope_parser._segment_has_asset_scope_cue` — [source://app/backend/src/assessment/scope_parser.py#L189] — Provenance `prov:c382bc949a13bf58` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_segment_has_independent_asset_cue` — symbol `app.backend.src.assessment.scope_parser._segment_has_independent_asset_cue` — [source://app/backend/src/assessment/scope_parser.py#L185] — Provenance `prov:056473b8fd2d81c7` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_segment_has_positive_scope_cue` — symbol `app.backend.src.assessment.scope_parser._segment_has_positive_scope_cue` — [source://app/backend/src/assessment/scope_parser.py#L181] — Provenance `prov:d192573d2ca52afb` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_segment_has_provider_boundary_cue` — symbol `app.backend.src.assessment.scope_parser._segment_has_provider_boundary_cue` — [source://app/backend/src/assessment/scope_parser.py#L193] — Provenance `prov:34675eadc26e159a` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_segment_index_for_match` — symbol `app.backend.src.assessment.scope_parser._segment_index_for_match` — [source://app/backend/src/assessment/scope_parser.py#L168] — Provenance `prov:785dc995a163faf0` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_strip_negated_scope_references` — symbol `app.backend.src.assessment.scope_parser._strip_negated_scope_references` — [source://app/backend/src/assessment/scope_parser.py#L442] — Provenance `prov:22871cf37714e6e8` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_suppress_less_specific_labels` — symbol `app.backend.src.assessment.scope_parser._suppress_less_specific_labels` — [source://app/backend/src/assessment/scope_parser.py#L476] — Provenance `prov:2d48c357beb80d1e` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_term_pattern` — symbol `app.backend.src.assessment.scope_parser._term_pattern` — [source://app/backend/src/assessment/scope_parser.py#L128] — Provenance `prov:b3ebb83035be1a8e` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_trailing_coordinated_negated_clause_bounds` — symbol `app.backend.src.assessment.scope_parser._trailing_coordinated_negated_clause_bounds` — [source://app/backend/src/assessment/scope_parser.py#L267] — Provenance `prov:a14c3aff922b3983` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_trailing_coordinated_negated_clause_spans` — symbol `app.backend.src.assessment.scope_parser._trailing_coordinated_negated_clause_spans` — [source://app/backend/src/assessment/scope_parser.py#L253] — Provenance `prov:16d2c62f6a278c36` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_trailing_coordinated_negated_subject_span` — symbol `app.backend.src.assessment.scope_parser._trailing_coordinated_negated_subject_span` — [source://app/backend/src/assessment/scope_parser.py#L235] — Provenance `prov:9d465adbf590e9e7` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_trailing_negation_applies_to_all_coordinated_subjects` — symbol `app.backend.src.assessment.scope_parser._trailing_negation_applies_to_all_coordinated_subjects` — [source://app/backend/src/assessment/scope_parser.py#L222] — Provenance `prov:a899b5809e89ad2a` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_trailing_predicate_verb` — symbol `app.backend.src.assessment.scope_parser._trailing_predicate_verb` — [source://app/backend/src/assessment/scope_parser.py#L218] — Provenance `prov:b38e2f876656eeb1` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_unique` — symbol `app.backend.src.assessment.scope_parser._unique` — [source://app/backend/src/assessment/scope_parser.py#L112] — Provenance `prov:9eba720e69f81899` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `has_independent_asset_signal` — symbol `app.backend.src.assessment.scope_parser.has_independent_asset_signal` — [source://app/backend/src/assessment/scope_parser.py#L467] — Provenance `prov:c897b0ac3432a8ab` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `has_meaningful_scope` — symbol `app.backend.src.assessment.scope_parser.has_meaningful_scope` — [source://app/backend/src/assessment/scope_parser.py#L513] — Provenance `prov:e13eda15a8e8c703` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `meaningful_other_scope_items` — symbol `app.backend.src.assessment.scope_parser.meaningful_other_scope_items` — [source://app/backend/src/assessment/scope_parser.py#L505] — Provenance `prov:ed0e27d1c413ace0` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `normalize_scope` — symbol `app.backend.src.assessment.scope_parser.normalize_scope` — [source://app/backend/src/assessment/scope_parser.py#L517] — Provenance `prov:ef2346e6150f3867` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `other_scope_items` — symbol `app.backend.src.assessment.scope_parser.other_scope_items` — [source://app/backend/src/assessment/scope_parser.py#L485] — Provenance `prov:8f55cbe189a91a7c` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `parse_scope` — symbol `app.backend.src.assessment.scope_parser.parse_scope` — [source://app/backend/src/assessment/scope_parser.py#L536] — Provenance `prov:407be8af91c731e2` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `scope_requires_other_review` — symbol `app.backend.src.assessment.scope_parser.scope_requires_other_review` — [source://app/backend/src/assessment/scope_parser.py#L509] — Provenance `prov:e270ee89cf2614ca` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_function` `_assistant_text_with_optional_llm` — symbol `app.backend.src.assessment.state_machine._assistant_text_with_optional_llm` — [source://app/backend/src/assessment/state_machine.py#L236] — Provenance `prov:ccb864fb4fa501c7` via `python_ast` confidence `deterministic` hash `e775d84f4f5b`
- `python_function` `_combined_control_answer` — symbol `app.backend.src.assessment.state_machine._combined_control_answer` — [source://app/backend/src/assessment/state_machine.py#L136] — Provenance `prov:36c5b95f91ef1b6e` via `python_ast` confidence `deterministic` hash `e775d84f4f5b`
- `python_function` `_control_answer_history` — symbol `app.backend.src.assessment.state_machine._control_answer_history` — [source://app/backend/src/assessment/state_machine.py#L120] — Provenance `prov:41cc195fa9c4a3cb` via `python_ast` confidence `deterministic` hash `e775d84f4f5b`
- `python_function` `_ensure_evidence_register_rows` — symbol `app.backend.src.assessment.state_machine._ensure_evidence_register_rows` — [source://app/backend/src/assessment/state_machine.py#L503] — Provenance `prov:7e761b55d4d859c5` via `python_ast` confidence `deterministic` hash `e775d84f4f5b`
- `python_function` `_has_unnegated_level2_signal` — symbol `app.backend.src.assessment.state_machine._has_unnegated_level2_signal` — [source://app/backend/src/assessment/state_machine.py#L174] — Provenance `prov:074dc5a5f557d527` via `python_ast` confidence `deterministic` hash `e775d84f4f5b`
- `python_function` `_level2_signal_is_negated` — symbol `app.backend.src.assessment.state_machine._level2_signal_is_negated` — [source://app/backend/src/assessment/state_machine.py#L165] — Provenance `prov:077d7a01fb396797` via `python_ast` confidence `deterministic` hash `e775d84f4f5b`
- `python_function` `_other_scope_review_prompt` — symbol `app.backend.src.assessment.state_machine._other_scope_review_prompt` — [source://app/backend/src/assessment/state_machine.py#L95] — Provenance `prov:1ea1a30acffb203e` via `python_ast` confidence `deterministic` hash `e775d84f4f5b`
- `python_function` `_record_control_answer` — symbol `app.backend.src.assessment.state_machine._record_control_answer` — [source://app/backend/src/assessment/state_machine.py#L129] — Provenance `prov:6b7c80ca541d7071` via `python_ast` confidence `deterministic` hash `e775d84f4f5b`
- `python_function` `_record_scope_answer` — symbol `app.backend.src.assessment.state_machine._record_scope_answer` — [source://app/backend/src/assessment/state_machine.py#L112] — Provenance `prov:650909bd3249c8d2` via `python_ast` confidence `deterministic` hash `e775d84f4f5b`
- `python_function` `_scope_raw_answers` — symbol `app.backend.src.assessment.state_machine._scope_raw_answers` — [source://app/backend/src/assessment/state_machine.py#L104] — Provenance `prov:17eaec7cbd4ea6f5` via `python_ast` confidence `deterministic` hash `e775d84f4f5b`
- `python_function` `_unique` — symbol `app.backend.src.assessment.state_machine._unique` — [source://app/backend/src/assessment/state_machine.py#L67] — Provenance `prov:44d98be82bcba3c6` via `python_ast` confidence `deterministic` hash `e775d84f4f5b`
- `python_function` `can_generate_report` — symbol `app.backend.src.assessment.state_machine.can_generate_report` — [source://app/backend/src/assessment/state_machine.py#L546] — Provenance `prov:af9f6a6b68b8098d` via `python_ast` confidence `deterministic` hash `e775d84f4f5b`
- `python_function` `control_question` — symbol `app.backend.src.assessment.state_machine.control_question` — [source://app/backend/src/assessment/state_machine.py#L468] — Provenance `prov:3de055db4078c3f7` via `python_ast` confidence `deterministic` hash `e775d84f4f5b`
- `python_function` `deterministic_triage` — symbol `app.backend.src.assessment.state_machine.deterministic_triage` — [source://app/backend/src/assessment/state_machine.py#L182] — Provenance `prov:b910e5278f52d876` via `python_ast` confidence `deterministic` hash `e775d84f4f5b`

### python_import

- `python_import` `database` — symbol `database` — [source://app/backend/alembic/env.py#L10] — Provenance `prov:c50498d342ea3372` via `python_ast` confidence `deterministic` hash `df239fcd8a00`
- `python_import` `logging.config` — symbol `logging.config` — [source://app/backend/alembic/env.py#L1] — Provenance `prov:84c86053a92a6f2b` via `python_ast` confidence `deterministic` hash `df239fcd8a00`
- `python_import` `sys` — symbol `sys` — [source://app/backend/alembic/env.py#L4] — Provenance `prov:068829f684f6b86d` via `python_ast` confidence `deterministic` hash `df239fcd8a00`
- `python_import` `copy` — symbol `copy` — [source://app/backend/src/assessment/state_machine.py#L1] — Provenance `prov:d53bbf9f10439ae8` via `python_ast` confidence `deterministic` hash `e775d84f4f5b`
- `python_import` `base64` — symbol `base64` — [source://app/backend/src/auth/public_beta.py#L1] — Provenance `prov:fb1e270b347a5ad6` via `python_ast` confidence `deterministic` hash `77b86338d3da`

Redacted source signal:

```text
import base64
import hashlib
import hmac
import json
from dataclasses import dataclass


class PublicBetaTokenError(ValueError):
    pass


@dataclass(frozen=True)
class PublicBetaClaims:
    organization_id: str
    user_id: str
    email: str
    organization_name: str


def _b64encode(raw: bytes)
```
- `python_import` `hashlib` — symbol `hashlib` — [source://app/backend/src/auth/public_beta.py#L2] — Provenance `prov:b1277d7fcb755adb` via `python_ast` confidence `deterministic` hash `77b86338d3da`

Redacted source signal:

```text
import base64
import hashlib
import hmac
import json
from dataclasses import dataclass


class PublicBetaTokenError(ValueError):
    pass


@dataclass(frozen=True)
class PublicBetaClaims:
    organization_id: str
    user_id: str
    email: str
    organization_name: str


def _b64encode(raw: bytes)
```
- `python_import` `hmac` — symbol `hmac` — [source://app/backend/src/auth/public_beta.py#L3] — Provenance `prov:ab51d2101d97bba4` via `python_ast` confidence `deterministic` hash `77b86338d3da`

Redacted source signal:

```text
import base64
import hashlib
import hmac
import json
from dataclasses import dataclass


class PublicBetaTokenError(ValueError):
    pass


@dataclass(frozen=True)
class PublicBetaClaims:
    organization_id: str
    user_id: str
    email: str
    organization_name: str


def _b64encode(raw: bytes)
```
- `python_import` `ipaddress` — symbol `ipaddress` — [source://app/backend/src/config/settings.py#L2] — Provenance `prov:f24f09b771022a65` via `python_ast` confidence `deterministic` hash `a7f19740b398`

Redacted source signal:

```text
from functools import lru_cache
from ipaddress import ip_address
from socket import inet_aton
from urllib.parse import urlparse

from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigurationError(RuntimeError):
    pass


class Settings(BaseSettings):
    app_name: str = "CMMC
```
- `python_import` `pydantic_settings` — symbol `pydantic_settings` — [source://app/backend/src/config/settings.py#L6] — Provenance `prov:a43c0a6e9c783000` via `python_ast` confidence `deterministic` hash `a7f19740b398`

Redacted source signal:

```text
from functools import lru_cache
from ipaddress import ip_address
from socket import inet_aton
from urllib.parse import urlparse

from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigurationError(RuntimeError):
    pass


class Settings(BaseSettings):
    app_name: str = "CMMC
```
- `python_import` `socket` — symbol `socket` — [source://app/backend/src/config/settings.py#L3] — Provenance `prov:69adbebb3750381a` via `python_ast` confidence `deterministic` hash `a7f19740b398`

Redacted source signal:

```text
from functools import lru_cache
from ipaddress import ip_address
from socket import inet_aton
from urllib.parse import urlparse

from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigurationError(RuntimeError):
    pass


class Settings(BaseSettings):
    app_name: str = "CMMC
```
- `python_import` `functools` — symbol `functools` — [source://app/backend/src/controls/library.py#L2] — Provenance `prov:e95b19efb348e0f4` via `python_ast` confidence `deterministic` hash `611f90f5e7eb`
- `python_import` `abc` — symbol `abc` — [source://app/backend/src/llm/client.py#L4] — Provenance `prov:da18788119c4e885` via `python_ast` confidence `deterministic` hash `31ae98c2afd4`

Redacted source signal:

```text
import json
import logging
from time import perf_counter
from abc import ABC, abstractmethod

import httpx

from assessment.schemas import FindingStatus, LLMAnswerEvaluation
from assessment.text_analysis import classify_stub_answer, extract_evidence_references
from config.settings import get_setting
```
- `python_import` `httpx` — symbol `httpx` — [source://app/backend/src/llm/client.py#L6] — Provenance `prov:e7a4ef6c9592c433` via `python_ast` confidence `deterministic` hash `31ae98c2afd4`

Redacted source signal:

```text
import json
import logging
from time import perf_counter
from abc import ABC, abstractmethod

import httpx

from assessment.schemas import FindingStatus, LLMAnswerEvaluation
from assessment.text_analysis import classify_stub_answer, extract_evidence_references
from config.settings import get_setting
```
- `python_import` `time` — symbol `time` — [source://app/backend/src/llm/client.py#L3] — Provenance `prov:5d1876f6f514275d` via `python_ast` confidence `deterministic` hash `31ae98c2afd4`

Redacted source signal:

```text
import json
import logging
from time import perf_counter
from abc import ABC, abstractmethod

import httpx

from assessment.schemas import FindingStatus, LLMAnswerEvaluation
from assessment.text_analysis import classify_stub_answer, extract_evidence_references
from config.settings import get_setting
```
- `python_import` `enum` — symbol `enum` — [source://app/backend/src/llm/schemas.py#L3] — Provenance `prov:fc6f406522b6a0b7` via `python_ast` confidence `deterministic` hash `797672e10df9`
- `python_import` `alembic` — symbol `alembic` — [source://app/backend/src/main.py#L5] — Provenance `prov:1b28c427a239d6cf` via `python_ast` confidence `deterministic` hash `5a10ae600ecc`
- `python_import` `alembic.config` — symbol `alembic.config` — [source://app/backend/src/main.py#L6] — Provenance `prov:c785f5c2a3d7b650` via `python_ast` confidence `deterministic` hash `5a10ae600ecc`
- `python_import` `contextlib` — symbol `contextlib` — [source://app/backend/src/main.py#L2] — Provenance `prov:fd7378f6135cc4a3` via `python_ast` confidence `deterministic` hash `5a10ae600ecc`
- `python_import` `fastapi` — symbol `fastapi` — [source://app/backend/src/main.py#L7] — Provenance `prov:ae47d6d63c1fe609` via `python_ast` confidence `deterministic` hash `5a10ae600ecc`
- `python_import` `fastapi.middleware.cors` — symbol `fastapi.middleware.cors` — [source://app/backend/src/main.py#L10] — Provenance `prov:c8e1c52fab8e44a4` via `python_ast` confidence `deterministic` hash `5a10ae600ecc`
- `python_import` `fastapi.responses` — symbol `fastapi.responses` — [source://app/backend/src/main.py#L11] — Provenance `prov:37c86dba4b9fc9a7` via `python_ast` confidence `deterministic` hash `5a10ae600ecc`
- `python_import` `io` — symbol `io` — [source://app/backend/src/main.py#L18] — Provenance `prov:90f7e3c0bcdeacc6` via `python_ast` confidence `deterministic` hash `5a10ae600ecc`
- `python_import` `pydantic` — symbol `pydantic` — [source://app/backend/src/main.py#L8] — Provenance `prov:c7348fca08051c7a` via `python_ast` confidence `deterministic` hash `5a10ae600ecc`
- `python_import` `slowapi` — symbol `slowapi` — [source://app/backend/src/main.py#L12] — Provenance `prov:c43a51b835204a62` via `python_ast` confidence `deterministic` hash `5a10ae600ecc`
- `python_import` `slowapi.errors` — symbol `slowapi.errors` — [source://app/backend/src/main.py#L14] — Provenance `prov:350266a9c19f90fe` via `python_ast` confidence `deterministic` hash `5a10ae600ecc`
- `python_import` `slowapi.util` — symbol `slowapi.util` — [source://app/backend/src/main.py#L13] — Provenance `prov:faf1fc9e00f1fd89` via `python_ast` confidence `deterministic` hash `5a10ae600ecc`
- `python_import` `starlette` — symbol `starlette` — [source://app/backend/src/main.py#L9] — Provenance `prov:5b46245e91d3d65d` via `python_ast` confidence `deterministic` hash `5a10ae600ecc`
- `python_import` `uuid` — symbol `uuid` — [source://app/backend/src/main.py#L1] — Provenance `prov:fdfe4618f9d775da` via `python_ast` confidence `deterministic` hash `5a10ae600ecc`
- `python_import` `weasyprint` — symbol `weasyprint` — [source://app/backend/src/main.py#L666] — Provenance `prov:34310d57904452f8` via `python_ast` confidence `deterministic` hash `5a10ae600ecc`
- `python_import` `reports.readiness` — symbol `reports.readiness` — [source://app/backend/src/reports/generator.py#L8] — Provenance `prov:6282482a5904405b` via `python_ast` confidence `deterministic` hash `f7e929ccdd20`
- `python_import` `sqlalchemy.orm` — symbol `sqlalchemy.orm` — [source://app/backend/src/reports/generator.py#L3] — Provenance `prov:2f50d38301135a4d` via `python_ast` confidence `deterministic` hash `f7e929ccdd20`
- `python_import` `collections` — symbol `collections` — [source://app/backend/src/reports/readiness.py#L3] — Provenance `prov:ef39e5bb2439b429` via `python_ast` confidence `deterministic` hash `321de5e54dc9`
- `python_import` `dataclasses` — symbol `dataclasses` — [source://app/backend/src/security/information_boundary.py#L3] — Provenance `prov:207c6fe7b4bf2ec8` via `python_ast` confidence `deterministic` hash `8bdcd77295de`
- `python_import` `typing` — symbol `typing` — [source://app/backend/src/security/information_boundary.py#L5] — Provenance `prov:56349d22f702ab3b` via `python_ast` confidence `deterministic` hash `8bdcd77295de`
- `python_import` `__future__` — symbol `__future__` — [source://app/backend/src/security/language.py#L1] — Provenance `prov:4714b73155671532` via `python_ast` confidence `deterministic` hash `decb66545081`
- `python_import` `urllib.parse` — symbol `urllib.parse` — [source://app/backend/src/testing/db_safety.py#L2] — Provenance `prov:4e135a5a40fb5b00` via `python_ast` confidence `deterministic` hash `32e1b5615896`
- `python_import` `assessment.confirmation` — symbol `assessment.confirmation` — [source://app/backend/tests/test_browser_persona_qa_remediation.py#L7] — Provenance `prov:1e5050791b36cd66` via `python_ast` confidence `deterministic` hash `c7d7b4cb2f9b`
- `python_import` `security` — symbol `security` — [source://app/backend/tests/test_full_assessment_flow.py#L112] — Provenance `prov:71b2690c93c932f8` via `python_ast` confidence `deterministic` hash `6f38b3391c38`
- `python_import` `sqlalchemy.exc` — symbol `sqlalchemy.exc` — [source://app/backend/tests/test_health.py#L5] — Provenance `prov:fa66458a80db1e8c` via `python_ast` confidence `deterministic` hash `68b71454bc84`
- `python_import` `security.information_boundary` — symbol `security.information_boundary` — [source://app/backend/tests/test_information_boundary.py#L6] — Provenance `prov:7eb4d52738999b7a` via `python_ast` confidence `deterministic` hash `8bb3322799b1`
- `python_import` `shutil` — symbol `shutil` — [source://app/backend/tests/test_issue_9_report_pdf_smoke.py#L3] — Provenance `prov:19d68065eb76b5f4` via `python_ast` confidence `deterministic` hash `995ec2fe1cf2`
- `python_import` `subprocess` — symbol `subprocess` — [source://app/backend/tests/test_issue_9_report_pdf_smoke.py#L4] — Provenance `prov:557f96ef8a1e990e` via `python_ast` confidence `deterministic` hash `995ec2fe1cf2`
- `python_import` `tempfile` — symbol `tempfile` — [source://app/backend/tests/test_issue_9_report_pdf_smoke.py#L5] — Provenance `prov:0e705b14ee5f9f09` via `python_ast` confidence `deterministic` hash `995ec2fe1cf2`
- `python_import` `llm.data_boundary` — symbol `llm.data_boundary` — [source://app/backend/tests/test_llm_input_boundary_all_sources.py#L194] — Provenance `prov:4b6f83026669cd36` via `python_ast` confidence `deterministic` hash `0579233dd66e`

Redacted source signal:

```text
import pytest
from fastapi.testclient import TestClient

from controls.library import get_control
from database.base import SessionLocal
from database.models import (
    AssessmentMessage,
    AssessmentSession,
    AuditEvent,
    ControlFinding,
    EvidenceReference,
    GeneratedReport,
    Org
```
- `python_import` `llm.policy` — symbol `llm.policy` — [source://app/backend/tests/test_llm_policy.py#L130] — Provenance `prov:e67d0bd464d6b2e0` via `python_ast` confidence `deterministic` hash `4d6c8d1f7338`

Redacted source signal:

```text
import pytest

from assessment.schemas import FindingStatus, LLMAnswerEvaluation


def fallback_evaluation():
    return LLMAnswerEvaluation(
        answer_summary="fallback",
        sufficiency="ambiguous",
        proposed_status=FindingStatus.UNKNOWN,
        rationale="Fallback used because th
```
- `python_import` `llm.schemas` — symbol `llm.schemas` — [source://app/backend/tests/test_llm_policy.py#L91] — Provenance `prov:61cd9ffec0d71fee` via `python_ast` confidence `deterministic` hash `4d6c8d1f7338`

Redacted source signal:

```text
import pytest

from assessment.schemas import FindingStatus, LLMAnswerEvaluation


def fallback_evaluation():
    return LLMAnswerEvaluation(
        answer_summary="fallback",
        sufficiency="ambiguous",
        proposed_status=FindingStatus.UNKNOWN,
        rationale="Fallback used because th
```
- `python_import` `logging` — symbol `logging` — [source://app/backend/tests/test_llm_provider_config.py#L2] — Provenance `prov:f69b200a506a09ce` via `python_ast` confidence `deterministic` hash `099e306e55ea`
- `python_import` `security.prompt_injection` — symbol `security.prompt_injection` — [source://app/backend/tests/test_mvp.py#L11] — Provenance `prov:e2295d96055b5018` via `python_ast` confidence `deterministic` hash `92b287dea155`
- `python_import` `re` — symbol `re` — [source://app/backend/tests/test_opus_browser_findings.py#L1] — Provenance `prov:40aca135d9c6a5c7` via `python_ast` confidence `deterministic` hash `655835aa996c`
- `python_import` `auth.public_beta` — symbol `auth.public_beta` — [source://app/backend/tests/test_public_beta_auth.py#L6] — Provenance `prov:3ba77c47cbbbe1c0` via `python_ast` confidence `deterministic` hash `ce4b691a2cdf`

Redacted source signal:

```text
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from auth.public_beta import PublicBetaTokenError, sign_public_beta_token, verify_public_beta_token
from database.base import Base, engine, SessionLocal
from database.models import Organization, User
from mai
```
- `python_import` `assessment.schemas` — symbol `assessment.schemas` — [source://app/backend/tests/test_red_team_hardening.py#L7] — Provenance `prov:de75eadcd9f3c1ae` via `python_ast` confidence `deterministic` hash `b3e85247912f`

Redacted source signal:

```text
import os
import importlib

import pytest
from fastapi.testclient import TestClient

from assessment.schemas import FindingStatus
from assessment.scope_parser import parse_scope
from assessment.text_analysis import extract_evidence_references, classify_stub_answer
from assessment.state_machine impor
```
- `python_import` `assessment.text_analysis` — symbol `assessment.text_analysis` — [source://app/backend/tests/test_red_team_hardening.py#L9] — Provenance `prov:abf223125d201b17` via `python_ast` confidence `deterministic` hash `b3e85247912f`

Redacted source signal:

```text
import os
import importlib

import pytest
from fastapi.testclient import TestClient

from assessment.schemas import FindingStatus
from assessment.scope_parser import parse_scope
from assessment.text_analysis import extract_evidence_references, classify_stub_answer
from assessment.state_machine impor
```
- `python_import` `audit.events` — symbol `audit.events` — [source://app/backend/tests/test_red_team_hardening.py#L418] — Provenance `prov:7ac0460f4f564dcc` via `python_ast` confidence `deterministic` hash `b3e85247912f`

Redacted source signal:

```text
import os
import importlib

import pytest
from fastapi.testclient import TestClient

from assessment.schemas import FindingStatus
from assessment.scope_parser import parse_scope
from assessment.text_analysis import extract_evidence_references, classify_stub_answer
from assessment.state_machine impor
```
- `python_import` `importlib` — symbol `importlib` — [source://app/backend/tests/test_red_team_hardening.py#L2] — Provenance `prov:34ab2931ddc21322` via `python_ast` confidence `deterministic` hash `b3e85247912f`

Redacted source signal:

```text
import os
import importlib

import pytest
from fastapi.testclient import TestClient

from assessment.schemas import FindingStatus
from assessment.scope_parser import parse_scope
from assessment.text_analysis import extract_evidence_references, classify_stub_answer
from assessment.state_machine impor
```
- `python_import` `builtins` — symbol `builtins` — [source://app/backend/tests/test_report_pdf.py#L1] — Provenance `prov:cd5b4a00008d33bc` via `python_ast` confidence `deterministic` hash `186ed4c8ff4c`
- `python_import` `html` — symbol `html` — [source://app/backend/tests/test_report_quality.py#L1] — Provenance `prov:934a0dbb9ea4255f` via `python_ast` confidence `deterministic` hash `e733011b7126`
- `python_import` `reports.generator` — symbol `reports.generator` — [source://app/backend/tests/test_report_quality.py#L11] — Provenance `prov:c16ace118d5cca6e` via `python_ast` confidence `deterministic` hash `e733011b7126`
- `python_import` `security.language` — symbol `security.language` — [source://app/backend/tests/test_report_quality.py#L12] — Provenance `prov:441cd9764fe58279` via `python_ast` confidence `deterministic` hash `e733011b7126`
- `python_import` `assessment.state_machine` — symbol `assessment.state_machine` — [source://app/backend/tests/test_reported_feedback_regressions.py#L6] — Provenance `prov:e3ebc991dd153d41` via `python_ast` confidence `deterministic` hash `48fe759a9bce`
- `python_import` `asyncio` — symbol `asyncio` — [source://app/backend/tests/test_reported_feedback_regressions.py#L1] — Provenance `prov:990c10e29a2b0657` via `python_ast` confidence `deterministic` hash `48fe759a9bce`
- `python_import` `controls.library` — symbol `controls.library` — [source://app/backend/tests/test_reported_feedback_regressions.py#L7] — Provenance `prov:b8f27eb65776ccc3` via `python_ast` confidence `deterministic` hash `48fe759a9bce`
- `python_import` `llm.client` — symbol `llm.client` — [source://app/backend/tests/test_reported_feedback_regressions.py#L9] — Provenance `prov:9a0e00edb241f261` via `python_ast` confidence `deterministic` hash `48fe759a9bce`
- `python_import` `assessment.scope_parser` — symbol `assessment.scope_parser` — [source://app/backend/tests/test_scope_unknowns.py#L3] — Provenance `prov:cc74424c419c297d` via `python_ast` confidence `deterministic` hash `c390511423d8`
- `python_import` `config.settings` — symbol `config.settings` — [source://app/backend/tests/test_startup_config.py#L7] — Provenance `prov:2ca660c82ce91f73` via `python_ast` confidence `deterministic` hash `da418c28c50f`

Redacted source signal:

```text
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

from config.settings import ConfigurationError, Settings, validate_production_auth_configuration, validate_production_settings
from main import (
    alembic_head_revis
```
- `python_import` `sqlalchemy` — symbol `sqlalchemy` — [source://app/backend/tests/test_startup_config.py#L4] — Provenance `prov:759b83c13084f9e9` via `python_ast` confidence `deterministic` hash `da418c28c50f`

Redacted source signal:

```text
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

from config.settings import ConfigurationError, Settings, validate_production_auth_configuration, validate_production_settings
from main import (
    alembic_head_revis
```
- `python_import` `sqlalchemy.pool` — symbol `sqlalchemy.pool` — [source://app/backend/tests/test_startup_config.py#L5] — Provenance `prov:4dac4539827d4342` via `python_ast` confidence `deterministic` hash `da418c28c50f`

Redacted source signal:

```text
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

from config.settings import ConfigurationError, Settings, validate_production_auth_configuration, validate_production_settings
from main import (
    alembic_head_revis
```
- `python_import` `auth.dependencies` — symbol `auth.dependencies` — [source://app/backend/tests/test_supabase_auth.py#L45] — Provenance `prov:862c1988dcae4192` via `python_ast` confidence `deterministic` hash `62ccec601269`

Redacted source signal:

```text
import json
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import jwt
import pytest
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric imp
```
- `python_import` `auth.supabase` — symbol `auth.supabase` — [source://app/backend/tests/test_supabase_auth.py#L212] — Provenance `prov:dbbdca5c94c31e54` via `python_ast` confidence `deterministic` hash `62ccec601269`

Redacted source signal:

```text
import json
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import jwt
import pytest
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric imp
```
- `python_import` `cryptography.hazmat.primitives.asymmetric` — symbol `cryptography.hazmat.primitives.asymmetric` — [source://app/backend/tests/test_supabase_auth.py#L10] — Provenance `prov:0d2d423aeb3367d1` via `python_ast` confidence `deterministic` hash `62ccec601269`

Redacted source signal:

```text
import json
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import jwt
import pytest
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric imp
```
- `python_import` `datetime` — symbol `datetime` — [source://app/backend/tests/test_supabase_auth.py#L3] — Provenance `prov:d987166e0f5af47c` via `python_ast` confidence `deterministic` hash `62ccec601269`

Redacted source signal:

```text
import json
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import jwt
import pytest
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric imp
```
- `python_import` `http.server` — symbol `http.server` — [source://app/backend/tests/test_supabase_auth.py#L4] — Provenance `prov:941d6c8cb9533b11` via `python_ast` confidence `deterministic` hash `62ccec601269`

Redacted source signal:

```text
import json
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import jwt
import pytest
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric imp
```
- `python_import` `json` — symbol `json` — [source://app/backend/tests/test_supabase_auth.py#L1] — Provenance `prov:a26f515dfe7be11d` via `python_ast` confidence `deterministic` hash `62ccec601269`

Redacted source signal:

```text
import json
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import jwt
import pytest
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric imp
```
- `python_import` `jwt` — symbol `jwt` — [source://app/backend/tests/test_supabase_auth.py#L7] — Provenance `prov:9e657674f7015ff2` via `python_ast` confidence `deterministic` hash `62ccec601269`

Redacted source signal:

```text
import json
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import jwt
import pytest
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric imp
```
- `python_import` `threading` — symbol `threading` — [source://app/backend/tests/test_supabase_auth.py#L2] — Provenance `prov:f5e8c9cbd0d52c31` via `python_ast` confidence `deterministic` hash `62ccec601269`

Redacted source signal:

```text
import json
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import jwt
import pytest
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric imp
```
- `python_import` `types` — symbol `types` — [source://app/backend/tests/test_supabase_auth.py#L5] — Provenance `prov:fdf7c32709a038a7` via `python_ast` confidence `deterministic` hash `62ccec601269`

Redacted source signal:

```text
import json
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import jwt
import pytest
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric imp
```
- `python_import` `pathlib` — symbol `pathlib` — [source://app/backend/tests/test_supabase_schema_hardening.py#L1] — Provenance `prov:5ae1ff23a83abc46` via `python_ast` confidence `deterministic` hash `c140ae9cfe55`
- `python_import` `database.base` — symbol `database.base` — [source://app/backend/tests/test_tenant_isolation_routes.py#L9] — Provenance `prov:dee3c8574458607e` via `python_ast` confidence `deterministic` hash `4ca736cecfad`
- `python_import` `database.models` — symbol `database.models` — [source://app/backend/tests/test_tenant_isolation_routes.py#L10] — Provenance `prov:14c2e43210dbdbdf` via `python_ast` confidence `deterministic` hash `4ca736cecfad`
- `python_import` `fastapi.testclient` — symbol `fastapi.testclient` — [source://app/backend/tests/test_tenant_isolation_routes.py#L4] — Provenance `prov:350f745db1cbf589` via `python_ast` confidence `deterministic` hash `4ca736cecfad`
- `python_import` `main` — symbol `main` — [source://app/backend/tests/test_tenant_isolation_routes.py#L11] — Provenance `prov:0627e82dae45c8f4` via `python_ast` confidence `deterministic` hash `4ca736cecfad`

### python_module

- `python_module` `app.backend.alembic.env` — symbol `app.backend.alembic.env` — [source://app/backend/alembic/env.py#L1] — Provenance `prov:dc3cd91b08e6bedb` via `python_ast` confidence `deterministic` hash `df239fcd8a00`
- `python_module` `app.backend.alembic.versions.0001_initial` — symbol `app.backend.alembic.versions.0001_initial` — [source://app/backend/alembic/versions/0001_initial.py#L1] — Provenance `prov:3419defabca5a76b` via `python_ast` confidence `deterministic` hash `b9a82ba6452a`
- `python_module` `app.backend.alembic.versions.0002_audit_event_organization_id` — symbol `app.backend.alembic.versions.0002_audit_event_organization_id` — [source://app/backend/alembic/versions/0002_audit_event_organization_id.py#L1] — Provenance `prov:47dd6808d6580490` via `python_ast` confidence `deterministic` hash `0077daca005a`
- `python_module` `app.backend.alembic.versions.0003_lock_down_supabase_public_table_grants` — symbol `app.backend.alembic.versions.0003_lock_down_supabase_public_table_grants` — [source://app/backend/alembic/versions/0003_lock_down_supabase_public_table_grants.py#L1] — Provenance `prov:bac221633a28403c` via `python_ast` confidence `deterministic` hash `f8d102a94cee`
- `python_module` `app.backend.alembic.versions.0004_cmmc_app_rls_policies` — symbol `app.backend.alembic.versions.0004_cmmc_app_rls_policies` — [source://app/backend/alembic/versions/0004_cmmc_app_rls_policies.py#L1] — Provenance `prov:bfba2b7f0e557160` via `python_ast` confidence `deterministic` hash `581de9538af5`
- `python_module` `app.backend.alembic.versions.0005_audit_events_append_only` — symbol `app.backend.alembic.versions.0005_audit_events_append_only` — [source://app/backend/alembic/versions/0005_audit_events_append_only.py#L1] — Provenance `prov:361e5a940f21cf25` via `python_ast` confidence `deterministic` hash `ab3203863f37`
- `python_module` `app.backend.alembic.versions.0006_auth_access_grants` — symbol `app.backend.alembic.versions.0006_auth_access_grants` — [source://app/backend/alembic/versions/0006_auth_access_grants.py#L1] — Provenance `prov:38e6ab9948b47f0c` via `python_ast` confidence `deterministic` hash `5c03e5e2eb9a`
- `python_module` `app.backend.src` — symbol `app.backend.src` — [source://app/backend/src/__init__.py#L1] — Provenance `prov:e22473c71b5811dc` via `python_ast` confidence `deterministic` hash `e3b0c44298fc`
- `python_module` `app.backend.src.api` — symbol `app.backend.src.api` — [source://app/backend/src/api/__init__.py#L1] — Provenance `prov:db833102e568082d` via `python_ast` confidence `deterministic` hash `e3b0c44298fc`
- `python_module` `app.backend.src.assessment` — symbol `app.backend.src.assessment` — [source://app/backend/src/assessment/__init__.py#L1] — Provenance `prov:3b45c63fcebb3826` via `python_ast` confidence `deterministic` hash `e3b0c44298fc`
- `python_module` `app.backend.src.assessment.confirmation` — symbol `app.backend.src.assessment.confirmation` — [source://app/backend/src/assessment/confirmation.py#L1] — Provenance `prov:7e0ff9b41c0b43a3` via `python_ast` confidence `deterministic` hash `4be7bcac76c0`
- `python_module` `app.backend.src.assessment.schemas` — symbol `app.backend.src.assessment.schemas` — [source://app/backend/src/assessment/schemas.py#L1] — Provenance `prov:44b4b4da672edc34` via `python_ast` confidence `deterministic` hash `711cffe52aae`

Redacted source signal:

```text
from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Annotated, Literal
from urllib.parse import parse_qsl, urlsplit
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator, model_validator


SENSITIVE_EXTERNAL_REFERENCE_QUERY_K
```
- `python_module` `app.backend.src.assessment.scope_parser` — symbol `app.backend.src.assessment.scope_parser` — [source://app/backend/src/assessment/scope_parser.py#L1] — Provenance `prov:aadcd804070ad44a` via `python_ast` confidence `deterministic` hash `ee57f4af7744`
- `python_module` `app.backend.src.assessment.state_machine` — symbol `app.backend.src.assessment.state_machine` — [source://app/backend/src/assessment/state_machine.py#L1] — Provenance `prov:9e31e5deaa293460` via `python_ast` confidence `deterministic` hash `e775d84f4f5b`
- `python_module` `app.backend.src.assessment.text_analysis` — symbol `app.backend.src.assessment.text_analysis` — [source://app/backend/src/assessment/text_analysis.py#L1] — Provenance `prov:361decb41f29f4b1` via `python_ast` confidence `deterministic` hash `bde2b7bcb7dc`
- `python_module` `app.backend.src.audit` — symbol `app.backend.src.audit` — [source://app/backend/src/audit/__init__.py#L1] — Provenance `prov:8ffd7b6050ea39b7` via `python_ast` confidence `deterministic` hash `e3b0c44298fc`
- `python_module` `app.backend.src.audit.events` — symbol `app.backend.src.audit.events` — [source://app/backend/src/audit/events.py#L1] — Provenance `prov:58b4c447b8803050` via `python_ast` confidence `deterministic` hash `f7f9a7793f84`
- `python_module` `app.backend.src.auth` — symbol `app.backend.src.auth` — [source://app/backend/src/auth/__init__.py#L1] — Provenance `prov:3646836f8a5b1552` via `python_ast` confidence `deterministic` hash `e3b0c44298fc`
- `python_module` `app.backend.src.auth.dependencies` — symbol `app.backend.src.auth.dependencies` — [source://app/backend/src/auth/dependencies.py#L1] — Provenance `prov:4230b3f9d25ad1f0` via `python_ast` confidence `deterministic` hash `d5edc52e827b`

Redacted source signal:

```text
from dataclasses import dataclass
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from config.settings import get_settings
from database.base import get_db
from database.models import AuthAccessGrant, Organization, User, AssessmentSession, now_utc
from audit.ev
```
- `python_module` `app.backend.src.auth.public_beta` — symbol `app.backend.src.auth.public_beta` — [source://app/backend/src/auth/public_beta.py#L1] — Provenance `prov:834ebec1631c5199` via `python_ast` confidence `deterministic` hash `77b86338d3da`

Redacted source signal:

```text
import base64
import hashlib
import hmac
import json
from dataclasses import dataclass


class PublicBetaTokenError(ValueError):
    pass


@dataclass(frozen=True)
class PublicBetaClaims:
    organization_id: str
    user_id: str
    email: str
    organization_name: str


def _b64encode(raw: bytes)
```
- `python_module` `app.backend.src.auth.supabase` — symbol `app.backend.src.auth.supabase` — [source://app/backend/src/auth/supabase.py#L1] — Provenance `prov:7a7149b233076c1a` via `python_ast` confidence `deterministic` hash `e5b0506670d2`

Redacted source signal:

```text
from dataclasses import dataclass
from functools import lru_cache
from ipaddress import ip_address
from socket import inet_aton
from urllib.parse import urlparse

import jwt
from jwt import PyJWKClient, PyJWTError


class SupabaseTokenError(ValueError):
    pass


@dataclass(frozen=True)
class Supab
```
- `python_module` `app.backend.src.config` — symbol `app.backend.src.config` — [source://app/backend/src/config/__init__.py#L1] — Provenance `prov:4a214e54ce20930b` via `python_ast` confidence `deterministic` hash `e3b0c44298fc`
- `python_module` `app.backend.src.config.settings` — symbol `app.backend.src.config.settings` — [source://app/backend/src/config/settings.py#L1] — Provenance `prov:c230b32cca5ce1c7` via `python_ast` confidence `deterministic` hash `a7f19740b398`

Redacted source signal:

```text
from functools import lru_cache
from ipaddress import ip_address
from socket import inet_aton
from urllib.parse import urlparse

from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigurationError(RuntimeError):
    pass


class Settings(BaseSettings):
    app_name: str = "CMMC
```
- `python_module` `app.backend.src.controls` — symbol `app.backend.src.controls` — [source://app/backend/src/controls/__init__.py#L1] — Provenance `prov:b9055d33abc8c621` via `python_ast` confidence `deterministic` hash `e3b0c44298fc`
- `python_module` `app.backend.src.controls.library` — symbol `app.backend.src.controls.library` — [source://app/backend/src/controls/library.py#L1] — Provenance `prov:9f1142d6d5b3aaac` via `python_ast` confidence `deterministic` hash `611f90f5e7eb`
- `python_module` `app.backend.src.controls.seed` — symbol `app.backend.src.controls.seed` — [source://app/backend/src/controls/seed.py#L1] — Provenance `prov:c4db4eba24b8267c` via `python_ast` confidence `deterministic` hash `ded57d70dafb`
- `python_module` `app.backend.src.database` — symbol `app.backend.src.database` — [source://app/backend/src/database/__init__.py#L1] — Provenance `prov:3f7ff035549a670f` via `python_ast` confidence `deterministic` hash `e3b0c44298fc`
- `python_module` `app.backend.src.database.base` — symbol `app.backend.src.database.base` — [source://app/backend/src/database/base.py#L1] — Provenance `prov:dca1bc97c5521505` via `python_ast` confidence `deterministic` hash `17ab4e8d2bd7`
- `python_module` `app.backend.src.database.models` — symbol `app.backend.src.database.models` — [source://app/backend/src/database/models.py#L1] — Provenance `prov:ab4dd2f0a3ed2d39` via `python_ast` confidence `deterministic` hash `fcb520456941`
- `python_module` `app.backend.src.evidence` — symbol `app.backend.src.evidence` — [source://app/backend/src/evidence/__init__.py#L1] — Provenance `prov:c132423fca6c5ea3` via `python_ast` confidence `deterministic` hash `e3b0c44298fc`
- `python_module` `app.backend.src.llm` — symbol `app.backend.src.llm` — [source://app/backend/src/llm/__init__.py#L1] — Provenance `prov:4d8952ad533a85b0` via `python_ast` confidence `deterministic` hash `e3b0c44298fc`
- `python_module` `app.backend.src.llm.client` — symbol `app.backend.src.llm.client` — [source://app/backend/src/llm/client.py#L1] — Provenance `prov:aad4db59631a972d` via `python_ast` confidence `deterministic` hash `31ae98c2afd4`

Redacted source signal:

```text
import json
import logging
from time import perf_counter
from abc import ABC, abstractmethod

import httpx

from assessment.schemas import FindingStatus, LLMAnswerEvaluation
from assessment.text_analysis import classify_stub_answer, extract_evidence_references
from config.settings import get_setting
```
- `python_module` `app.backend.src.llm.data_boundary` — symbol `app.backend.src.llm.data_boundary` — [source://app/backend/src/llm/data_boundary.py#L1] — Provenance `prov:56057a9d7db07d1a` via `python_ast` confidence `deterministic` hash `804f9a44dec1`
- `python_module` `app.backend.src.llm.policy` — symbol `app.backend.src.llm.policy` — [source://app/backend/src/llm/policy.py#L1] — Provenance `prov:838cdd24e0c0ba78` via `python_ast` confidence `deterministic` hash `0351fa64b528`
- `python_module` `app.backend.src.llm.schemas` — symbol `app.backend.src.llm.schemas` — [source://app/backend/src/llm/schemas.py#L1] — Provenance `prov:9ef3461850c91d0d` via `python_ast` confidence `deterministic` hash `797672e10df9`
- `python_module` `app.backend.src.main` — symbol `app.backend.src.main` — [source://app/backend/src/main.py#L1] — Provenance `prov:7e09975083c7abc4` via `python_ast` confidence `deterministic` hash `5a10ae600ecc`
- `python_module` `app.backend.src.reports` — symbol `app.backend.src.reports` — [source://app/backend/src/reports/__init__.py#L1] — Provenance `prov:92d607b784f53207` via `python_ast` confidence `deterministic` hash `e3b0c44298fc`
- `python_module` `app.backend.src.reports.generator` — symbol `app.backend.src.reports.generator` — [source://app/backend/src/reports/generator.py#L1] — Provenance `prov:4ac1bd98d30ed60b` via `python_ast` confidence `deterministic` hash `f7e929ccdd20`
- `python_module` `app.backend.src.reports.readiness` — symbol `app.backend.src.reports.readiness` — [source://app/backend/src/reports/readiness.py#L1] — Provenance `prov:5ffc40018c3bb956` via `python_ast` confidence `deterministic` hash `321de5e54dc9`
- `python_module` `app.backend.src.security` — symbol `app.backend.src.security` — [source://app/backend/src/security/__init__.py#L1] — Provenance `prov:14d39377c3a519dd` via `python_ast` confidence `deterministic` hash `e3b0c44298fc`
- `python_module` `app.backend.src.security.information_boundary` — symbol `app.backend.src.security.information_boundary` — [source://app/backend/src/security/information_boundary.py#L1] — Provenance `prov:758bed5176ac336f` via `python_ast` confidence `deterministic` hash `8bdcd77295de`
- `python_module` `app.backend.src.security.language` — symbol `app.backend.src.security.language` — [source://app/backend/src/security/language.py#L1] — Provenance `prov:c4f5208237bc79b0` via `python_ast` confidence `deterministic` hash `decb66545081`
- `python_module` `app.backend.src.security.prompt_injection` — symbol `app.backend.src.security.prompt_injection` — [source://app/backend/src/security/prompt_injection.py#L1] — Provenance `prov:e5d09e8854a5dabd` via `python_ast` confidence `deterministic` hash `7788ec023a36`

Redacted source signal:

```text
import re

BLOCKED_PATTERNS = [
    re.compile(r"\bignore\s+(?:all\s+)?(?:previous|prior)\s+instructions\b", re.I),
    re.compile(r"\bdisregard\s+(?:the\s+)?(?:rules|instructions)\b", re.I),
    re.compile(r"\bskip\s+(?:the\s+)?(?:rest|remaining\s+controls|controls)\b", re.I),
    re.compile(r"\bma
```
- `python_module` `app.backend.src.testing.db_safety` — symbol `app.backend.src.testing.db_safety` — [source://app/backend/src/testing/db_safety.py#L1] — Provenance `prov:53d98160ac529e58` via `python_ast` confidence `deterministic` hash `32e1b5615896`
- `python_module` `app.backend.tests.conftest` — symbol `app.backend.tests.conftest` — [source://app/backend/tests/conftest.py#L1] — Provenance `prov:bababdb3964ac559` via `python_ast` confidence `deterministic` hash `19d2248048a7`
- `python_module` `app.backend.tests.test_alembic_env_database_url` — symbol `app.backend.tests.test_alembic_env_database_url` — [source://app/backend/tests/test_alembic_env_database_url.py#L1] — Provenance `prov:719fe678eb646360` via `python_ast` confidence `deterministic` hash `0dd10d9cc3c3`
- `python_module` `app.backend.tests.test_audit_security_rejections` — symbol `app.backend.tests.test_audit_security_rejections` — [source://app/backend/tests/test_audit_security_rejections.py#L1] — Provenance `prov:ff056d6a234503fe` via `python_ast` confidence `deterministic` hash `5baa38dc0082`
- `python_module` `app.backend.tests.test_auth_access_grants_schema` — symbol `app.backend.tests.test_auth_access_grants_schema` — [source://app/backend/tests/test_auth_access_grants_schema.py#L1] — Provenance `prov:b13d164eef159d79` via `python_ast` confidence `deterministic` hash `ee84eb0fdcbd`
- `python_module` `app.backend.tests.test_auth_boundaries` — symbol `app.backend.tests.test_auth_boundaries` — [source://app/backend/tests/test_auth_boundaries.py#L1] — Provenance `prov:8e33f943bb893860` via `python_ast` confidence `deterministic` hash `42e4fee3feda`

Redacted source signal:

```text
import os
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["CONTROL_LIBRARY_PATH"] = "../../control-library/cmmc_level_1_controls.json"

from config.settings import ConfigurationError, Settings, v
```
- `python_module` `app.backend.tests.test_browser_persona_qa_regressions` — symbol `app.backend.tests.test_browser_persona_qa_regressions` — [source://app/backend/tests/test_browser_persona_qa_regressions.py#L1] — Provenance `prov:2ed7de874a248028` via `python_ast` confidence `deterministic` hash `9e566b1d543f`
- `python_module` `app.backend.tests.test_browser_persona_qa_remediation` — symbol `app.backend.tests.test_browser_persona_qa_remediation` — [source://app/backend/tests/test_browser_persona_qa_remediation.py#L1] — Provenance `prov:458d9579540afe87` via `python_ast` confidence `deterministic` hash `c7d7b4cb2f9b`
- `python_module` `app.backend.tests.test_confirmation_na_hardening` — symbol `app.backend.tests.test_confirmation_na_hardening` — [source://app/backend/tests/test_confirmation_na_hardening.py#L1] — Provenance `prov:016644203cf0e8f5` via `python_ast` confidence `deterministic` hash `f8a5cff3d238`
- `python_module` `app.backend.tests.test_evidence_boundaries` — symbol `app.backend.tests.test_evidence_boundaries` — [source://app/backend/tests/test_evidence_boundaries.py#L1] — Provenance `prov:24f78088343661b9` via `python_ast` confidence `deterministic` hash `25fc2b2dea4b`

Redacted source signal:

```text
import os

import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["CONTROL_LIBRARY_PATH"] = "../../control-library/cmmc_level_1_controls.json"

from database.base import Base, engine
from main import app




@pytest.fixture
def client():
```
- `python_module` `app.backend.tests.test_evidence_lifecycle` — symbol `app.backend.tests.test_evidence_lifecycle` — [source://app/backend/tests/test_evidence_lifecycle.py#L1] — Provenance `prov:0cbb78f0ceeb1668` via `python_ast` confidence `deterministic` hash `2f061cf6d7a4`
- `python_module` `app.backend.tests.test_full_assessment_flow` — symbol `app.backend.tests.test_full_assessment_flow` — [source://app/backend/tests/test_full_assessment_flow.py#L1] — Provenance `prov:9f59fb42a22d7c1c` via `python_ast` confidence `deterministic` hash `6f38b3391c38`
- `python_module` `app.backend.tests.test_health` — symbol `app.backend.tests.test_health` — [source://app/backend/tests/test_health.py#L1] — Provenance `prov:37c7f2a82d25795a` via `python_ast` confidence `deterministic` hash `68b71454bc84`
- `python_module` `app.backend.tests.test_information_boundary` — symbol `app.backend.tests.test_information_boundary` — [source://app/backend/tests/test_information_boundary.py#L1] — Provenance `prov:b05380c337b3e2bd` via `python_ast` confidence `deterministic` hash `8bb3322799b1`
- `python_module` `app.backend.tests.test_issue_9_report_pdf_smoke` — symbol `app.backend.tests.test_issue_9_report_pdf_smoke` — [source://app/backend/tests/test_issue_9_report_pdf_smoke.py#L1] — Provenance `prov:5af240413f69d713` via `python_ast` confidence `deterministic` hash `995ec2fe1cf2`
- `python_module` `app.backend.tests.test_llm_assisted_interview` — symbol `app.backend.tests.test_llm_assisted_interview` — [source://app/backend/tests/test_llm_assisted_interview.py#L1] — Provenance `prov:ecc08088abe26dd0` via `python_ast` confidence `deterministic` hash `16c46f705d11`
- `python_module` `app.backend.tests.test_llm_input_boundary_all_sources` — symbol `app.backend.tests.test_llm_input_boundary_all_sources` — [source://app/backend/tests/test_llm_input_boundary_all_sources.py#L1] — Provenance `prov:a1160e72876adea5` via `python_ast` confidence `deterministic` hash `0579233dd66e`

Redacted source signal:

```text
import pytest
from fastapi.testclient import TestClient

from controls.library import get_control
from database.base import SessionLocal
from database.models import (
    AssessmentMessage,
    AssessmentSession,
    AuditEvent,
    ControlFinding,
    EvidenceReference,
    GeneratedReport,
    Org
```
- `python_module` `app.backend.tests.test_llm_policy` — symbol `app.backend.tests.test_llm_policy` — [source://app/backend/tests/test_llm_policy.py#L1] — Provenance `prov:d3d7e9c44b68acbb` via `python_ast` confidence `deterministic` hash `4d6c8d1f7338`

Redacted source signal:

```text
import pytest

from assessment.schemas import FindingStatus, LLMAnswerEvaluation


def fallback_evaluation():
    return LLMAnswerEvaluation(
        answer_summary="fallback",
        sufficiency="ambiguous",
        proposed_status=FindingStatus.UNKNOWN,
        rationale="Fallback used because th
```
- `python_module` `app.backend.tests.test_llm_provider_config` — symbol `app.backend.tests.test_llm_provider_config` — [source://app/backend/tests/test_llm_provider_config.py#L1] — Provenance `prov:82c7e1ddc0811a7a` via `python_ast` confidence `deterministic` hash `099e306e55ea`
- `python_module` `app.backend.tests.test_mvp` — symbol `app.backend.tests.test_mvp` — [source://app/backend/tests/test_mvp.py#L1] — Provenance `prov:a1612a11f7b67df7` via `python_ast` confidence `deterministic` hash `92b287dea155`
- `python_module` `app.backend.tests.test_opus_browser_findings` — symbol `app.backend.tests.test_opus_browser_findings` — [source://app/backend/tests/test_opus_browser_findings.py#L1] — Provenance `prov:2b3b08c0b66f59b8` via `python_ast` confidence `deterministic` hash `655835aa996c`
- `python_module` `app.backend.tests.test_public_beta_auth` — symbol `app.backend.tests.test_public_beta_auth` — [source://app/backend/tests/test_public_beta_auth.py#L1] — Provenance `prov:d51729e19c2080c6` via `python_ast` confidence `deterministic` hash `ce4b691a2cdf`

Redacted source signal:

```text
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from auth.public_beta import PublicBetaTokenError, sign_public_beta_token, verify_public_beta_token
from database.base import Base, engine, SessionLocal
from database.models import Organization, User
from mai
```
- `python_module` `app.backend.tests.test_red_team_hardening` — symbol `app.backend.tests.test_red_team_hardening` — [source://app/backend/tests/test_red_team_hardening.py#L1] — Provenance `prov:5fc0ba438414d9ee` via `python_ast` confidence `deterministic` hash `b3e85247912f`

Redacted source signal:

```text
import os
import importlib

import pytest
from fastapi.testclient import TestClient

from assessment.schemas import FindingStatus
from assessment.scope_parser import parse_scope
from assessment.text_analysis import extract_evidence_references, classify_stub_answer
from assessment.state_machine impor
```
- `python_module` `app.backend.tests.test_report_eligibility` — symbol `app.backend.tests.test_report_eligibility` — [source://app/backend/tests/test_report_eligibility.py#L1] — Provenance `prov:7d36193f0768685e` via `python_ast` confidence `deterministic` hash `54516c5a1777`
- `python_module` `app.backend.tests.test_report_pdf` — symbol `app.backend.tests.test_report_pdf` — [source://app/backend/tests/test_report_pdf.py#L1] — Provenance `prov:6eb6843b4491be5a` via `python_ast` confidence `deterministic` hash `186ed4c8ff4c`
- `python_module` `app.backend.tests.test_report_quality` — symbol `app.backend.tests.test_report_quality` — [source://app/backend/tests/test_report_quality.py#L1] — Provenance `prov:77caace91d513857` via `python_ast` confidence `deterministic` hash `e733011b7126`
- `python_module` `app.backend.tests.test_reported_feedback_regressions` — symbol `app.backend.tests.test_reported_feedback_regressions` — [source://app/backend/tests/test_reported_feedback_regressions.py#L1] — Provenance `prov:5bc783524aeb963e` via `python_ast` confidence `deterministic` hash `48fe759a9bce`
- `python_module` `app.backend.tests.test_scope_parser_quality` — symbol `app.backend.tests.test_scope_parser_quality` — [source://app/backend/tests/test_scope_parser_quality.py#L1] — Provenance `prov:f564bf7624b118df` via `python_ast` confidence `deterministic` hash `b44c50b832e6`
- `python_module` `app.backend.tests.test_scope_unknowns` — symbol `app.backend.tests.test_scope_unknowns` — [source://app/backend/tests/test_scope_unknowns.py#L1] — Provenance `prov:b5d9b80a2ffb1529` via `python_ast` confidence `deterministic` hash `c390511423d8`
- `python_module` `app.backend.tests.test_session_resume` — symbol `app.backend.tests.test_session_resume` — [source://app/backend/tests/test_session_resume.py#L1] — Provenance `prov:b314f8f1e1174252` via `python_ast` confidence `deterministic` hash `c39a9073fb24`
- `python_module` `app.backend.tests.test_startup_config` — symbol `app.backend.tests.test_startup_config` — [source://app/backend/tests/test_startup_config.py#L1] — Provenance `prov:29e0a803f84f2fee` via `python_ast` confidence `deterministic` hash `da418c28c50f`

Redacted source signal:

```text
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

from config.settings import ConfigurationError, Settings, validate_production_auth_configuration, validate_production_settings
from main import (
    alembic_head_revis
```
- `python_module` `app.backend.tests.test_supabase_app_role_policies` — symbol `app.backend.tests.test_supabase_app_role_policies` — [source://app/backend/tests/test_supabase_app_role_policies.py#L1] — Provenance `prov:024dae3aab1b0c2b` via `python_ast` confidence `deterministic` hash `ff2bb1b7e61a`
- `python_module` `app.backend.tests.test_supabase_audit_append_only` — symbol `app.backend.tests.test_supabase_audit_append_only` — [source://app/backend/tests/test_supabase_audit_append_only.py#L1] — Provenance `prov:f9ce828a865f6da2` via `python_ast` confidence `deterministic` hash `d4acbce00237`
- `python_module` `app.backend.tests.test_supabase_auth` — symbol `app.backend.tests.test_supabase_auth` — [source://app/backend/tests/test_supabase_auth.py#L1] — Provenance `prov:2a14c2ab2313a924` via `python_ast` confidence `deterministic` hash `62ccec601269`

Redacted source signal:

```text
import json
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import jwt
import pytest
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric imp
```
- `python_module` `app.backend.tests.test_supabase_schema_hardening` — symbol `app.backend.tests.test_supabase_schema_hardening` — [source://app/backend/tests/test_supabase_schema_hardening.py#L1] — Provenance `prov:d0952770ec375433` via `python_ast` confidence `deterministic` hash `c140ae9cfe55`
- `python_module` `app.backend.tests.test_tenant_isolation_routes` — symbol `app.backend.tests.test_tenant_isolation_routes` — [source://app/backend/tests/test_tenant_isolation_routes.py#L1] — Provenance `prov:f8b5edd94622972e` via `python_ast` confidence `deterministic` hash `4ca736cecfad`
- `python_module` `app.backend.tests.test_test_database_safety` — symbol `app.backend.tests.test_test_database_safety` — [source://app/backend/tests/test_test_database_safety.py#L1] — Provenance `prov:b309b19863d3ce83` via `python_ast` confidence `deterministic` hash `65c5b2e84428`

### test_file

- `test_file` `app/backend/tests/test_alembic_env_database_url.py` — [source://app/backend/tests/test_alembic_env_database_url.py#L1] — Provenance `prov:86ae214132475d7c` via `filesystem` confidence `deterministic` hash `0dd10d9cc3c3`
- `test_file` `app/backend/tests/test_audit_security_rejections.py` — [source://app/backend/tests/test_audit_security_rejections.py#L1] — Provenance `prov:c75d3072d10f5dfa` via `filesystem` confidence `deterministic` hash `5baa38dc0082`
- `test_file` `app/backend/tests/test_auth_access_grants_schema.py` — [source://app/backend/tests/test_auth_access_grants_schema.py#L1] — Provenance `prov:06ed8a6b9634acc8` via `filesystem` confidence `deterministic` hash `ee84eb0fdcbd`
- `test_file` `app/backend/tests/test_auth_boundaries.py` — [source://app/backend/tests/test_auth_boundaries.py#L1] — Provenance `prov:61c8719e9dccc319` via `filesystem` confidence `deterministic` hash `42e4fee3feda`

Redacted source signal:

```text
import os
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["CONTROL_LIBRARY_PATH"] = "../../control-library/cmmc_level_1_controls.json"

from config.settings import ConfigurationError, Settings, v
```
- `test_file` `app/backend/tests/test_browser_persona_qa_regressions.py` — [source://app/backend/tests/test_browser_persona_qa_regressions.py#L1] — Provenance `prov:dcecb84fc4753330` via `filesystem` confidence `deterministic` hash `9e566b1d543f`
- `test_file` `app/backend/tests/test_browser_persona_qa_remediation.py` — [source://app/backend/tests/test_browser_persona_qa_remediation.py#L1] — Provenance `prov:c2be0d591377ff99` via `filesystem` confidence `deterministic` hash `c7d7b4cb2f9b`
- `test_file` `app/backend/tests/test_confirmation_na_hardening.py` — [source://app/backend/tests/test_confirmation_na_hardening.py#L1] — Provenance `prov:bc94009053fd57bd` via `filesystem` confidence `deterministic` hash `f8a5cff3d238`
- `test_file` `app/backend/tests/test_evidence_boundaries.py` — [source://app/backend/tests/test_evidence_boundaries.py#L1] — Provenance `prov:fa0c97cbcd32a884` via `filesystem` confidence `deterministic` hash `25fc2b2dea4b`

Redacted source signal:

```text
import os

import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["CONTROL_LIBRARY_PATH"] = "../../control-library/cmmc_level_1_controls.json"

from database.base import Base, engine
from main import app




@pytest.fixture
def client():
```
- `test_file` `app/backend/tests/test_evidence_lifecycle.py` — [source://app/backend/tests/test_evidence_lifecycle.py#L1] — Provenance `prov:29f811cbb8d11c37` via `filesystem` confidence `deterministic` hash `2f061cf6d7a4`
- `test_file` `app/backend/tests/test_full_assessment_flow.py` — [source://app/backend/tests/test_full_assessment_flow.py#L1] — Provenance `prov:27217caa8b77976b` via `filesystem` confidence `deterministic` hash `6f38b3391c38`
- `test_file` `app/backend/tests/test_health.py` — [source://app/backend/tests/test_health.py#L1] — Provenance `prov:27d3629ac8e6fa2e` via `filesystem` confidence `deterministic` hash `68b71454bc84`
- `test_file` `app/backend/tests/test_information_boundary.py` — [source://app/backend/tests/test_information_boundary.py#L1] — Provenance `prov:549f9cee7780b77d` via `filesystem` confidence `deterministic` hash `8bb3322799b1`
- `test_file` `app/backend/tests/test_issue_9_report_pdf_smoke.py` — [source://app/backend/tests/test_issue_9_report_pdf_smoke.py#L1] — Provenance `prov:86e6594af640a078` via `filesystem` confidence `deterministic` hash `995ec2fe1cf2`
- `test_file` `app/backend/tests/test_llm_assisted_interview.py` — [source://app/backend/tests/test_llm_assisted_interview.py#L1] — Provenance `prov:c6644f2963226b6a` via `filesystem` confidence `deterministic` hash `16c46f705d11`
- `test_file` `app/backend/tests/test_llm_input_boundary_all_sources.py` — [source://app/backend/tests/test_llm_input_boundary_all_sources.py#L1] — Provenance `prov:fffb4b3b67723d38` via `filesystem` confidence `deterministic` hash `0579233dd66e`

Redacted source signal:

```text
import pytest
from fastapi.testclient import TestClient

from controls.library import get_control
from database.base import SessionLocal
from database.models import (
    AssessmentMessage,
    AssessmentSession,
    AuditEvent,
    ControlFinding,
    EvidenceReference,
    GeneratedReport,
    Org
```
- `test_file` `app/backend/tests/test_llm_policy.py` — [source://app/backend/tests/test_llm_policy.py#L1] — Provenance `prov:397a1f0b322a34fa` via `filesystem` confidence `deterministic` hash `4d6c8d1f7338`

Redacted source signal:

```text
import pytest

from assessment.schemas import FindingStatus, LLMAnswerEvaluation


def fallback_evaluation():
    return LLMAnswerEvaluation(
        answer_summary="fallback",
        sufficiency="ambiguous",
        proposed_status=FindingStatus.UNKNOWN,
        rationale="Fallback used because th
```
- `test_file` `app/backend/tests/test_llm_provider_config.py` — [source://app/backend/tests/test_llm_provider_config.py#L1] — Provenance `prov:6786de6affbbe944` via `filesystem` confidence `deterministic` hash `099e306e55ea`
- `test_file` `app/backend/tests/test_mvp.py` — [source://app/backend/tests/test_mvp.py#L1] — Provenance `prov:f9e13efa0363a005` via `filesystem` confidence `deterministic` hash `92b287dea155`
- `test_file` `app/backend/tests/test_opus_browser_findings.py` — [source://app/backend/tests/test_opus_browser_findings.py#L1] — Provenance `prov:353d48ee052db387` via `filesystem` confidence `deterministic` hash `655835aa996c`
- `test_file` `app/backend/tests/test_public_beta_auth.py` — [source://app/backend/tests/test_public_beta_auth.py#L1] — Provenance `prov:00f24903fd3d064f` via `filesystem` confidence `deterministic` hash `ce4b691a2cdf`

Redacted source signal:

```text
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from auth.public_beta import PublicBetaTokenError, sign_public_beta_token, verify_public_beta_token
from database.base import Base, engine, SessionLocal
from database.models import Organization, User
from mai
```
- `test_file` `app/backend/tests/test_red_team_hardening.py` — [source://app/backend/tests/test_red_team_hardening.py#L1] — Provenance `prov:df5be5f57107c7af` via `filesystem` confidence `deterministic` hash `b3e85247912f`

Redacted source signal:

```text
import os
import importlib

import pytest
from fastapi.testclient import TestClient

from assessment.schemas import FindingStatus
from assessment.scope_parser import parse_scope
from assessment.text_analysis import extract_evidence_references, classify_stub_answer
from assessment.state_machine impor
```
- `test_file` `app/backend/tests/test_report_eligibility.py` — [source://app/backend/tests/test_report_eligibility.py#L1] — Provenance `prov:0818c3ca33f8ce52` via `filesystem` confidence `deterministic` hash `54516c5a1777`
- `test_file` `app/backend/tests/test_report_pdf.py` — [source://app/backend/tests/test_report_pdf.py#L1] — Provenance `prov:c3add5ba0c891f3b` via `filesystem` confidence `deterministic` hash `186ed4c8ff4c`
- `test_file` `app/backend/tests/test_report_quality.py` — [source://app/backend/tests/test_report_quality.py#L1] — Provenance `prov:8d9e357139dbc70f` via `filesystem` confidence `deterministic` hash `e733011b7126`
- `test_file` `app/backend/tests/test_reported_feedback_regressions.py` — [source://app/backend/tests/test_reported_feedback_regressions.py#L1] — Provenance `prov:c15eb24ad833aed6` via `filesystem` confidence `deterministic` hash `48fe759a9bce`
- `test_file` `app/backend/tests/test_scope_parser_quality.py` — [source://app/backend/tests/test_scope_parser_quality.py#L1] — Provenance `prov:718b4471fa79bc5e` via `filesystem` confidence `deterministic` hash `b44c50b832e6`
- `test_file` `app/backend/tests/test_scope_unknowns.py` — [source://app/backend/tests/test_scope_unknowns.py#L1] — Provenance `prov:35c6ad0b34b211d1` via `filesystem` confidence `deterministic` hash `c390511423d8`
- `test_file` `app/backend/tests/test_session_resume.py` — [source://app/backend/tests/test_session_resume.py#L1] — Provenance `prov:cd2a3a99edafb273` via `filesystem` confidence `deterministic` hash `c39a9073fb24`
- `test_file` `app/backend/tests/test_startup_config.py` — [source://app/backend/tests/test_startup_config.py#L1] — Provenance `prov:5607337954e16ca5` via `filesystem` confidence `deterministic` hash `da418c28c50f`

Redacted source signal:

```text
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

from config.settings import ConfigurationError, Settings, validate_production_auth_configuration, validate_production_settings
from main import (
    alembic_head_revis
```
- `test_file` `app/backend/tests/test_supabase_app_role_policies.py` — [source://app/backend/tests/test_supabase_app_role_policies.py#L1] — Provenance `prov:c569470f4422ae11` via `filesystem` confidence `deterministic` hash `ff2bb1b7e61a`
- `test_file` `app/backend/tests/test_supabase_audit_append_only.py` — [source://app/backend/tests/test_supabase_audit_append_only.py#L1] — Provenance `prov:567d896fa3923dfc` via `filesystem` confidence `deterministic` hash `d4acbce00237`
- `test_file` `app/backend/tests/test_supabase_auth.py` — [source://app/backend/tests/test_supabase_auth.py#L1] — Provenance `prov:f9db2bd5f11b5c26` via `filesystem` confidence `deterministic` hash `62ccec601269`

Redacted source signal:

```text
import json
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import jwt
import pytest
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric imp
```
- `test_file` `app/backend/tests/test_supabase_schema_hardening.py` — [source://app/backend/tests/test_supabase_schema_hardening.py#L1] — Provenance `prov:f1ced770171171f5` via `filesystem` confidence `deterministic` hash `c140ae9cfe55`
- `test_file` `app/backend/tests/test_tenant_isolation_routes.py` — [source://app/backend/tests/test_tenant_isolation_routes.py#L1] — Provenance `prov:77d76e7f765f1503` via `filesystem` confidence `deterministic` hash `4ca736cecfad`
- `test_file` `app/backend/tests/test_test_database_safety.py` — [source://app/backend/tests/test_test_database_safety.py#L1] — Provenance `prov:566a55812bb406d6` via `filesystem` confidence `deterministic` hash `65c5b2e84428`

### verification_artifact

- `verification_artifact` `docs/verification/2026-04-30-adversarial-scope-fixes-delegation-prompt.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-04-30-adversarial-scope-fixes-delegation-prompt.md#L1] — Provenance `prov:276baf27dc8ac2e4` via `filesystem` confidence `deterministic` hash `495d39741a41`
- `verification_artifact` `docs/verification/2026-04-30-baseline-diffstat.txt` — tags `excluded_from_primary_context` — [source://docs/verification/2026-04-30-baseline-diffstat.txt#L1] — Provenance `prov:aa48da7c535d2064` via `filesystem` confidence `deterministic` hash `b3138c5acd8b`
- `verification_artifact` `docs/verification/2026-04-30-baseline-status.txt` — tags `excluded_from_primary_context` — [source://docs/verification/2026-04-30-baseline-status.txt#L1] — Provenance `prov:b4b19062d63640c8` via `filesystem` confidence `deterministic` hash `02dec44f85e7`
- `verification_artifact` `docs/verification/2026-05-01-adversarial-remediation-verification.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-01-adversarial-remediation-verification.md#L1] — Provenance `prov:d9b4f3245c631d6e` via `filesystem` confidence `deterministic` hash `2d509e2df1cf`
- `verification_artifact` `docs/verification/2026-05-01-cloudflare-deployment-prep-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-01-cloudflare-deployment-prep-status.md#L1] — Provenance `prov:d22d2e4c4de0be89` via `filesystem` confidence `deterministic` hash `3d09484a1d7f`
- `verification_artifact` `docs/verification/2026-05-01-maintenance-plan-update-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-01-maintenance-plan-update-status.md#L1] — Provenance `prov:b43a7dec137f0835` via `filesystem` confidence `deterministic` hash `79ebe5aaafaa`
- `verification_artifact` `docs/verification/2026-05-01-new-assessment-startup-migration-bugfix.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-01-new-assessment-startup-migration-bugfix.md#L1] — Provenance `prov:9d9bdf3c8c35516c` via `filesystem` confidence `deterministic` hash `70ce9b2e8098`
- `verification_artifact` `docs/verification/2026-05-01-opus-maintenance-plan-review.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-01-opus-maintenance-plan-review.md#L1] — Provenance `prov:d5a93bb035fb9030` via `filesystem` confidence `deterministic` hash `b2df6d2ed2b5`
- `verification_artifact` `docs/verification/2026-05-01-pre-cleanup-diffstat.txt` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-01-pre-cleanup-diffstat.txt#L1] — Provenance `prov:c9ede039071b5530` via `filesystem` confidence `deterministic` hash `897cb55e13e1`
- `verification_artifact` `docs/verification/2026-05-01-pre-cleanup-status.txt` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-01-pre-cleanup-status.txt#L1] — Provenance `prov:8c6aae95fd558fbc` via `filesystem` confidence `deterministic` hash `4206e2a83265`
- `verification_artifact` `docs/verification/2026-05-01-pre-cleanup-untracked.txt` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-01-pre-cleanup-untracked.txt#L1] — Provenance `prov:bc1af08e4c4426e2` via `filesystem` confidence `deterministic` hash `a375a66bbaee`
- `verification_artifact` `docs/verification/2026-05-01-prod-readiness-source-diff.patch` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-01-prod-readiness-source-diff.patch#L1] — Provenance `prov:1d751adb97b7fe23` via `filesystem` confidence `deterministic` hash `6dcee7b3acb1`

Redacted source signal:

```text
diff --git a/app/backend/src/audit/events.py b/app/backend/src/audit/events.py
index 8ab0f47..e069d36 100644
--- a/app/backend/src/audit/events.py
+++ b/app/backend/src/audit/events.py
@@ -1,10 +1,36 @@
 from sqlalchemy.orm import Session
+
 from database.models import AuditEvent
 from security.prom
```
- `verification_artifact` `docs/verification/2026-05-01-workflow-ui-source-diff.patch` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-01-workflow-ui-source-diff.patch#L1] — Provenance `prov:d13cf6fa336eb1b4` via `filesystem` confidence `deterministic` hash `93258a92e652`
- `verification_artifact` `docs/verification/2026-05-03-autonomous-phase-4-task-1-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-03-autonomous-phase-4-task-1-status.md#L1] — Provenance `prov:8d94831419a7f63a` via `filesystem` confidence `deterministic` hash `51abfdcb8288`

Redacted source signal:

```text
# Autonomous Production Readiness Status — Phase 4.1

Date: 2026-05-03
Repository: `/home/leonb/projects/cmmc-level1-readiness-assistant`

## Scope selected

Selected **Phase 4.1: full 15-control completion/report-generation regression and report-language hardening** because Phase 0 through Phase 3
```
- `verification_artifact` `docs/verification/2026-05-03-autonomous-phase-4-task-2-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-03-autonomous-phase-4-task-2-status.md#L1] — Provenance `prov:abf2b0f69b6c4ea4` via `filesystem` confidence `deterministic` hash `d9a0fea18adb`

Redacted source signal:

```text
# Autonomous Production Readiness Status — Phase 4.2

Date: 2026-05-03
Repository: `/home/leonb/projects/cmmc-level1-readiness-assistant`

## Scope selected

Selected **Phase 4.2: session resume regression coverage** because:

- The primary plan lists Phase 4 after completed Phases 0–3.
- `docs/veri
```
- `verification_artifact` `docs/verification/2026-05-04-autonomous-phase-4-5-task-1-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-04-autonomous-phase-4-5-task-1-status.md#L1] — Provenance `prov:1bd4188dc80832e1` via `filesystem` confidence `deterministic` hash `db184e0611b2`

Redacted source signal:

```text
# Autonomous Production Readiness Status — Phase 4.5.1

Date: 2026-05-04T04:59:22Z
Repository: `/home/leonb/projects/cmmc-level1-readiness-assistant`

## Scope selected

Selected **Phase 4.5.1: evidence endpoint boundary tests** because:

- Phase 4.1 and Phase 4.2 already have durable completion art
```
- `verification_artifact` `docs/verification/2026-05-04-autonomous-phase-4-5-task-2-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-04-autonomous-phase-4-5-task-2-status.md#L1] — Provenance `prov:90592da5bba577f0` via `filesystem` confidence `deterministic` hash `bfc1bb3dc35f`

Redacted source signal:

```text
# Autonomous Production Readiness Status — Phase 4.5.2

Date: 2026-05-04
Repository: `/home/leonb/projects/cmmc-level1-readiness-assistant`

## Scope selected

Selected **Phase 4.5.2: report PDF endpoint smoke/fallback tests** because:

- Phase 4.1 and Phase 4.2 have durable completion artifacts.
-
```
- `verification_artifact` `docs/verification/2026-05-04-autonomous-phase-5-task-1-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-04-autonomous-phase-5-task-1-status.md#L1] — Provenance `prov:96ad573c7ea18c11` via `filesystem` confidence `deterministic` hash `b72ebd4aa6cb`

Redacted source signal:

```text
# Autonomous Production Readiness Status — Phase 5.1

Date: 2026-05-04T06:46:12Z
Repository: `/home/leonb/projects/cmmc-level1-readiness-assistant`

## Scope selected

Selected **Phase 5.1: scope parser deduplication tests** because:

- Phase 4.1 and Phase 4.2 have durable completion artifacts.
- Ph
```
- `verification_artifact` `docs/verification/2026-05-04-autonomous-phase-5-task-2-follow-up-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-04-autonomous-phase-5-task-2-follow-up-status.md#L1] — Provenance `prov:8c6c88afee433562` via `filesystem` confidence `deterministic` hash `ecc095ca06aa`

Redacted source signal:

```text
# Autonomous Phase 5 Task 2 Follow-up Status — Coordinated Negation Parser/Report Quality

Date: 2026-05-04
Repository: `/home/leonb/projects/cmmc-level1-readiness-assistant`

## Selected task

Phase 5.2 report/scope quality hardening follow-up.

I selected this because the latest Phase 5.2 status a
```
- `verification_artifact` `docs/verification/2026-05-04-autonomous-phase-5-task-2-negation-follow-up-2-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-04-autonomous-phase-5-task-2-negation-follow-up-2-status.md#L1] — Provenance `prov:6325d7a87a6f4864` via `filesystem` confidence `deterministic` hash `154bc5c7a8d7`

Redacted source signal:

```text
# Autonomous Phase 5 Task 2 Follow-up Status — Parser/Report Negation Boundary Round 2

Date: 2026-05-04
Repository: `/home/leonb/projects/cmmc-level1-readiness-assistant`

## Selected task

Selected a tightly scoped **Phase 5.2 parser/report quality follow-up** because the latest durable artifact,
```
- `verification_artifact` `docs/verification/2026-05-04-autonomous-phase-5-task-2-negation-follow-up-3-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-04-autonomous-phase-5-task-2-negation-follow-up-3-status.md#L1] — Provenance `prov:cc5378ac5757ad3d` via `filesystem` confidence `deterministic` hash `0f09ffa0139f`

Redacted source signal:

```text
# Autonomous Phase 5 Task 2 Follow-up Status — Parser/Report Coordination Round 3

Date: 2026-05-04
Repository: `/home/leonb/projects/cmmc-level1-readiness-assistant`

## Selected task

Selected a tightly scoped continuation of **Phase 5.2 parser/report quality hardening** because the previous statu
```
- `verification_artifact` `docs/verification/2026-05-04-autonomous-phase-5-task-2-negation-follow-up-4-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-04-autonomous-phase-5-task-2-negation-follow-up-4-status.md#L1] — Provenance `prov:5af476658ce6f1bd` via `filesystem` confidence `deterministic` hash `fc095a09a6b6`

Redacted source signal:

```text
# Autonomous Phase 5 Task 2 Negation Follow-up 4 Status

Date: 2026-05-04
Repository: `/home/leonb/projects/cmmc-level1-readiness-assistant`
Branch observed: `master`

## Selected unit

**Phase 5.2 parser/report quality hardening follow-up: target-first/passive coordinated negation.**

I selected th
```
- `verification_artifact` `docs/verification/2026-05-04-autonomous-phase-5-task-2-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-04-autonomous-phase-5-task-2-status.md#L1] — Provenance `prov:8f57c0619f277e3a` via `filesystem` confidence `deterministic` hash `8c4d674312fa`

Redacted source signal:

```text
# Autonomous Production Readiness Phase 5 Task 2 Status

Date: 2026-05-04

Repository: `/home/leonb/projects/cmmc-level1-readiness-assistant`

## Selected phase/task

Selected Phase 5.2 report-quality hardening in plan order after prior Phase 4/5.1 status artifacts indicated report/PDF and report-la
```
- `verification_artifact` `docs/verification/2026-05-04-autonomous-phase-6-task-1-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-04-autonomous-phase-6-task-1-status.md#L1] — Provenance `prov:30238eb5c9bdc493` via `filesystem` confidence `deterministic` hash `02a1c607dea9`

Redacted source signal:

```text
# Autonomous Production Readiness Status — Phase 6.1

Date: 2026-05-04
Repository: `/home/leonb/projects/cmmc-level1-readiness-assistant`
Branch observed: `master`

## Scope selected

Selected **Phase 6.1: run backend/frontend final gates** because:

- The primary plan lists Phase 6 after Phase 5 pa
```
- `verification_artifact` `docs/verification/2026-05-04-autonomous-phase-6-task-2-browser-smoke-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-04-autonomous-phase-6-task-2-browser-smoke-status.md#L1] — Provenance `prov:a0129e93752260fa` via `filesystem` confidence `deterministic` hash `80beaa4a00f1`

Redacted source signal:

```text
# Autonomous Production Readiness — Phase 6 Task 6.2 Browser Smoke Status

**Date:** 2026-05-04
**Runner:** Scheduled autonomous production-readiness phase runner
**Repository:** `/home/leonb/projects/cmmc-level1-readiness-assistant`
**Plan:** `docs/plans/2026-04-30-production-readiness-implementati
```
- `verification_artifact` `docs/verification/2026-05-04-autonomous-phase-6-task-3-review-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-04-autonomous-phase-6-task-3-review-status.md#L1] — Provenance `prov:8197b25995fc0f96` via `filesystem` confidence `deterministic` hash `7a1a826d2d51`

Redacted source signal:

```text
# Autonomous Production Readiness — Phase 6 Task 6.3 Review Status

**Date:** 2026-05-04 15:21:23 UTC
**Runner:** Scheduled autonomous production-readiness phase runner
**Repository:** `/home/leonb/projects/cmmc-level1-readiness-assistant`
**Plan:** `docs/plans/2026-04-30-production-readiness-implem
```
- `verification_artifact` `docs/verification/2026-05-05-phase-6-3-blocker-resolution-completion-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-05-phase-6-3-blocker-resolution-completion-status.md#L1] — Provenance `prov:a9d09ec4e8b513a7` via `filesystem` confidence `deterministic` hash `654faa0e811b`
- `verification_artifact` `docs/verification/2026-05-05-public-beta-launch-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-05-public-beta-launch-status.md#L1] — Provenance `prov:0cdbbf24ed443646` via `filesystem` confidence `deterministic` hash `bd5a92f2eac6`
- `verification_artifact` `docs/verification/2026-05-07-browser-opus-persona-qa-findings.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-07-browser-opus-persona-qa-findings.md#L1] — Provenance `prov:07a0c1d35af0726f` via `filesystem` confidence `deterministic` hash `dd9693d1b3f5`
- `verification_artifact` `docs/verification/2026-05-07-cmmc-browser-persona-qa-remediation-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-07-cmmc-browser-persona-qa-remediation-status.md#L1] — Provenance `prov:3953fc9266506856` via `filesystem` confidence `deterministic` hash `305206d1fe5c`
- `verification_artifact` `docs/verification/2026-05-07-live-browser-qa-capability-check.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-07-live-browser-qa-capability-check.md#L1] — Provenance `prov:bed7c9b40b587a17` via `filesystem` confidence `deterministic` hash `d4813da53b79`
- `verification_artifact` `docs/verification/2026-05-07-slice-4-scope-unknowns-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-07-slice-4-scope-unknowns-status.md#L1] — Provenance `prov:a927f2c26ba12225` via `filesystem` confidence `deterministic` hash `5ce66bc2b7b8`
- `verification_artifact` `docs/verification/2026-05-08-github-hermes-hybrid-autonomy-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-08-github-hermes-hybrid-autonomy-status.md#L1] — Provenance `prov:c91c94a06655efd8` via `filesystem` confidence `deterministic` hash `4dfd909e508a`

Redacted source signal:

```text
# GitHub + Hermes Hybrid Autonomy Implementation Status

Date: 2026-05-08T04:15:03Z
Repository: `leonbreukelman/cmmc-level1-readiness-assistant`
Local checkout: `/home/leonb/projects/cmmc-level1-readiness-assistant`
Branch: `feat/cmmc-public-beta-qa-remediation-20260507`

## Scope

Implemented the h
```
- `verification_artifact` `docs/verification/2026-05-08-google-auth-access-gate-opus-implementation-review.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-08-google-auth-access-gate-opus-implementation-review.md#L1] — Provenance `prov:12348a2e90d2c4d4` via `filesystem` confidence `deterministic` hash `a106cb754ed6`

Redacted source signal:

```text
# Adversarial Review: Google Auth Access Gate

## Verdict: REQUEST_CHANGES

There is one HIGH-severity authn bypass, one MEDIUM schema correctness issue, and several worthwhile hardening notes.

---

## Blocking findings

### H1 — `email_verified` and Google-provider checks trust user-controllable `
```
- `verification_artifact` `docs/verification/2026-05-08-google-auth-access-gate-opus-postfix-review.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-08-google-auth-access-gate-opus-postfix-review.md#L1] — Provenance `prov:4dcd34291b43f210` via `filesystem` confidence `deterministic` hash `646592ebb735`
- `verification_artifact` `docs/verification/2026-05-08-google-auth-access-gate-verification.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-08-google-auth-access-gate-verification.md#L1] — Provenance `prov:e014b38b4fb6d23a` via `filesystem` confidence `deterministic` hash `4edfd076f643`

Redacted source signal:

```text
# Google Auth Access Gate Verification — 2026-05-08

## Scope

Implemented and verified the first production-oriented Google Auth access-gate slice for the CMMC Level 1 Readiness Assistant.

Production target confirmed in the plan remains:

- Cloudflare Pages for the public/static frontend.
- Supaba
```
- `verification_artifact` `docs/verification/2026-05-08-guided-assessment-ux-polish-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-08-guided-assessment-ux-polish-status.md#L1] — Provenance `prov:7e2a90c817e422db` via `filesystem` confidence `deterministic` hash `62d10df92989`
- `verification_artifact` `docs/verification/2026-05-08-issue-5-accessibility-labels-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-08-issue-5-accessibility-labels-status.md#L1] — Provenance `prov:bb957af5f819c7e0` via `filesystem` confidence `deterministic` hash `22afb8085438`
- `verification_artifact` `docs/verification/2026-05-08-issue-9-report-pdf-language-smoke-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-08-issue-9-report-pdf-language-smoke-status.md#L1] — Provenance `prov:998d9e11fc9b8141` via `filesystem` confidence `deterministic` hash `fccb02aa2fe8`
- `verification_artifact` `docs/verification/2026-05-08-pr-packaging-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-08-pr-packaging-status.md#L1] — Provenance `prov:fc4ded0941c66347` via `filesystem` confidence `deterministic` hash `f8fb98f0387f`
- `verification_artifact` `docs/verification/2026-05-08-production-smoke-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-08-production-smoke-status.md#L1] — Provenance `prov:1441107910843458` via `filesystem` confidence `deterministic` hash `507374c12aba`
- `verification_artifact` `docs/verification/2026-05-08-tenant-isolation-route-matrix-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-08-tenant-isolation-route-matrix-status.md#L1] — Provenance `prov:7809f0a19f745293` via `filesystem` confidence `deterministic` hash `04b422b0b076`
- `verification_artifact` `docs/verification/2026-05-10-beta-request-link-profile-fix.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-10-beta-request-link-profile-fix.md#L1] — Provenance `prov:16303f8ef032c17f` via `filesystem` confidence `deterministic` hash `d84366932c0e`
- `verification_artifact` `docs/verification/2026-05-10-llm-assisted-interview-status.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-10-llm-assisted-interview-status.md#L1] — Provenance `prov:41963d375f930cb9` via `filesystem` confidence `deterministic` hash `4e565ae13d9a`
- `verification_artifact` `docs/verification/2026-05-10-mailto-handler-routing.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-10-mailto-handler-routing.md#L1] — Provenance `prov:df2ea5d956d15484` via `filesystem` confidence `deterministic` hash `f32f125ca01b`
- `verification_artifact` `docs/verification/2026-05-10-production-pages-deploy-guardrail.md` — tags `excluded_from_primary_context` — [source://docs/verification/2026-05-10-production-pages-deploy-guardrail.md#L1] — Provenance `prov:9dba4b9c85b7ff17` via `filesystem` confidence `deterministic` hash `1b2101999bfb`
- `verification_artifact` `docs/verification/browser-smoke.md` — tags `excluded_from_primary_context` — [source://docs/verification/browser-smoke.md#L1] — Provenance `prov:a504c187197c887f` via `filesystem` confidence `deterministic` hash `a51ee61a1c92`
