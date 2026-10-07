# Bulk Certificate Generator Backend

## Setup and Run
1. Create a virtual environment: `python3 -m venv venv`
2. Activate it: `source venv/bin/activate`
3. Install dependencies: `pip install fastapi uvicorn sqlalchemy pandas openpyxl reportlab python-multipart pytest httpx`
4. Run the server: `uvicorn main:app --reload`

## How to Use (via Swagger UI)
A sample Excel file (`recipients.xlsx`) is included in the repository. It contains the required column `name`, as well as optional `course` and `date` columns for reference.

1. Start the server and open your browser to the interactive API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
2. **Submit a Generation Job**:
   * Click on the `POST /api/jobs` row to expand it.
   * Click the **Try it out** button.
   * Upload the provided `recipients.xlsx` file and click **Execute**.
   * Scroll down to the Server Response and copy the `job_id` string from the JSON body.
3. **Check Job Status & Progress**:
   * Click on the `GET /api/jobs/{job_id}` row to expand it.
   * Click **Try it out**.
   * Paste your copied `job_id` into the field and click **Execute**.
   * The response will display the real-time progress, overall job status, and an array of individual generation results. 
   * Locate a successful generation in the `details` list and copy its `cert_id`.
4. **Retrieve a Generated Certificate**:
   * Click on the `GET /api/certificates/{cert_id}` row to expand it.
   * Click **Try it out**.
   * Paste the `cert_id` and click **Execute**.
   * Click the **Download file** link in the response body to view the final PDF.

## Run Tests
Run `pytest` in the terminal to execute the test suite.

## Design Decisions
* **Background Tasks**: Used FastAPI's built-in `BackgroundTasks` instead of Celery to handle asynchronous bulk generation efficiently without requiring external message brokers like Redis.
* **Database Choice**: Used SQLite for a zero-configuration relational database setup that tracks the granular status of each certificate.
* **Failure Handling**: Wrapped individual row generation in a `try/except` block so that one invalid recipient does not stop the entire batch from processing.