# Project Standards (FoSGamers Universal)

## Required Practices
- All code must be version controlled with Git and pushed to GitHub after every change.
- All features, fixes, and refactors must be accompanied by or followed by tests.
- All projects must have CI/testing via GitHub Actions, running on every push and PR, with all tests passing before merge.
- Include a `.github/workflows/python-app.yml` (or equivalent) for CI. The badge should be in the README.
- Never break existing functionality or leave the app in an inconsistent state.
- Communicate clearly about what is being changed, why, and how it is being tested.

## Recommended Project Structure
- `main.py` (or entry point)
- `assets/` (images, sounds, etc.)
- `config/` (templates, settings)
- `tests/` (unit and integration tests)
- `.github/workflows/` (CI workflows)
- `README.md` (with CI badge and setup instructions)

---

For updates to these standards, see the template repository or shared documentation. 