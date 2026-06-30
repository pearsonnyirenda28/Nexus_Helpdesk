# NexusDesk — IT Help Desk & VoIP Tracking System

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-green)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-336791)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**NexusDesk** is a full‑featured Django web application for IT departments to manage support tickets, track VoIP calls with caller ID, monitor call duration, and maintain a complete audit trail of all system activity.

---

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Quick Start (Development)](#quick-start-development)
- [Production Setup](#production-setup)
  - [1. PostgreSQL Database](#1-postgresql-database)
  - [2. Environment Configuration](#2-environment-configuration)
  - [3. Static Files & Migrations](#3-static-files--migrations)
  - [4. Run with Gunicorn](#4-run-with-gunicorn)
  - [5. Nginx Reverse Proxy](#5-nginx-reverse-proxy)
- [Security Best Practices](#security-best-practices)
- [VoIP Integration](#voip-integration)
- [User Roles](#user-roles)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

---

## Features

| Module | Capabilities |
|--------|--------------|
| **Ticket Management** | Create, assign, prioritise, resolve; SLA tracking; overdue alerts |
| **VoIP Call Tracking** | Caller ID, caller name, call duration (talk/ring/hold), live call board |
| **Caller Directory** | Known caller profiles, call history per number, VIP/blocked flags |
| **Live Dashboard** | Real‑time stats, charts, active call counters, agent workload |
| **Reports** | Period reports, agent performance, priority/source breakdown |
| **Audit Trail** | Immutable log of every action — logins, status changes, assignments |
| **Role‑based Access** | Superuser / IT Staff / User roles |

---

## Technology Stack

- **Backend**: Django 4.2 + Python 3.10–3.12
- **Database**: PostgreSQL 14+ (recommended) / SQLite (dev) / MySQL 8+
- **Server**: Gunicorn + Nginx (production)
- **VoIP**: SIP / Asterisk webhook integration
- **Frontend**: Bootstrap 5, Chart.js, FontAwesome

> PostgreSQL is strongly recommended for production because NexusDesk uses `JSONField` for audit change records, and PostgreSQL’s native JSONB gives the best query performance and indexing support for audit trail searches.

---

## Quick Start (Development)

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12
- pip
- Git (optional)

### 2. Clone and set up virtual environment

**Windows (PowerShell):**
```powershell
git clone https://github.com/pearsonnyirenda28/Nexus_Helpdesk.git
cd Nexus_Helpdesk

python -m venv venv
.\venv\Scripts\Activate.ps1
# If blocked by execution policy, run once:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser