# TESTING.md

## Test Design Approach

- **Equivalence Partitioning** – valid vs invalid inputs for duration, status, overlap
- **Boundary Value Analysis** – 29/30 min, 4 h / 4 h 1 min, exact start=end of previous booking

## Test Cases (FR-03 focus)

| Test ID | Requirement | Test Condition | Expected Result | Technique | Result |
|---------|-------------|----------------|-----------------|-----------|--------|
| T01 | FR-03 | End time before start | Reject | Boundary | Pass |
| T02 | FR-03 | End time equal start | Reject | Boundary | Pass |
| T03 | FR-03 | Duration 29 min | Reject | Boundary | Pass |
| T04 | FR-03 | Duration 30 min | Accept | Boundary | Pass |
| T05 | FR-03 | Duration 4 hours | Accept | Boundary | Pass |
| T06 | FR-03 | Duration 4 h 1 min | Reject | Boundary | Pass |
| T07 | FR-03 | Booking starts in the past | Reject | Equivalence | Pass |
| T08 | FR-03 | Equipment Out of service | Reject | Equivalence | Pass |
| T09 | FR-03 | New booking overlaps existing | Reject | Equivalence | Pass |
| T10 | FR-03 | New booking starts when other ends | Accept | Boundary | Pass |
| T11 | FR-00 | Student registration | Success | Equivalence | Pass |
| T12 | FR-00 | Login with wrong password | Reject | Equivalence | Pass |
| T13 | FR-00 | Student cannot access staff page | Reject | Equivalence | Pass |
| T14 | FR-01 | Staff can add equipment | Success | Equivalence | Pass |
| T15 | FR-02 | Valid booking request stored as Pending | Success | Equivalence | Pass |
| T16 | FR-04 | Staff approve pending booking | Success | Equivalence | Pass |
| T17 | FR-04 | Staff reject with reason | Success | Equivalence | Pass |

## How to run

```bash
pytest -v
pytest --cov=main --cov-report=term-missing
```

Target: ≥ 40 % line coverage on `main.py`.
