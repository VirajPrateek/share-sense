# ShareSense - Requirements Document

## 1. Project Overview
**Name:** ShareSense
**Purpose:** A lightweight, simple web application for roommates and groups to track shared expenses and settle debts.
**Platform:** Web Application (Mobile Responsible)

## 2. Core Features

### 2.1 User Authentication
*   **Google Sign-In:** Users can sign in using their existing Google accounts for ease of access.
*   **Profile:** Basic profile with name and email (pulled from Google).

### 2.2 Group Management
*   **Create Group:** Users can create a new group (e.g., "Flat 101", "Trip to Vegas").
*   **Manage Members:**
    *   Add members via email.
    *   Members can join or leave groups.
    *   Deactivate members (soft delete, keeping history).

### 2.3 Expense Tracking
*   **Add Expense:**
    *   Description (What was bought?)
    *   Amount (How much?)
    *   Payer (Who paid?)
    *   Date (When?)
*   **Splitting Logic (MVP):**
    *   Split equally among all active members of the group.
    *   *Future:* Unequal splits, shares, specific people.

### 2.4 Balances & Settlement
*   **Dashboard:** View current balances (e.g., "You owe Alice $50", "Bob owes you $20").
*   **Date Range Filter:** Filter expenses and balances by date.
*   **Settle Up:**
    *   Record a payment (Person A paid Person B).
    *   Confirmation mechanism (optional for MVP, but good practice).
    *   Resets the debt cycle for those specific transactions.

## 3. User Experience (UX)
*   **Design:** Modern, clean, and "premium" feel. Vibrant colors, smooth transitions.
*   **Simplicity:** Minimal clicks to add an expense.
*   **Responsiveness:** Must work perfectly on mobile browsers since users will likely add expenses on the go.

## 4. Constraints & Assumptions
*   **Free Hosting:** The project aims to run on zero-cost infrastructure.
*   **Connectivity:** Requires internet access.
