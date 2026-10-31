---
type: Decision
title: Mail and settings libraries
description: Send mail with stdlib smtplib until the worker is async; load configuration with pydantic-settings.
tags: [delivery, configuration]
status: stable
generated: { by: "agent:claude-opus-5-5", at: 2026-10-31T00:00:00Z }  # decided by human:jx-nin
---

# Decision

* Spec 5.5 (v0.7) named aiosmtplib; M0 services are synchronous, so stdlib `smtplib` sends mail without an extra dependency.
* Upgrade path: aiosmtplib once the worker is async (M1); only `adapters/mail/` changes, the `Mailer` protocol may become async.
* Configuration uses pydantic-settings as spec 5.5 names it: typed `ARX_*` variables, `.env` support and validation (allowlist, `@kindle.com`) at load time.
* Secrets stay out of the environment: settings hold only secret file paths (spec 7.4); see [SMTP provider Gmail](/decisions/smtp-provider.md).
