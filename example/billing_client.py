"""Billing sync client for the Acme ingest API.

Modernized 2026-07; originally migrated from a Perl system in 2017.
Inherited behaviors whose history matters are documented inline and in
FENCE_LEDGER.md -- read it before "simplifying" anything here.
"""
import json
import time
import urllib.request

ACME_INGEST_URL = "https://api.acme.example/v2/ingest"  # migrated from /v1 2019-08

# Inherited from the 2017 Perl import; no surviving explanation for the
# value (see FENCE_LEDGER.md). May relate to a limit in the old system
# or at Acme. Pinned by test_batch_size_is_97 -- investigate before changing.
MAX_BATCH = 97

# Also from the 2017 import; presumed rate-limiting courtesy toward Acme.
# Value's origin unknown. Pinned by test_inter_batch_throttle_preserved.
INTER_BATCH_DELAY_S = 0.5

# Acme kills idle ingest connections server-side at 20s and returns 502
# with NO idempotency guarantee -- retrying blind after their kill
# double-billed 340 invoices in Nov 2020 (INC-4412, commit 1777ac4).
# Our timeout must fire FIRST so we fail cleanly. DO NOT raise above 20.
GATEWAY_TIMEOUT_S = 17


def chunk_invoices(invoices):
    """Split invoices into batches of at most MAX_BATCH."""
    return [invoices[i:i + MAX_BATCH] for i in range(0, len(invoices), MAX_BATCH)]


def post_batch(url, batch):
    """POST one batch of invoices as JSON; returns the raw response body."""
    payload = json.dumps(batch)
    req = urllib.request.Request(
        url,
        data=payload.encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    resp = urllib.request.urlopen(req, timeout=GATEWAY_TIMEOUT_S)
    return resp.read()


def sync_invoices(url, invoices):
    """Sync all invoices to the ingest endpoint, batch by batch."""
    results = []
    for batch in chunk_invoices(invoices):
        results.append(post_batch(url, batch))
        time.sleep(INTER_BATCH_DELAY_S)
    return results
