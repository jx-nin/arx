---
type: Decision
title: Default Kindle profile
description: The default rendering profile targets the owner's Kindle Paperwhite Signature Edition (11th generation).
tags: [conversion, kindle]
status: stable
generated: { by: "agent:claude-opus-5-5", at: 2026-10-31T00:00:00Z }  # decided by human:jx-nin
---

# Decision

* Answers Q-1 of the [specification](/specs/tds.md) (v0.4, section 6.5).
* Profile `paperwhite-11-signature`: 1236 × 1648 px, `image_dpi` 300, greyscale; seeded as the default row of `kindle_profile`.
* 300 dpi is the panel's native density, so maths and figure images map 1:1 to device pixels; the panel shows 16 grey levels.
* Target firmware for the device test (Q-3, [ADR-006](/decisions/adr-006-math-png.md)): 5.19.2.
* Not decided: figure margins (tuned on the device) and further profiles (FR-CNV-06, P1).
