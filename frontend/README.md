# Medical AI Assistant Frontend

Simple React console for testing the Secure Multimodal Medical AI backend.

## Run

```powershell
cd frontend
npm install
npm run dev
```

Default URL:

```text
http://127.0.0.1:5173
```

## Configure API URL

Create `.env` from `.env.example`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Features

- Login and register
- Create and select patients
- Create chat sessions
- Upload PDF/image reports
- Preview protected uploaded files
- View extracted OCR/PDF text
- Trigger document embedding
- Search documents semantically
- Chat with source citations and latency trace
