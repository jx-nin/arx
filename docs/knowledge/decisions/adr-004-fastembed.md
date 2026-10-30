---
type: Decision
title: "ADR-004 fastembed on CPU"
description: Embeddings use fastembed (ONNX Runtime) with BAAI/bge-small-en-v1.5, 384 dimensions.
tags: [ml, embeddings, adr]
status: stable
generated: { by: "agent:claude-opus-5-5", at: 2026-10-30T00:00:00Z }
---

# Decision

* About 130 MB model, no PyTorch, runs on CPU, good enough quality for abstracts.
* The model name is stored with each embedding so the corpus can be re-indexed.
* Pins the Python version: onnxruntime ships wheels only up to 3.14 (see [ADR-010](/decisions/adr-010-python.md)).

Summary row: [specification](/specs/tds.md), section 13.
