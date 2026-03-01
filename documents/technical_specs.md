# ShareSense - Technical Specifications

## 1. Technology Stack

### 1.1 Frontend
*   **Framework:** React (via Vite)
    *   Fast, modern, and standard for web apps.
*   **Language:** TypeScript
    *   Ensures type safety and better code quality.
*   **Styling:** Tailwind CSS
    *   Rapid UI development with utility classes.
    *   Allows for "premium" design implementation easily.
*   **State Management:** React Context API or Zustand (lightweight).
*   **Routing:** React Router.

### 1.2 Backend & Database
**Recommendation: Firebase (Google)**
*   **Authentication:** Firebase Auth (Native Google Sign-in support).
*   **Database:** Firestore (NoSQL).
    *   Real-time updates (users see expenses appear instantly).
    *   Secure (Security Rules standard).
    *   Generous Free Tier (Spark Plan).
*   **Why not Google Sheets?**
    *   While possible, using Google Sheets as a backend for a multi-user app introduces latency, concurrency issues, and complex security handling.
    *   Firebase provides a "serverless" experience that feels like a real app and is still free to host for small scale.

### 1.3 Hosting
*   **Provider:** Firebase Hosting (or Vercel).
    *   Free SSL.
    *   Fast global CDN.
    *   One-command deployment.

## 2. Data Model (Firestore Schema Proposed)

### `users` (collection)
*   `uid` (string)
*   `displayName` (string)
*   `email` (string)
*   `photoURL` (string)

### `groups` (collection)
*   `id` (string)
*   `name` (string)
*   `members` (array of user UIDs)
*   `createdBy` (user UID)
*   `createdAt` (timestamp)

### `expenses` (collection)
*   `id` (string)
*   `groupId` (string)
*   `payerId` (string)
*   `amount` (number)
*   `description` (string)
*   `date` (timestamp)
*   `splitAmong` (array of user UIDs)

### `settlements` (collection)
*   `id` (string)
*   `groupId` (string)
*   `payerId` (string)
*   `receiverId` (string)
*   `amount` (number)
*   `confirmed` (boolean)

## 3. Development Phases

### Phase 1: Setup
*   Initialize Vite + React project.
*   Configure Tailwind CSS.
*   Set up Firebase project.

### Phase 2: Core Skeleton
*   Implement Google Auth.
*   Create Group CRUD (Create, Read, Update, Delete).

### Phase 3: Expense Logic
*   Add Expense UI.
*   Implement split logic (Backend/Frontend calculation).
*   Build Balance Dashboard.

### Phase 4: Polish
*   UI/UX improvements (animations, glassmorphism).
*   Testing and Bug fixes.
