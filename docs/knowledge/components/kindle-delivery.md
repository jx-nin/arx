---
type: Component
title: Kindle delivery
description: M0 path that e-mails a converted EPUB to an allowlisted Kindle address over Gmail SMTP with STARTTLS.
tags: [delivery, kindle, security]
status: draft
generated: { by: "agent:claude-opus-5-5", at: 2026-10-31T00:00:00Z }
---

# Component

* Covers FR-DLV-02, FR-DLV-03 (reject only; downscale option in M1) and FR-DLV-07 for M0 (spec 6.6.3); history (FR-DLV-05), retries (FR-DLV-06) and digests follow in M1.
* `services/delivery.py`: `DeliveryService.send_epub` checks the recipient against the allowlist and the raw size against the limit before building the message; it depends on the `Mailer` protocol, which takes a stdlib `EmailMessage`.
* Rejections raise `RecipientNotAllowedError` or `AttachmentTooLargeError` (both `ValueError`) and never reach the mailer.
* Attachment name `<surname>-<year>-<five title words>.epub`, ASCII-folded, at most 80 characters; the versioned arXiv ID replaces a surname without ASCII letters.
* `adapters/mail/smtp_mailer.py`: `SmtpMailer` uses stdlib `smtplib` with STARTTLS (certificate verified) and login; it reads the password file on every send. Provider per the [SMTP provider decision](/decisions/smtp-provider.md).
* `settings.py`: pydantic-settings reads `ARX_*` variables and `.env`; secrets only as file paths (spec 7.4). Settings refuse an empty allowlist or a non-`@kindle.com` recipient.
* Not wired yet: `bootstrap.py` and the CLI come in the next slice. Implicit TLS (465) is unsupported until a provider needs it.
