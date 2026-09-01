# Software Testing Document
## SLM-Powered Legal & Civic Service Assistant

**Project:** Legal & Civic Service Assistant
**Testing Type:** Manual Functional / Black-Box Testing
**Tested By:** _______________________
**Date:** _______________________

---

## 1. Testing Scope

This document covers manual functional testing for the following modules, derived directly from the implemented routes in the system:

| # | Module | Source File(s) |
|---|---|---|
| 1 | Authentication (Register/Login/Logout) | `routes/auth.py` |
| 2 | User Dashboard | `routes/dashboard.py` |
| 3 | AI Chat Assistant (Gemini + Fallback KB) | `routes/chatbot.py` |
| 4 | Government Services | `routes/services.py` |
| 5 | Document Checklist | `routes/checklist.py` |
| 6 | User Profile | `routes/profile.py` |
| 7 | Admin Panel (Services/Users/Links) | `routes/admin.py` |
| 8 | Multilingual Switching | `app.py`, `translations.py` |

**Out of scope:** Load testing, penetration testing, automated unit tests (noted as future work in Limitations section).

---

## 2. Test Environment

| Item | Detail |
|---|---|
| OS | Windows 10/11 |
| Browser | Google Chrome (latest) |
| Backend | Python 3.11, Flask 3.0 |
| Database | MySQL 8 (via XAMPP) |
| AI | Google Gemini API (gemini-1.5-flash) + rule-based fallback |
| Test Accounts | Admin: `admin@legalcivic.lk` / `admin123` <br> User: created during TC-002 |

---

## 3. Test Case Table

