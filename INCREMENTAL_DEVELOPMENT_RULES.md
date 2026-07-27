# Isolated Incremental Improvement Guidelines

This document defines the strict rules that all AI coding agents must follow when making incremental improvements in this repository and branch.

---

## 🎯 Core Objective
Make additions, enhancements, and bug fixes **incrementally** and **in isolation**, ensuring that all pre-existing, stable features remain completely unaffected and functional.

---

## 📜 Agent Execution Rules

### 1. File & Module Isolation
* **Create New Files First**: Whenever adding a new feature, report format, UI component, or data processing logic, create a dedicated new file or module (e.g., `report_v2.py`, `feature_x.py`, or sub-packages) rather than refactoring or editing existing files.
* **Keep Edits Additive**: If modifying existing files (such as `app.py` or `db.py`) is necessary to wire up the new logic, keep the changes strictly **additive** (e.g., adding new imports or route declarations). **Do not delete, overwrite, or refactor existing working functions**.

### 2. Preserve Existing Function Signatures & Behavior
* **Open-Closed Principle**: Existing functions, classes, and helper utilities are closed for modification but open for extension.
* **Side-by-Side Implementation**: Create parallel versions of functions (e.g., `generate_ba_report_v2()`) alongside the stable versions (`generate_ba_report()`) instead of altering the original function's internal implementation or signature.

### 3. Use Feature Flags & Safe Fallbacks
* **Controlled Rollout**: Use feature flags or configuration variables (e.g., `ENABLE_V2_FEATURES = False`) to gate new experimental features.
* **Default to Stable**: Ensure the default execution path routes to the stable, proven logic unless explicitly configured or toggled on.

### 4. Mandatory Regression & Sanity Verification
* **Check Old & New**: Before marking any task complete:
  1. Test that existing stable features work exactly as before (No Regressions).
  2. Test that the new incremental feature works in isolation.
* **Do Not Mask Failures**: If an error occurs, inspect raw log traces and fix the root cause without suppressing exceptions or removing existing assertions.

---

## 🛠 Quick Checklist for Agents Before Applying Changes
- [ ] Is this new feature placed in its own dedicated file/module?
- [ ] Are existing working functions untouched and preserved?
- [ ] Is there a fallback mechanism to the legacy logic if needed?
- [ ] Have both existing logic and new logic been tested?
