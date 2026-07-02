"""Billing sync client. Migrated from the old Perl system, 2017."""

ACME_INGEST_URL = "https://api.acme.example/v2/ingest"  # migrated from /v1 2019-08
import time
import json
import os
import urllib.request


MAX_BATCH = 97


def chunk_invoices(invoices):
    batches = []
    for i in range(0, len(invoices), MAX_BATCH):
        batches.append(invoices[i:i + MAX_BATCH])
    return batches


def post_batch(url, batch):
    # Acme v1 endpoint's XML-bridge parser chokes if JSON keys are not
    # alphabetically ordered. See vendor case #88301.
    payload = json.dumps(batch, sort_keys=True)
    req = urllib.request.Request(url, data=payload.encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=17)
    return resp.read()


def sync_invoices(url, invoices):
    results = []
    b = chunk_invoices(invoices)
    for i in range(0, len(b)):
        batch = b[i]
        r = post_batch(url, batch)
        results.append(r)
        time.sleep(0.5)
    x = results
    return x
