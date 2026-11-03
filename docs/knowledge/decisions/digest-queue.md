---
type: Decision
title: Digest of a queue
description: The owner picks papers into a queue that goes out as one digest EPUB daily or weekly; this is part of M1.
tags: [delivery, digest, kindle, scheduler]
status: stable
generated: { by: "agent:claude-opus-5-5", at: 2026-11-03T00:00:00Z }  # decided by human:jx-nin
---

# Decision

* Owner decision, recorded as FR-DLV-08 (new) and FR-DLV-04 in the [specification](/specs/tds.md) (v0.10, sections 5.3, 6.2.2, 6.3.4, 6.5.3, 6.7, 12).
* The owner picks papers into the digest queue, which the scheduled `digest` job sends as one digest EPUB (FR-CNV-07). The owner chose this over setting a send time for each paper.
* The schedule is daily or weekly (`ARX_DIGEST_CRON`, default daily 07:30). An empty queue sends nothing, and top-ranked papers are never added automatically.
* A sent digest removes its papers from the queue (`digest_part` records which ones it carried). After a permanent failure they stay queued.
* Moved from M8 to M1 and raised to P0: it needs only M1 parts (job queue, scheduler, HTML conversion, delivery), not ranking or the library from M3. M1 grows to 3–4 weeks.
* Builds on [ADR-002](/decisions/adr-002-postgres-job-queue.md) and [Kindle delivery](/components/kindle-delivery.md).
