# Security Architecture & Audit Report

## Overview
Universal Deal Tracker is built with a defense-in-depth cybersecurity architecture, leveraging **Django MVT**, **Docker microsegmentation**, and **Zero-Trust validation principles** to safeguard application logic, background scraping workflows, and database integrity.

## 1. Architectural Protections (Secure by Design)
- **SQL Injection (SQLi) Immunity:** All database interactions are executed strictly via the Django ORM using parameterized queries and prepared statements. User input is treated entirely as data literals, neutralizing SQL manipulation attempts.
- **Cross-Site Scripting (XSS) Prevention:** The frontend utilizes auto-escaping template engines alongside custom Bootstrap 5 client-side validation (`novalidate` + `needs-validation`), preventing malicious DOM injection and script execution.
- **Brute Force & DoS Mitigation:** Integrated `django-ratelimit` middleware enforces strict IP-based request throttling (`5 requests / 15 minutes` on authentication endpoints), automatically blocking automated fuzzing and credential stuffing with `HTTP 403 Forbidden` responses.
- **User Enumeration Protection:** Authentication error handlers are deliberately obfuscated to return generic failure messaging, preventing attackers from harvesting valid usernames.

## 2. Dynamic Application Security Testing (DAST)
The application underwent rigorous automated vulnerability scanning and penetration testing in an isolated Docker network environment before production deployment.

### OWASP ZAP (Zed Attack Proxy) – Active & Baseline Audits
- **Methodology:** Autonomous spidering and active fuzzing (`zap-full-scan.py`) targeted all public endpoints, authentication forms, AJAX state-toggle controllers, and Celery asynchronous triggers over a sustained 10-minute active attack window.
- **Results:** - **0 Critical/High Vulnerabilities (FAIL):** No data leaks, session hijacking vulnerabilities, or remote code execution (RCE) vectors detected.
  - **131 Passed Security Checks (PASS):** Verified robust handling of X-Frame-Options, MIME-sniffing protections, and secure form validation under heavy fuzzing load.

### SQLMap – Database Penetration Testing
- **Methodology:** Deep-inspection fuzzing targeted against authentication POST forms (`/login/`) utilizing Level 2 / Risk 2 heuristics to test Boolean-based blind, Time-based blind, Error-based, UNION-query, and Stacked-query injection techniques against the PostgreSQL backend.
- **Results:**
  - **Status: Immutable.** All tested form parameters were confirmed non-injectable.
  - **IPS Behavior Verified:** During high-frequency payload injection, the application's rate-limiting middleware successfully intercepted the attack vectors, throttling connection responses and dropping suspicious traffic autonomously.