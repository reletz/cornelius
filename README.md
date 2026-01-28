# Cornell Notes Generator

Transform lecture materials into detailed Cornell-style notes using AI.

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <repo-url>
cd cornell-notes

# Start the application
docker compose up -d

# Access at http://localhost:8000
```

### Development Mode

```bash
# Start with hot reloading
docker compose -f docker-compose.dev.yml up

# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
```

## 🔧 Manual Setup

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## 📋 Features

- **Multi-format Support**: PPTX, PDF, DOCX, PNG, JPG
- **AI-Powered Clustering**: Automatic topic detection using Gemini
- **Cornell Notes Generation**: Structured notes with Questions, Main Notes, Summary, and Ad Libitum sections
- **Export Options**: Markdown (Obsidian-compatible) and PDF
- **GitHub Sync**: Push notes directly to your repository
- **BYOK**: Bring Your Own Key - your API key stays in your browser

## 🔑 API Key

This application uses the **Bring Your Own Key (BYOK)** model:

1. Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Enter it when prompted on first use
3. Your key is stored locally in your browser and never sent to our servers

## 📁 Project Structure

```
cornell-notes/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Config, database, security
│   │   ├── models/        # Database models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── services/      # Business logic
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── store/         # Zustand store
│   │   └── lib/           # Utilities and API
│   └── package.json
├── docker-compose.yml     # Production
├── docker-compose.dev.yml # Development
└── Dockerfile
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/config/validate-key` | Validate Gemini API key |
| POST | `/api/sessions/` | Create new session |
| POST | `/api/upload/` | Upload files |
| GET | `/api/upload/{session_id}` | List documents |
| POST | `/api/clusters/analyze/{session_id}` | Analyze and cluster |
| POST | `/api/generate/` | Generate notes |
| GET | `/api/export/{session_id}/markdown` | Export as ZIP |
| GET | `/api/export/{session_id}/pdf` | Export as PDF |

## 📄 License

MIT License
