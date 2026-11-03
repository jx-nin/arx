---
type: Decision
title: Web UI access before owner login
description: M1's minimal UI is reachable over the tailnet only, without login; owner login (FR-ADM-05) arrives in M3.
tags: [security, ui]
status: stable
generated: { by: "agent:claude-opus-5-5", at: 2026-11-03T00:00:00Z }  # decided by human:jx-nin
---

# Decision

* Answers Q-7 of the [specification](/specs/tds.md) (v0.10; 3.10, 7.2 T1, 14).
* M1-M2: the minimal UI (feed list, send button) is bound to the tailnet only (Tailscale) and has no login; tailnet exposure is the only control for threat T1.
* M3: owner login FR-ADM-05 (P0) arrives with the full UI: Argon2id password hash, session cookie (`Secure`, `HttpOnly`, `SameSite=Strict`), CSRF token; probe and metrics endpoints stay open.
