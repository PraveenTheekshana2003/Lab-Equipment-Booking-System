# Peer Code Review Checklist

Before approving and merging a Pull Request into `main`, reviewers must verify the following:

## 1. Code Quality & Formatting
- [ ] Code follows Python / PEP 8 guidelines and passes `ruff check .` with no linting errors.
- [ ] Variable and function names are clear, descriptive, and consistent.
- [ ] No temporary debug statements, hardcoded credentials, or unused code remain.

## 2. Functionality & Requirements
- [ ] The feature meets the acceptance criteria defined in the linked GitHub Issue.
- [ ] Existing functionality remains unaffected (no regression issues).

## 3. Automated Testing & CI
- [ ] New or updated unit tests are included under `tests/`.
- [ ] All tests pass via `pytest`.
- [ ] GitHub Actions CI pipeline passes successfully.

## 4. Documentation & Maintenance
- [ ] Relevant documentation (e.g., inline comments, docstrings, or README) is updated if necessary.
- [ ] Database migrations or schema updates (if any) are properly documented.


# Code Review Checklist

Use this checklist when reviewing a pull request. Leave a comment confirming the items checked.

```
[ ] User inputs are validated.
[ ] Business rules and conditions are correct.
[ ] Database operations are appropriate.
[ ] Login and role restrictions are checked.
[ ] Errors are handled appropriately.
[ ] No passwords or secret values are committed.
[ ] Relevant automated tests have been added.
[ ] Existing tests still pass.
```

## Reviewer notes

- A student must **not** approve their own pull request.
- If any item fails, request changes before merging.
- Reference the related GitHub Issue in the PR description.
