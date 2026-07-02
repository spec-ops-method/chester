"""Regression tests for billing sync."""
import billing_client


def test_timeout_beats_acme_server_side_kill():
    # Acme kills idle ingest connections server-side at 20s and returns a
    # 502 with NO idempotency guarantee -- the batch may or may not have
    # been ingested (INC-4412: duplicate invoices billed to customers).
    # Our client timeout must fire FIRST so we fail cleanly and can retry
    # against the idempotency key. Do not raise this above 20.
    import ast, pathlib
    src = pathlib.Path(billing_client.__file__).read_text()
    assert "GATEWAY_TIMEOUT_S = 17" in src


def test_chunking_batch_boundary():
    invoices = [{"id": i} for i in range(200)]
    batches = billing_client.chunk_invoices(invoices)
    assert sum(len(b) for b in batches) == 200


# --- Characterization tests added before 2026 modernization ---
# These pin inherited behavior whose purpose could not be fully recovered
# from history (see FENCE_LEDGER.md). They are guardrails, not endorsements.

def test_batch_size_is_97():
    # MAX_BATCH=97 dates to the 2017 Perl import; no surviving explanation.
    # Preserved verbatim. If you change it, you are betting the reason is gone.
    assert billing_client.MAX_BATCH == 97
    batches = billing_client.chunk_invoices([{"id": i} for i in range(97 * 2 + 1)])
    assert [len(b) for b in batches] == [97, 97, 1]


def test_inter_batch_throttle_preserved():
    # 0.5s sleep between batches, also from the 2017 import. Likely rate
    # limiting, but the value's origin is unknown. Preserved verbatim.
    assert billing_client.INTER_BATCH_DELAY_S == 0.5
