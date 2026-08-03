# Pogo-Pin Monitoring System (PPM V5)

A desktop application for tracking pogo-pin replacement and maintenance activities for loadboards and probecards, with role-based access, historical review, and reporting.

![Python](https://img.shields.io/badge/python-3.x-blue.svg) ![PyQt](https://img.shields.io/badge/PyQt-6.x-green.svg) ![SQLite](https://img.shields.io/badge/database-SQLite-lightgrey.svg)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [First-Time Setup](#first-time-setup)
- [Usage](#usage)
  - [Login](#login)
  - [New Item View](#new-item-view)
  - [History View](#history-view)
  - [SAP View](#sap-view)
  - [Extract Data View](#extract-data-view)
- [Application Flow](#application-flow)
- [Database Structure](#database-structure)
- [Key Classes and Functions](#key-classes-and-functions)
- [Dependencies](#dependencies)
- [Notes](#notes)
- [Contact](#contact)

---

## Overview

The Pogo-Pin Monitoring System is a lightweight desktop tool for monitoring pogo-pin replacement work. It provides:

- A central SQLite database for maintenance records and SAP master data.
- User authentication and restricted admin features.
- Data entry for replacement transactions, including BHW, SAP, quantity, site, and remarks.
- History browsing with date and BHW filters.
- Data analysis through charts for usage and cost trends.

---

## Features

- Secure login and account management.
- Maintenance form for recording replacement events.
- Auto-complete support for loadboard and SAP values.
- Run-count lookup for BHW entries.
- SAP master-data maintenance for pricing and part details.
- Historical record review with filtering and copy support.
- Graph generation for BHW, SAP, and contributor trends.
- Notification support, update checks, and themed UI styling.

---

## Installation

1. Clone or download this repository.
2. Install the required Python dependencies.

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python PPM_V5.py
```

> The application expects its shared resource paths and database location to be configured correctly in libs/GlobalVariables.py.

---

## First-Time Setup

On first run, the application creates and uses an SQLite database file named POGOINSERTION.db. The required tables are created automatically through the database connector module.

The main tables include:

- LOADBOARDS
- POGOINSERTION
- CREDENTIALS
- SAPNUMBER
- RECEPINENTS
- OLD_VERSION
- ANNOUNCEMENT
- E100_USER
- THEME

---

## Usage

### Login

- Open the application from PPM_V5.py.
- Use the Account menu to log in or manage account credentials.
- Successful login enables access to admin-restricted functions.

### New Item View

- Enter the BHW name, replacement date, SAP number, run count, quantity, price, site, replacement user, and remarks.
- The form supports auto-complete for BHW and SAP values.
- Saving the form writes the record to the main maintenance table.

### History View

- Review all saved records from the History tab.
- Filter by BHW name or date range.
- Copy selected rows to the clipboard for reporting or sharing.

### SAP View

- Manage SAP master data and price details.
- Add, edit, or delete SAP records.
- This view is restricted to users with admin access.

### Extract Data View

- Select a timeframe and graph mode.
- Generate charts for:
  - BHW serial usage
  - SAP number usage
  - SAP contributor analysis

---

## Application Flow

```text
Start
  │
  ▼
Login / Account Setup
  │
  ▼
Main Window
  ├── New Item
  ├── SAP
  ├── History
  └── Extract Data
```

- The app starts from PPM_V5.py and creates the main window.
- User actions update the database and refresh the related views.
- Reporting and history views are built from the stored transaction records.

---

## Database Structure

| Table | Purpose |
|------|---------|
| LOADBOARDS | Stores loadboard names used in the maintenance form. |
| POGOINSERTION | Main transaction table for pogo-pin replacement records. |
| CREDENTIALS | Stores user credentials and access level information. |
| SAPNUMBER | Stores SAP master data, price, and part-number details. |
| RECEPINENTS | Holds email recipient configuration for notifications. |
| OLD_VERSION | Tracks previous application versions. |
| ANNOUNCEMENT | Stores announcement text shown in the app. |
| E100_USER | Maps E100 user IDs to user names. |
| THEME | Stores user-specific theme preference. |

---

## Key Classes and Functions

- PogoPinMonitoring – main window controller and navigation shell.
- AddNew – maintenance form for new replacement records.
- SAPEdit – SAP master-data editor for admin use.
- History – historical record browser with filtering.
- DataGraphing – chart generation and analysis view.
- LoginDialog – login, add-user, and password-change dialog.
- DatabaseConnector – SQLite helper for schema creation and CRUD operations.
- GlobalState – shared version and path configuration.

---

## Dependencies

- Python 3.x
- PyQt6
- SQLite3 (built-in)
- matplotlib
- numpy
- pandas
- Pillow
- requests
- pywin32
- oracledb
- seaborn
- nltk

---

## Notes

- Current application version: 5.1.0
- This project is still under active development and may be refined further over time.

---

## Contact

For support or questions, contact:

Oliver Feronel

Email: oliver.feronel@ams.com
