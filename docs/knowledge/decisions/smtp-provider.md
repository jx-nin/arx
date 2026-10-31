---
type: Decision
title: SMTP provider Gmail
description: Send to Kindle mail goes out through a dedicated Gmail account with an app password.
tags: [delivery, kindle, security]
status: stable
generated: { by: "agent:claude-opus-5-5", at: 2026-10-31T00:00:00Z }  # decided by human:jx-nin
---

# Decision

* Answers Q-4 of the [specification](/specs/tds.md) (v0.4, section 6.6.3).
* A Gmail account used only by Arx is the approved sender: `smtp.gmail.com:587`, STARTTLS, app password in `ARX_SMTP_PASSWORD_FILE`.
* Free, no own domain needed, and Gmail signs with DKIM, so Amazon accepts the mail.
* A separate account limits a leaked app password, which grants full mailbox access, to a throwaway inbox.
* Gmail's 25 MB attachment limit sets `ARX_DELIVERY_MAX_BYTES` to 20 MiB of raw file: base64 grows the message by about a third, and Send to Kindle's 50 MB is higher anyway. Large digests are split (spec 6.5.3).
* Upgrade path: a transactional provider (SES, Postmark) with SPF/DKIM on an own domain, or OAuth2 instead of the app password; both change configuration, not the mail adapter interface.