| TC ID | Module | Test Scenario | Steps | Test Data | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|---|---|
| TC-001 | Auth | Register with valid details | 1. Go to `/register` 2. Fill all fields 3. Submit | fullname="Test User", email="test1@mail.com", password="Test@123", confirm="Test@123" | Account created, redirected to dashboard, flash "Account created!" | | |
| TC-002 | Auth | Register with mismatched passwords | 1. Go to `/register` 2. Enter different password/confirm | password="abc123", confirm="xyz456" | Flash error "Passwords do not match", form redisplayed | | |
| TC-003 | Auth | Register with already-used email | 1. Register with an email already in DB | email="admin@legalcivic.lk" | Flash error "Email already registered" | | |
| TC-004 | Auth | Login with correct credentials | 1. Go to `/login` 2. Enter valid email/password | email="admin@legalcivic.lk", password="admin123" | Redirected to `/admin/dashboard` (admin) or `/dashboard` (user) | | |
| TC-005 | Auth | Login with incorrect password | 1. Go to `/login` 2. Enter wrong password | email="admin@legalcivic.lk", password="wrongpass" | Flash error "Invalid email or password", stays on login page | | |
| TC-006 | Auth | Logout | 1. While logged in, click Logout | — | Session cleared, redirected to `/login` | | |
| TC-007 | Auth | Access protected page while logged out | 1. Log out 2. Manually visit `/dashboard` | — | Redirected to `/login` (Flask-Login `@login_required`) | | |
| TC-008 | Dashboard | View dashboard after login | 1. Log in as normal user | — | Shows welcome message, chat count, saved guides count, recent chats, popular services | | |
| TC-009 | Dashboard | Dashboard with zero chat history | 1. Log in as brand-new user | — | "My Chats" = 0, "No chats yet" message shown with link to chat | | |
| TC-010 | AI Chat | Ask a question (fallback mode, no Gemini key) | 1. Go to `/ai-chat` 2. Type "How to apply for NIC?" 3. Send | question="How to apply for NIC?" | Returns pre-written NIC fallback answer, badge shows "Using Built-in Knowledge Base" | | |
| TC-011 | AI Chat | Ask a question (Gemini mode, real key set) | 1. Add valid Gemini key in `.env` 2. Restart app 3. Ask a question | question="What documents do I need for passport?" | Badge shows "Gemini AI Active", returns AI-generated contextual answer | | |
| TC-012 | AI Chat | Ask an unrelated/unknown question (fallback mode) | 1. Type question with no matching keyword | question="What is the capital of France?" | Returns default fallback message (not an error) | | |
| TC-013 | AI Chat | Empty question submission | 1. Click Send with empty input | question="" | Client-side blocks submission OR server returns 400 "Empty question" | | |
| TC-014 | AI Chat | Chat history persists after reload | 1. Ask a question 2. Reload `/ai-chat` page | — | Previous Q&A still visible (loaded from `chat_history` table) | | |
| TC-015 | AI Chat | Gemini API failure simulation (no internet/invalid key) | 1. Set invalid Gemini key 2. Ask a question | GEMINI_API_KEY="invalid_key_123" | System catches exception, silently falls back to KB answer (no crash/500 error) | | |
| TC-016 | Services | View all government services | 1. Go to `/services` | — | Lists all `Active` services with icon, name, category | | |
| TC-017 | Services | Search/filter services | 1. Go to `/services` 2. Type in search box | search="passport" | Only matching service cards remain visible (client-side JS filter) | | |
| TC-018 | Services | View service detail page | 1. Click a service card (e.g. NIC Application) | — | Shows description, numbered step-by-step process, required documents list, official link button | | |
| TC-019 | Services | Save a service guide | 1. Open a service detail page 2. Click "Save Guide" | — | Flash "Guide saved to your dashboard!", button changes to "Saved" (disabled) | | |
| TC-020 | Services | Save the same guide twice | 1. Save a guide 2. Visit the same service page again | — | No duplicate row created in `saved_guides` table (checked via `existing` query before insert) | | |
| TC-021 | Checklist | View checklist list page | 1. Go to `/checklist` | — | Shows all active services as cards | | |
| TC-022 | Checklist | View checklist for specific service | 1. Click a service from checklist page | — | Shows required documents with Required/Optional badges and checkboxes | | |
| TC-023 | Checklist | Check off documents updates progress counter | 1. Open a checklist 2. Tick 2 of 5 checkboxes | — | Progress badge updates to "2 / 5" instantly (client-side JS) | | |
| TC-024 | Profile | View and update profile | 1. Go to `/profile` 2. Change full name and language 3. Save | fullname="Updated Name" | Flash "Profile updated successfully!", changes persist on reload | | |
| TC-025 | Profile | Email field is read-only | 1. Go to `/profile` | — | Email input is `disabled`, cannot be edited | | |
| TC-026 | Admin | Non-admin user tries to access `/admin/dashboard` | 1. Log in as normal user 2. Manually visit `/admin/dashboard` | — | Flash "Admin access required", redirected to `/login` (via `admin_required` decorator) | | |
| TC-027 | Admin | Admin views dashboard stats | 1. Log in as admin 2. Go to `/admin/dashboard` | — | Shows correct counts: total users, total services, total chats, total documents | | |
| TC-028 | Admin | Add a new government service | 1. Go to `/admin/services/add` 2. Fill form 3. Submit | name="Test Service", category="Test", icon="🧪" | Service appears in `/admin/services` list and public `/services` page | | |
| TC-029 | Admin | Edit an existing service | 1. Click edit icon on a service 2. Change name 3. Save | name="Updated NIC Service" | Change reflected immediately in services list | | |
| TC-030 | Admin | Delete a service (with confirmation) | 1. Click delete icon 2. Confirm browser dialog | — | Service and its related steps/documents removed (cascade delete via SQLAlchemy relationship) | | |
| TC-031 | Admin | View all registered users | 1. Go to `/admin/users` | — | Table lists all users with name, email, mobile, language, role, join date | | |
| TC-032 | Admin | Add an official government link | 1. Go to `/admin/links` 2. Fill form 3. Submit | title="Test Dept", url="https://test.gov.lk" | Link appears in the list immediately | | |
| TC-033 | Multilingual | Switch UI language to Tamil | 1. Click 🌐 dropdown 2. Select "தமிழ்" | — | Sidebar, dashboard, and all visited pages instantly show Tamil labels | | |
| TC-034 | Multilingual | Switch UI language to Sinhala | 1. Click 🌐 dropdown 2. Select "සිංහල" | — | All UI labels switch to Sinhala | | |
| TC-035 | Multilingual | AI chat responds in selected language (fallback mode) | 1. Switch language to Tamil 2. Ask "NIC" related question | question="NIC எப்படி பெறுவது?" | Fallback answer returned in Tamil (from trilingual `FALLBACK_KB`) | | |
| TC-036 | Multilingual | Language persists across page navigation | 1. Switch to Sinhala 2. Navigate to 3 different pages | — | Language remains Sinhala on every page (stored in Flask `session`) | | |
| TC-037 | Multilingual | Guest (pre-login) language switch on login page | 1. On `/login` page (not logged in) 2. Switch language | — | Login page labels translate without requiring authentication | | |
| TC-038 | Security | Password is hashed in database | 1. Register a user 2. Inspect `users.password` column in MySQL | — | Value is a bcrypt hash (e.g. `$2b$12$...`), never plain text | | |
| TC-039 | Security | File upload size limit (if applicable) | 1. Attempt to upload file >16MB | — | Flask rejects with `413 Request Entity Too Large` (`MAX_CONTENT_LENGTH` config) | | |
| TC-040 | Responsiveness | Sidebar collapses on mobile width | 1. Resize browser to <768px width | — | Sidebar shrinks to icon-only view per CSS media query | | |

---

## 4. Test Summary

| Metric | Count |
|---|---|
| Total Test Cases | 40 |
| Passed | _____ |
| Failed | _____ |
| Blocked/Not Run | _____ |
| Pass Rate | _____% |

---

## 5. Defects Found (fill during actual execution)

| Defect ID | Related TC | Description | Severity | Status |
|---|---|---|---|---|
| | | | | |

---

## 6. Known Limitations (Honest Disclosure)

1. **No automated unit tests** — all testing above is manual/black-box. Future work: add `pytest` + `Flask-Testing` for route-level automated tests.
2. **No CSRF protection** — forms do not yet use Flask-WTF CSRF tokens.
3. **Gemini fallback covers 9 topics only** — NIC, Passport, Birth Certificate, Marriage, Land, Driving License, Police Clearance, Visa, Legal Aid. Questions outside these return a generic default message in fallback mode (by design, not a bug).
4. **No automated translation of admin-entered service content** — services added via Admin Panel (name/description) only display in the language they were typed in; only static UI labels are fully trilingual.

---

## 7. Conclusion

The system was tested across 8 functional modules covering authentication, AI chat (both Gemini and fallback modes), government services, document checklists, admin management, and multilingual switching. All test cases are designed to be re-run by future developers or examiners following the steps and expected results listed above.
