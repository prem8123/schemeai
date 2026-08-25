# SchemeAI Privacy and Data Handling

## What SchemeAI processes

A student profile may contain sensitive information such as family income, category, disability status, education history, and location/state.

## Logging

Raw student profile fields are not intentionally written to application logs. Operational logs contain request IDs, endpoint paths, latency, HTTP status, retrieval-hit counts, and aggregate eligibility-tier counts.

## Retention

The MVP does not persist submitted student profiles by default. If a deployment adds persistence, it must define a retention period, purpose, access controls, and deletion mechanism before storing profiles.

## Deletion

For any deployment that persists profile data, provide a user-accessible deletion operation and delete associated records from primary storage, derived analytics, and backups according to the deployment retention policy.

## Secrets

API keys and provider credentials belong in environment/secret-management systems and must never be committed to Git. `.env` files are ignored by Git and CI performs a tracked-secret check.

## Important limitation

SchemeAI is an informational matching system. Students must verify current eligibility, deadlines, documents, and application requirements on the official authority's portal before applying.
