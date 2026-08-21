## 📝 Description

Summarize the changes introduced by this Pull Request. Include relevant motivation and context.

Fixes # (issue)

## 🛠️ Type of Change

- [ ] 🐛 Bug fix (non-breaking change fixing an issue)
- [ ] ✨ New feature / workflow
- [ ] 💊 Drug data update / seeding
- [ ] 📚 Documentation update
- [ ] 🧪 Test suite improvement

## ✅ Pre-Submission Verification Checklist

Please verify that all tests pass before requesting review:

- [ ] **Workflow Linter:** `python .agent/scripts/workflow_linter.py` passed with 0 errors.
- [ ] **Data Validator:** `python scripts/maintenance/validate_data.py` passed with 0 errors.
- [ ] **Unit & Integration Tests:** `python -m pytest tests/ -v` passed cleanly.
- [ ] **Medical Disclaimer:** All new workflows contain the mandatory medical disclaimer.

## 📷 Screenshots / Evidence (if applicable)

Add screenshots, log output snippets, or example execution markdown reports.
