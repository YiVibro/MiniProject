# StudySpark AI - Your AI Study Companion

Welcome to **StudySpark AI**, a comprehensive, AI-powered learning platform designed to transform how you study. StudySpark AI provides dynamic course generation, interactive tutoring sessions, smart goal tracking, and personalized study plans, all driven by advanced LLM technology.

## 🌟 Key Features

*   **Dynamic Course Generation:** Simply enter what you want to learn in natural language (e.g., "I want to learn Python for 3 months with weekly tests"), and the system generates a personalized, multi-lesson curriculum.
*   **Interactive AI Tutoring:** Engage with a context-aware AI tutor during your lessons. Ask questions, request examples, or get practice problems on the fly.
*   **Smart Goal Tracking:** Track your progress visually as you complete lessons and quizzes.
*   **Authentication & Profiles:** Secure authentication via Google OAuth and Supabase, with personalized user profiles.
*   **Gamification Dashboard:** Stay motivated with a gamified learning experience.
*   **Modern Workspace:** Includes a text editor, notes section, and rich markdown support.

## 🏗️ Architecture

The project is structured as a modern full-stack web application:

*   **Frontend (Vite / React):**
    *   Framework: React with TypeScript.
    *   Styling: Tailwind CSS and Shadcn UI components for a beautiful, responsive, and accessible interface.
    *   State/Data: React Query for efficient data fetching, and Zustand/Context for local state.
    *   Animations: Framer Motion for smooth micro-interactions.
*   **Backend (FastAPI):**
    *   Framework: FastAPI (Python) for high-performance, asynchronous REST endpoints.
    *   AI Integration: Uses `langgraph` and `google-generativeai` (Gemini Pro) to orchestrate the multi-agent AI tutoring and planning system.
    *   Database & Auth: Supabase for PostgreSQL database management and user authentication.

---

## 🚀 Getting Started

Follow these instructions to get the project running locally on your machine.

### Prerequisites

*   **Node.js** (v18+ recommended)
*   **Python** (v3.10+ recommended)
*   **Supabase** account (for authentication and database)
*   **Google Gemini API Key** (for AI features)

### 1. Backend Setup

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```
2.  Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure Environment Variables:
    Create a `.env` file in the `backend` directory with the following variables:
    ```env
    # Supabase Credentials
    SUPABASE_URL=your_supabase_url
    SUPABASE_KEY=your_supabase_key
    
    # Session/OAuth
    SECRET_KEY=your_secret_key
    SESSION_SAMESITE=none
    SESSION_HTTPS_ONLY=false
    
    # Frontend URL for CORS
    FRONTEND_ORIGINS=http://localhost:5173
    
    # AI Config
    GOOGLE_API_KEY=your_gemini_api_key
    ```
5.  Run the FastAPI server:
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    The backend API will be available at `http://localhost:8000`.

### 2. Frontend Setup

1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Configure Environment Variables (if required, though development defaults proxy to `localhost:8000`).
4.  Run the development server:
    ```bash
    npm run dev
    ```
    The frontend will be available at `http://localhost:5173`.

---
## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
