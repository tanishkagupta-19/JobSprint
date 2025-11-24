# 0-Day Job Hunter

A full-stack web application that finds job listings posted on LinkedIn within the last 24 hours.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install fastapi uvicorn requests beautifulsoup4
    ```

2.  **Run Backend**:
    ```bash
    uvicorn server:app --host 0.0.0.0 --port 5000
    ```

3.  **Run Frontend**:
    Open `index.html` in your browser.

## Usage

1.  Enter a Job Title and Location.
2.  Click "Find Fresh Jobs".
3.  Download the results as CSV.
