# Document Q&A Agent

A Retrieval-Augmented Generation (RAG) application that accepts documents and answers questions using only information found in the uploaded document.

The application supports follow-up questions, source-grounded answers, OCR for images and scanned PDFs, and the required fallback response when information is unavailable.

## Features

- Upload PDF, TXT, PNG, JPG and JPEG files
- Extract text from normal PDFs and text files
- Apply Tesseract OCR to images and scanned PDFs
- Split documents into overlapping text chunks
- Generate local embeddings using `all-MiniLM-L6-v2`
- Store and retrieve document chunks using ChromaDB
- Generate grounded answers through OpenRouter
- Maintain conversation context for follow-up questions
- Reject questions whose answers are unavailable
- Vue-based upload and chat interface
- Automated API tests

## Technology Stack

### Frontend

- Vue 3
- Vite
- Tailwind CSS
- Axios
- Lucide Vue icons

### Backend

- Python
- FastAPI
- LangChain
- PyMuPDF
- Tesseract OCR
- Pytesseract
- Pillow
- Sentence Transformers
- ChromaDB
- OpenRouter

## Project Structure

```text
document-qa-agent/
├── backend/
│   ├── app/
│   ├── chroma_data/
│   ├── .env.example
│   ├── requirements.txt
│   └── test_api.py
├── frontend/
│   ├── src/
│   ├── .env.example
│   └── package.json
├── sample-documents/
├── docs/
├── .gitignore
└── README.md
```

## Prerequisites

Install the following before running the project:

- Python 3.13
- Node.js 24
- Git
- Tesseract OCR
- An OpenRouter API key

## Backend Setup

From the project root:

```powershell
cd backend
python -m venv .venv
```

Activate the virtual environment:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create the environment file:

```powershell
Copy-Item .env.example .env
```

Update `backend/.env`:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=google/gemma-4-26b-a4b-it:free
OPENROUTER_FALLBACK_MODEL=openrouter/free
TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract.exe
```

Never commit the real `.env` file or API key.

## Frontend Setup

Open another terminal:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
```

The frontend environment file should contain:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Running the Application

Start the backend:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

The backend runs at:

```text
http://127.0.0.1:8000
```

API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

Start the frontend in another terminal:

```powershell
cd frontend
npm run dev
```

Open:

```text
http://localhost:5173
```

## Running Tests

From the backend folder:

```powershell
pytest -q
```

The API test suite covers:

- Health endpoint
- Document upload
- Unsupported file rejection
- Question answering
- Invalid sessions

Build and validate the frontend:

```powershell
cd frontend
npm run lint
npm run build
```

## RAG Workflow

```text
Upload document
→ Extract text or apply OCR
→ Split text into chunks
→ Generate embeddings
→ Store chunks in ChromaDB
→ Retrieve relevant chunks
→ Generate a grounded LLM answer
→ Update conversation history
```

## Fallback Behaviour

If the answer is unavailable, the application returns:

```text
The information is not available in the provided document.
```

## Current Limitations

- Conversation sessions are stored in memory and reset when FastAPI restarts.
- ChromaDB is stored locally.
- OCR currently uses English language recognition.
- OpenRouter free models may have availability and rate limits.
- The retrieval-distance threshold is provisional and may require tuning for larger documents.

## Security

- API keys are stored only in `backend/.env`.
- `.env` files are excluded through `.gitignore`.
- `.env.example` contains placeholders only.
- Uploaded documents are processed locally and are not committed to Git automatically.
