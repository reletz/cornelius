# Cornell Notes Generator - Software Requirements Specification

Version: 2.1 (BYOK Edition)  
Date: 2026-01-28

## 1. Executive Summary

### 1.1 Product Overview
A web-based application that automates the generation of detailed Cornell-style notes from multiple academic documents (PPT, PDF, DOCX). The system processes uploaded documents through a localized OCR pipeline, intelligently clusters content using LLMs, and generates comprehensive markdown notes.

### 1.2 Target Users
University students (primarily Computer Science) who need to process multiple lecture materials into structured study notes efficiently.

### 1.3 Core Value Proposition
Transform lecture materials into detailed Cornell notes instantly using a single, portable, lightweight Docker container.  
Plug-and-Play: No complex infrastructure setup required.  
Bring Your Own Key (BYOK): Users securely input their own AI API Key via the UI, ensuring privacy and control over usage costs.

## 2. System Architecture

### 2.1 Deployment Environment
- Delivery: Single Docker Image (cornell-notes:latest).
- Orchestration: Docker Compose (Single Service).
- Database: SQLite (Embedded, zero-configuration, file-based).
- Backend: Python FastAPI.
- Frontend: React + Tailwind CSS (Built as static assets served by FastAPI).
- Queue System: Python asyncio BackgroundTasks (In-memory).
- File Storage: Local volume bind mount.

### 2.2 External & Internal Dependencies
- LLM Provider: Google Gemini API (Model: gemini-1.5-flash for high-throughput tasks, gemini-1.5-pro for reasoning). Key provided by user via UI.
- PDF Engine (Internal): WeasyPrint (Python library for HTML-to-PDF rendering).
- OCR Engine (Internal):
  - python-pptx: Direct text extraction for presentations.
  - pypdfium2: Direct text extraction for digital PDFs.
  - Tesseract (Optimized): Fallback for scanned images (English/Indonesian only) via Python wrapper.
- GitHub API: For optional vault synchronization.

## 3. Functional Requirements

### 3.1 Document Upload and Processing

#### 3.1.1 File Upload Interface
- Support multiple file upload (drag-and-drop).
- Supported formats: PPTX, PDF, DOCX, PNG, JPG.
- File size limit: 50MB per file.
- Constraint: Files are stored temporarily in the localized Docker volume and cleaned up after session expiry.

#### 3.1.2 OCR Pipeline (Local-First Strategy)
The system utilizes a tiered extraction strategy to minimize resource usage:  
Tier 1 (Direct Extraction): Attempt to extract text using python-pptx (for slides) or pypdfium2 (for digital PDFs). This is CPU-inexpensive and fast.  
Tier 2 (Local OCR Fallback): If Tier 1 yields insufficient text (scanned documents/images), utilize local Tesseract.  
Optimization: Docker image includes only minimal Tesseract binaries and language data (ENG/IND) to maintain a small footprint.  
Tier 3 (LLM Cleanup): Raw text output is sent to Gemini during the clustering/generation phase with instructions to fix OCR typos and formatting errors.

#### 3.1.3 Error Handling
- Detect corrupted files immediately.
- Timeout protection (max 5 minutes per file for OCR).
- Graceful degradation: If a slide cannot be read, log a warning and proceed to the next.

### 3.2 Content Clustering

#### 3.2.1 Automatic Topic Detection
- Analyze extracted text using Gemini API.
- Identify 3-7 coherent subtopics based on semantic similarity.
- Output JSON structure containing Cluster ID, Title, Source Mapping, and Estimated Word Count.

#### 3.2.2 Cluster Review Interface
- Display detected clusters.
- Allow users to Edit Title, Merge Clusters, Split Clusters, or Delete Clusters.
- Default action: "Generate All".

### 3.3 Cornell Notes Generation

#### 3.3.1 Generation Process
- The backend accepts the Gemini API Key from the frontend request header for every generation call. The key is never stored permanently in the database, only in the user's browser session/local storage.
- Use prompts embedding the "Cornell Master" persona and specific Cornell Markdown formatting.
- Process generation asynchronously using FastAPI BackgroundTasks.
- Concurrency: Limited to 2 concurrent generation tasks per container to prevent memory spikes on low-end host machines.

#### 3.3.2 Cornell Note Template & Validation
Maintains strict adherence to the Markdown structure defined in the original requirements, including Questions/Cues, Reference Points, detailed explanations, Summary, and mandatory Ad Libitum section.

### 3.4 Export and Synchronization

#### 3.4.1 Export Formats
- Markdown (Primary): Obsidian-compatible, zipped.
- PDF (Secondary): Generated internally via WeasyPrint.

#### 3.4.2 PDF Generation (Internal)
Instead of relying on external microservices, the system renders PDFs locally:  
Convert Markdown to HTML.  
Inject "Print-CSS" optimized for A4 paper (margins, font sizing, page breaks).  
Invoke WeasyPrint to render HTML to PDF bytes in-memory.  
Stream result to user.

