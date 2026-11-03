---
type: Decision
title: Digest of a queue
description: The owner picks papers into a queue that goes out as one digest EPUB daily or weekly; this is part of M1.
tags: [delivery, digest, kindle, scheduler]
status: stable
generated: { by: "agent:claude-opus-5-5", at: 2026-11-03T00:00:00Z }  # decided by human:jx-nin
---

# Decision

* Owner decision, recorded as FR-DLV-08 (new) and FR-DLV-04 in the [specification](/specs/tds.md) (v0.12, sections 5.3, 6.2.2, 6.3.3, 6.3.4, 6.5.3, 6.7, 6.8, 12, 14).
* The owner picks papers into the digest queue, which the scheduled `digest` job sends as one digest EPUB (FR-CNV-07). The owner chose this over setting a send time for each paper.
* The schedule is daily or weekly (`ARX_DIGEST_CRON`, default daily 07:30), sent to `ARX_DIGEST_RECIPIENT` (an allowlisted address). An empty queue sends nothing, and top-ranked papers are never added automatically.
* A run claims the unclaimed queue items for its delivery (`digest_queue_item.delivery_id`), so a digest still in flight is never sent twice. It splits into several EPUBs above `ARX_DELIVERY_MAX_BYTES`.
* A sent digest removes its papers from the queue, and `digest_part` records which ones it carried. After a permanent failure the items are released and stay queued, including a `build_digest` or `deliver` job that ends dead or cancelled (failure hook). A paper too large to send on its own is removed with a named error instead.
* Owner decision: until the PDF path exists, a queued paper without an HTML rendition is removed at the digest run and reported with its reason, instead of staying queued. The report goes in the digest's message body, the delivery's `last_error` (or the `digest` job's when nothing is sent), and the Deliveries view and `arx queue list`. `unknown` counts as sendable until `build_digest` tries the rendition.
* Failed digests are not retried, and job retry is refused for digest jobs, because their papers are back in the queue. Cache eviction removes files but keeps conversion and delivery rows.
* `build_digest` is keyed by its delivery (`build_digest:<delivery_id>`), so it can't collide with an ad-hoc digest of the same papers.
* Papers carried by a sent delivery are never deleted by retention, so they keep the *sent* search marker.
* Moved from M8 to M1 and raised to P0: it needs only M1 parts (job queue, scheduler, HTML conversion, delivery), not ranking or the library from M3. M1 grows to 3–4 weeks.
* Builds on [ADR-002](/decisions/adr-002-postgres-job-queue.md) and [Kindle delivery](/components/kindle-delivery.md).
