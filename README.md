Web application that finds job listings posted on LinkedIn within the last 24 hours.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install fastapi uvicorn requests beautifulsoup4
    ```

2.  **Run Backend**:
    ```bash
    python server.py
    ```

3.  **Run Frontend**:
    Open `index.html` in your browser.

## Usage

1.  Enter a Job Title (e.g., "Python Developer") and Location.
2.  Click "Find Fresh Jobs".
3.  View the list of jobs posted in the last 24 hours.
4.  See the "Trending Skills" analysis based on the job titles found.
5.  Click "Quick Apply" to jump to the job posting.