#### 3.4.3 GitHub Integration
- Direct API calls to push generated Markdown files to a user-specified repository path.
- Requires User PAT (Personal Access Token).

## 4. Non-Functional Requirements

### 4.1 Performance (Lightweight Context)
- Startup Time: Container ready in < 5 seconds.
- Resource Footprint: Target idle memory usage < 200MB.
- OCR Speed: Text-based PDF extraction < 1 second/page. Image-based OCR < 3 seconds/page.

### 4.2 Portable Scalability
Designed for vertical scaling (single larger instance) rather than horizontal orchestration.  
Database file (SQLite) handles up to 10 concurrent write operations comfortably, sufficient for individual or small-team use.

### 4.3 Reliability & Security
- Data Persistence: SQLite database file and uploads/ directory must be mounted to the host.
- Secret Management: API Keys are NOT stored in the backend DB. They are passed from Client -> Server on each sensitive request or stored in an ephemeral, encrypted session cookie.

## 5. User Interface Specifications

### 5.1 Page Flow
- Step 0: Configuration (New): Modal/Card asking for Gemini API Key. Option to "Save locally" (localStorage) so user doesn't re-enter every time. Validation check (ping Gemini API) before proceeding.
- Step 1: Upload: Drag-and-drop interface.
- Step 2: Processing: Progress bars for OCR.
- Step 3: Clustering: Review and edit topic clusters.
- Step 4: Generation: Status indicators for note creation.
- Step 5: Review & Export: Preview notes and download buttons.

### 5.2 Visual Design
- Framework: Tailwind CSS.
- Theme: Clean, academic, distraction-free.
- Responsiveness: Functional on Desktop and Tablet.

## 6. Data Models (SQLite Schema)
All tables reside in a single cornell.db SQLite file.  

Tables:  
- users: id (TEXT/UUID), github_config (JSON), created_at (DATETIME). Note: API Keys are NOT stored here.  
- sessions: id (TEXT/UUID), user_id (TEXT), status (TEXT), created_at (DATETIME).  
- documents: id (TEXT), session_id (TEXT), filename (TEXT), file_path (TEXT), extracted_text (BLOB/TEXT), status (TEXT).  
- clusters: id (TEXT), session_id (TEXT), title (TEXT), sources_json (JSON).  
- notes: id (TEXT), cluster_id (TEXT), markdown_content (TEXT), created_at (DATETIME).

## 7. API Specifications

### 7.1 Key Endpoints
- POST /api/config/validate-key: Validate the user-provided Gemini API Key.
- POST /api/upload: Multipart upload.
- POST /api/process: Trigger async extraction.
- POST /api/generate: Trigger note generation. Header: X-Gemini-Key: <user_key>.
- GET /api/export/{session_id}/pdf: Returns PDF stream.

## 8. Deployment Configuration (The "Ship" Strategy)

### 8.1 Dockerfile Structure
Multi-stage build to ensure the final image remains minimal (~300MB-400MB).

```dockerfile
# Stage 1: Build Frontend
FROM node:18-alpine as frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Stage 2: Runtime Backend
FROM python:3.11-slim-bookworm
WORKDIR /app

# Install System Dependencies
# - WeasyPrint needs: libpango, libpangoft2, libjpeg, zlib
# - Tesseract needs: tesseract-ocr-core and specific language packs (ENG/IND)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    tesseract-ocr-core \
    tesseract-ocr-eng \
    tesseract-ocr-ind \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Frontend Static Files
COPY --from=frontend-build /app/frontend/dist /app/static

# Copy Application Code
COPY . .

# Environment Configuration
ENV DATABASE_URL="sqlite:///./data/cornell.db"
ENV TESSDATA_PREFIX="/usr/share/tesseract-ocr/5/tessdata/"
ENV PORT=8000

# Mount Point for Persistence
VOLUME ["/app/data"]

# Entrypoint
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 8.2 Docker Compose (User Interface)
The end-user distribution file. Note: GEMINI_API_KEY is removed from mandatory env vars.

```yaml
version: '3.8'
services:
  cornell-notes:
    image: your-registry/cornell-notes:latest
    container_name: cornell-notes
    ports:
      - "8000:8000"
    volumes:
      - ./cornell_data:/app/data
    environment: []
      # Optional: Pre-fill key if running in a trusted private environment
      # - GEMINI_API_KEY=your_key_here 
    restart: unless-stopped
```

## 9. Success Metrics

- **Deployment Success:** Users can start the app with a single `docker compose up` command without errors.
- **PDF Generation:** 100% accurate rendering of the Cornell layout without external API calls.
- **OCR Reliability:** Capable of handling mixed-media inputs (PPTX + Scanned PDF) in a single batch without crashing the container.