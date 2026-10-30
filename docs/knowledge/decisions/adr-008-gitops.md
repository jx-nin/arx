---
type: Decision
title: "ADR-008 GitOps deployment"
description: Phase 2 deploys by Argo CD pulling from Git; CI never reaches into the homelab.
tags: [deployment, adr]
status: stable
generated: { by: "agent:claude-opus-5-5", at: 2026-10-30T00:00:00Z }
---

# Decision

* CI needs no inbound access to the homelab, Git is the source of truth, and drift is detected.

Summary row: [specification](/specs/tds.md), section 13.
