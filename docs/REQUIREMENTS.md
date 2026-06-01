# REQUIREMENTS.md
# Conversational RAG Platform — Software Requirements Specification

**Version:** 1.0.0
**Status:** Approved for Implementation
**Audience:** Engineering, Product, Architecture Review

---

## Table of Contents

1. Executive Summary
2. Project Vision
3. Product Goals
4. User Personas
5. User Journeys
6. User Stories
7. Functional Requirements
8. Non-Functional Requirements
9. Technical Requirements
10. Security Requirements
11. Data Requirements
12. UI Requirements
13. Accessibility Requirements
14. Deployment Requirements
15. Performance Requirements
16. Error Handling Requirements
17. Logging Requirements
18. Monitoring Requirements
19. Scalability Considerations
20. Risks and Mitigations
21. Success Metrics
22. Acceptance Criteria

---

## 1. Executive Summary

This document specifies the complete requirements for a production-style Conversational Retrieval-Augmented Generation (RAG) platform. The system allows users to upload one or more PDF documents and interact with their content through a natural language chat interface. The platform performs semantic retrieval over document content, generates context-grounded responses using a large language model, and presents source citations with page references.

The application is intended for portfolio, internship, educational, and demonstration use cases. It must be fully deployable on free-tier infrastructure, publicly accessible after deployment, and maintainable by a single developer. The interface must follow a Neo-Brutalist design language.

All requirements in this document are traceable to tasks in TASKS.md and to design decisions in DESIGN.md.

---

## 2. Project Vision

Build an accessible, fully deployable AI document assistant that allows users to upload PDF documents and converse with their content using natural language. The application must feel like a real product rather than a tutorial project, demonstrating production-quality architecture while remaining simple enough for a single developer to implement and maintain.

The system must operate entirely on free-tier tools, APIs, and infrastructure, with zero paid services required for deployment or operation.

---

## 3. Product Goals

| ID | Goal | Priority |
|----|------|----------|
| G-01 | Enable users to upload and query PDF documents through natural language chat | Critical |
| G-02 | Provide source-grounded answers with page-level citations | Critical |
| G-03 | Maintain conversation history within a session | Critical |
| G-04 | Support multiple documents in a single session | High |
| G-05 | Deploy publicly with zero cost using free-tier services | Critical |
| G-06 | Present a polished Neo-Brutalist interface | High |
| G-07 | Provide streaming responses for perceived performance | High |
| G-08 | Allow document management within a session | Medium |
| G-09 | Enable users to export their chat history | Medium |
| G-10 | Support dark and light theme switching | Low |

---

## 4. User Personas

### 4.1 Persona: Research Student

**Name:** Priya  
**Background:** Graduate student, reads academic papers and technical reports  
**Goals:** Quickly extract answers from dense documents without reading every page  
**Pain Points:** Spending hours manually scanning PDFs for specific information  
**Technical Level:** Moderate — comfortable with web applications  
**Device:** Desktop browser, occasionally mobile  

### 4.2 Persona: Junior Developer / Portfolio Builder

**Name:** Alex  
**Background:** Recent CS graduate building a portfolio for internship applications  
**Goals:** Study the system as a reference implementation; demonstrate capability to recruiters  
**Pain Points:** Existing RAG tutorials are toy examples with no production structure  
**Technical Level:** High — capable of reading code and architecture documents  
**Device:** Desktop browser  

### 4.3 Persona: Non-Technical Professional

**Name:** Marcus  
**Background:** Business analyst working with policy documents, contracts, and reports  
**Goals:** Extract answers from long documents without technical background  
**Pain Points:** Cannot use CLI tools or code-based solutions  
**Technical Level:** Low — web application only  
**Device:** Desktop browser  

### 4.4 Persona: Educator / Instructor

**Name:** Dr. Chen  
**Background:** University instructor using the tool to demonstrate AI capabilities  
**Goals:** Show students how RAG systems work; demonstrate source citation  
**Pain Points:** Most demos are either too complex or too simplistic  
**Technical Level:** Moderate  
**Device:** Desktop browser, projected during lectures  

---

## 5. User Journeys

### 5.1 Journey: First-Time User — Single Document Query

1. User navigates to the public deployment URL
2. User sees the landing interface with upload affordance
3. User uploads a PDF document via drag-and-drop or file picker
4. System processes the document (chunking, embedding, indexing)
5. System indicates processing is complete
6. User types a natural language question in the chat input
7. System retrieves relevant passages, constructs a prompt, and calls the LLM
8. Response streams into the chat interface with source citations
9. User asks follow-up questions; system maintains conversation context
10. User downloads the chat history

### 5.2 Journey: Multi-Document Query

1. User uploads a first PDF and receives processing confirmation
2. User uploads a second PDF; both documents are tracked in the document panel
3. User asks a question that spans both documents
4. System retrieves passages from both, constructs a unified prompt, and responds
5. Citations reference document names and page numbers for both sources
6. User removes one document from the session
7. System continues with only the remaining document

### 5.3 Journey: Document Management

1. User uploads three documents
2. User views the document management dashboard
3. User sees metadata (filename, page count, upload time, chunk count)
4. User removes a document; vector store entries for that document are deleted
5. User uploads a replacement document

### 5.4 Journey: Theme and Export

1. User toggles between dark and light themes
2. User completes a conversation
3. User clicks "Download Chat" and receives a formatted text or JSON file

---

## 6. User Stories

Each user story is linked to functional requirements via FR-XX IDs.

| ID | As a... | I want to... | So that... | Linked FRs |
|----|---------|--------------|------------|------------|
| US-01 | User | Upload one or more PDF files | I can ask questions about their content | FR-01, FR-02 |
| US-02 | User | Drag and drop a PDF onto the upload zone | I don't have to navigate file dialogs | FR-02 |
| US-03 | User | See upload and processing progress | I know the system is working | FR-03 |
| US-04 | User | Type a question in the chat input | I can query the document | FR-06 |
| US-05 | User | Receive a response grounded in document content | I get accurate, verifiable answers | FR-07, FR-08 |
| US-06 | User | See source citations with page references | I can verify answers against the source | FR-09 |
| US-07 | User | Ask follow-up questions | The assistant understands conversation context | FR-10 |
| US-08 | User | See responses stream in real time | The interface feels fast | FR-11 |
| US-09 | User | See a typing indicator while the system processes | I know the system is active | FR-12 |
| US-10 | User | View a list of uploaded documents | I can manage my session | FR-13 |
| US-11 | User | Remove a document from my session | I can control which documents are active | FR-14 |
| US-12 | User | Download my conversation | I can keep a record of my session | FR-15 |
| US-13 | User | Toggle between dark and light themes | I can use the app in different lighting conditions | FR-16 |
| US-14 | User | See how many documents and chunks are active | I understand the system state | FR-17 |
| US-15 | User | Receive an error message if something goes wrong | I know how to proceed | FR-18 |
| US-16 | User | Use the application on a mobile browser | I am not restricted to desktop | NFR-04 |
| US-17 | User | Start a fresh session by clearing all documents | I can start over without refreshing | FR-19 |

---

## 7. Functional Requirements

### 7.1 Document Upload and Ingestion

---

**FR-01: PDF Upload — File Picker**

- **ID:** FR-01
- **Title:** PDF Upload via File Picker
- **Description:** The system must allow users to upload one or more PDF files using a standard file input control.
- **Priority:** Critical
- **Acceptance Criteria:**
  - User can select one or more `.pdf` files from their filesystem
  - Non-PDF files are rejected with an appropriate error message
  - Files larger than the defined size limit are rejected with an appropriate error message
  - Accepted files are transmitted to the backend for processing
- **Dependencies:** FR-03, TR-02

---

**FR-02: PDF Upload — Drag and Drop**

- **ID:** FR-02
- **Title:** PDF Upload via Drag and Drop
- **Description:** The system must provide a drag-and-drop upload zone that accepts PDF files.
- **Priority:** High
- **Acceptance Criteria:**
  - A visually distinct drop zone is present on the interface
  - Dragging a valid file over the zone provides visual feedback
  - Dropping a valid file triggers the upload flow
  - Dragging an invalid file provides a rejection indication
- **Dependencies:** FR-01, FR-03

---

**FR-03: Upload Progress Indication**

- **ID:** FR-03
- **Title:** Upload and Processing Progress
- **Description:** The system must provide visual feedback during upload and document processing.
- **Priority:** High
- **Acceptance Criteria:**
  - A progress indicator appears when upload begins
  - A processing indicator appears when the backend is chunking and embedding the document
  - A success confirmation appears when processing is complete
  - An error message appears if processing fails
- **Dependencies:** FR-01, FR-02

---

**FR-04: PDF Text Extraction**

- **ID:** FR-04
- **Title:** PDF Text Extraction
- **Description:** The backend must extract text content from uploaded PDF documents, including page numbers for each extracted segment.
- **Priority:** Critical
- **Acceptance Criteria:**
  - Text is extracted from all readable pages
  - Page number metadata is preserved with each text segment
  - Scanned/image-only PDFs that cannot yield text produce a clear error message
  - Extracted text is passed to the chunking pipeline
- **Dependencies:** TR-04

---

**FR-05: Document Chunking**

- **ID:** FR-05
- **Title:** Document Chunking
- **Description:** The backend must split extracted text into overlapping chunks suitable for embedding and retrieval.
- **Priority:** Critical
- **Acceptance Criteria:**
  - Text is split into chunks of a defined maximum token/character length
  - Chunks overlap by a defined amount to preserve context across boundaries
  - Each chunk retains metadata: document ID, document name, page number, chunk index
  - Chunks are passed to the embedding pipeline
- **Dependencies:** FR-04

---

**FR-06: Embedding Generation**

- **ID:** FR-06
- **Title:** Embedding Generation
- **Description:** The backend must generate dense vector embeddings for each text chunk using a Sentence Transformer model.
- **Priority:** Critical
- **Acceptance Criteria:**
  - Each chunk produces exactly one embedding vector
  - Embedding dimensionality is consistent across all chunks
  - Embeddings are generated locally without an external API call
  - Generated embeddings are stored in the vector database with associated metadata
- **Dependencies:** FR-05, TR-05

---

### 7.2 Chat and Retrieval

---

**FR-07: Natural Language Query Input**

- **ID:** FR-07
- **Title:** Natural Language Query Input
- **Description:** The system must provide a text input field that accepts natural language queries from the user.
- **Priority:** Critical
- **Acceptance Criteria:**
  - A text input is visible and accessible at all times during an active session
  - The user can submit a query by pressing Enter or clicking a send button
  - The input is cleared after submission
  - The input is disabled while the system is generating a response
- **Dependencies:** FR-06

---

**FR-08: Semantic Retrieval**

- **ID:** FR-08
- **Title:** Semantic Retrieval
- **Description:** The backend must retrieve the most semantically relevant document chunks for each user query.
- **Priority:** Critical
- **Acceptance Criteria:**
  - The user query is embedded using the same model used for document chunks
  - The top-K most similar chunks are retrieved from the vector database (K is configurable)
  - Retrieved chunks include their associated metadata (document name, page number)
  - Retrieval operates across all currently active documents
- **Dependencies:** FR-06, TR-06

---

**FR-09: Context-Grounded Response Generation**

- **ID:** FR-09
- **Title:** Context-Grounded LLM Response
- **Description:** The backend must construct a prompt from retrieved chunks and conversation history, submit it to the Groq LLM API, and return a grounded response.
- **Priority:** Critical
- **Acceptance Criteria:**
  - Retrieved chunks are injected into the system prompt as context
  - Conversation history (up to a defined turn limit) is included in the prompt
  - The LLM is instructed to answer only from provided context
  - The LLM is instructed to state when information is not available in the documents
  - The response is returned to the frontend
- **Dependencies:** FR-08, TR-07

---

**FR-10: Source Citation Display**

- **ID:** FR-10
- **Title:** Source Citations with Page References
- **Description:** The system must display citations alongside each AI response, identifying which document and page each cited passage originates from.
- **Priority:** Critical
- **Acceptance Criteria:**
  - Each response is accompanied by a list of source citations
  - Each citation includes the document filename and page number
  - Citations are visually distinct from the response text
  - Clicking or expanding a citation reveals the raw retrieved passage
- **Dependencies:** FR-08, FR-09

---

**FR-11: Conversation Memory**

- **ID:** FR-11
- **Title:** Conversation History and Memory
- **Description:** The system must maintain conversation history within a session, including prior user messages and assistant responses, and include relevant history in subsequent LLM prompts.
- **Priority:** Critical
- **Acceptance Criteria:**
  - All messages in a session are stored in session state
  - Up to a configurable number of prior turns are included in each new prompt
  - Older turns are truncated gracefully when the context window limit is approached
  - Chat history is rendered in the UI in chronological order
- **Dependencies:** FR-09

---

**FR-12: Streaming Responses**

- **ID:** FR-12
- **Title:** Streaming LLM Responses
- **Description:** The system must stream LLM responses token-by-token (or chunk-by-chunk) to the frontend so that output appears progressively.
- **Priority:** High
- **Acceptance Criteria:**
  - The frontend begins displaying response text before generation is complete
  - Text appears progressively as the LLM generates it
  - The streaming display does not cause layout shifts
  - Citations are displayed after the full response is received
- **Dependencies:** FR-09, TR-07

---

**FR-13: Typing Indicator**

- **ID:** FR-13
- **Title:** Typing / Processing Indicator
- **Description:** The system must display a visual indicator when the backend is processing a query and before the first response token is received.
- **Priority:** High
- **Acceptance Criteria:**
  - An animated indicator appears after query submission
  - The indicator disappears when the first response token is received
  - The indicator is visually distinct from chat messages
- **Dependencies:** FR-12

---

### 7.3 Document Management

---

**FR-14: Document List Display**

- **ID:** FR-14
- **Title:** Document Management Dashboard
- **Description:** The system must display a list of all documents currently active in the session.
- **Priority:** High
- **Acceptance Criteria:**
  - Each document is listed with its filename, page count, chunk count, and upload timestamp
  - The list updates dynamically when documents are added or removed
  - The document list is accessible without leaving the chat interface
- **Dependencies:** FR-01

---

**FR-15: Document Removal**

- **ID:** FR-15
- **Title:** Remove Document from Session
- **Description:** The user must be able to remove a document from the active session, which deletes its vectors from the vector store.
- **Priority:** High
- **Acceptance Criteria:**
  - A remove/delete control is available for each listed document
  - Triggering removal prompts a confirmation
  - On confirmation, the document's vectors are deleted from the vector database
  - The document disappears from the list
  - Subsequent queries do not retrieve from the removed document
- **Dependencies:** FR-14, TR-06

---

**FR-16: Session Clear**

- **ID:** FR-16
- **Title:** Clear All Documents and Reset Session
- **Description:** The user must be able to clear all documents and conversation history to start a fresh session.
- **Priority:** Medium
- **Acceptance Criteria:**
  - A "Clear Session" or equivalent control is available
  - Triggering it removes all vectors from the vector store for the session
  - Conversation history is cleared from session state
  - The interface resets to the initial upload state
- **Dependencies:** FR-14, FR-15

---

### 7.4 Export and Utility

---

**FR-17: Chat History Export**

- **ID:** FR-17
- **Title:** Download Chat History
- **Description:** The user must be able to download the conversation as a file.
- **Priority:** Medium
- **Acceptance Criteria:**
  - A "Download Chat" button is available during or after a conversation
  - The exported file includes all messages with timestamps
  - The export format is either plain text (.txt) or JSON (.json), user-selectable or defaulted to JSON
  - The filename is auto-generated with a timestamp
- **Dependencies:** FR-11

---

**FR-18: Error Display**

- **ID:** FR-18
- **Title:** User-Facing Error Messages
- **Description:** The system must display clear, non-technical error messages when operations fail.
- **Priority:** Critical
- **Acceptance Criteria:**
  - Upload failures display a message explaining the issue (file type, size, processing error)
  - Query failures display a fallback message without exposing stack traces
  - Network errors display a retry prompt
  - All errors are styled consistently with the UI design
- **Dependencies:** All functional requirements

---

**FR-19: Theme Toggle**

- **ID:** FR-19
- **Title:** Dark/Light Theme Switch
- **Description:** The system must provide a toggle allowing users to switch between dark and light interface themes.
- **Priority:** Low
- **Acceptance Criteria:**
  - A theme toggle control is visible and accessible
  - Switching themes updates all interface components immediately
  - The selected theme persists within the session
- **Dependencies:** UIR-01

---

**FR-20: Session Status Display**

- **ID:** FR-20
- **Title:** Session Metadata Display
- **Description:** The interface must display current session status including number of active documents and total chunk count.
- **Priority:** Medium
- **Acceptance Criteria:**
  - Active document count is visible at all times during a session
  - Total indexed chunk count is displayed
  - Metadata updates when documents are added or removed
- **Dependencies:** FR-14

---

## 8. Non-Functional Requirements

---

**NFR-01: Response Latency**

- **ID:** NFR-01
- **Title:** End-to-End Response Latency
- **Description:** The system must return the first response token within an acceptable time after query submission.
- **Priority:** High
- **Acceptance Criteria:**
  - Time-to-first-token must not exceed 5 seconds under normal network conditions
  - Full response delivery must complete within 30 seconds for responses under 500 words
- **Dependencies:** TR-07, PR-01

---

**NFR-02: Document Processing Time**

- **ID:** NFR-02
- **Title:** PDF Processing Latency
- **Description:** Documents must be processed and indexed within a reasonable time after upload.
- **Priority:** High
- **Acceptance Criteria:**
  - A 50-page PDF must be processed within 60 seconds
  - A 200-page PDF must be processed within 180 seconds
  - Processing time per page must not exceed 1.5 seconds on average
- **Dependencies:** TR-04, TR-05

---

**NFR-03: Availability**

- **ID:** NFR-03
- **Title:** Deployment Availability
- **Description:** The deployed application must maintain acceptable uptime for a free-tier portfolio deployment.
- **Priority:** Medium
- **Acceptance Criteria:**
  - The application must be accessible during normal business hours
  - Cold-start delays on free-tier hosting are acceptable but must not exceed 60 seconds
  - Application must not require manual restart to recover from common errors
- **Dependencies:** DR-01, DR-02

---

**NFR-04: Mobile Responsiveness**

- **ID:** NFR-04
- **Title:** Mobile Browser Compatibility
- **Description:** The interface must be usable on mobile browsers without horizontal scrolling or broken layouts.
- **Priority:** High
- **Acceptance Criteria:**
  - Layout adapts to screen widths from 375px upward
  - Chat input and upload affordance are accessible on mobile
  - Text is readable without zooming
- **Dependencies:** UIR-02

---

**NFR-05: Security Baseline**

- **ID:** NFR-05
- **Title:** Basic Security Posture
- **Description:** The system must follow basic security practices appropriate for a portfolio application.
- **Priority:** High
- **Acceptance Criteria:**
  - API keys are never exposed in frontend code or public repositories
  - API keys are loaded from environment variables
  - Uploaded files are not permanently stored unless explicitly designed to be
  - CORS is configured to restrict origins appropriately
- **Dependencies:** SR-01, SR-02

---

**NFR-06: Maintainability**

- **ID:** NFR-06
- **Title:** Code Maintainability
- **Description:** The codebase must be structured and documented such that a single developer can understand and modify any component within a reasonable time.
- **Priority:** High
- **Acceptance Criteria:**
  - Each module has a clear, single responsibility
  - Functions are documented with docstrings
  - No single file exceeds 300 lines of code without structural justification
  - A README provides setup instructions sufficient for a new developer
- **Dependencies:** TR-01

---

**NFR-07: Free-Tier Constraint**

- **ID:** NFR-07
- **Title:** Zero-Cost Operation
- **Description:** The application must operate entirely within free-tier limits of all services used.
- **Priority:** Critical
- **Acceptance Criteria:**
  - No paid API calls are made during normal operation
  - No paid hosting tiers are required for deployment
  - All services used offer a permanent or sufficiently long free tier
  - Usage limits of free tiers are documented and respected
- **Dependencies:** DR-01, DR-02, TR-07

---

## 9. Technical Requirements

---

**TR-01: Backend Framework**

- **ID:** TR-01
- **Title:** FastAPI Backend
- **Description:** The backend must be implemented using FastAPI.
- **Priority:** Critical
- **Acceptance Criteria:**
  - All API endpoints are defined as FastAPI route handlers
  - The application starts via uvicorn
  - OpenAPI schema is auto-generated and accessible at `/docs`
- **Dependencies:** None

---

**TR-02: Frontend Framework**

- **ID:** TR-02
- **Title:** Streamlit Frontend
- **Description:** The frontend must be implemented using Streamlit.
- **Priority:** Critical
- **Acceptance Criteria:**
  - All user-facing UI components are Streamlit components or Streamlit-compatible HTML
  - The Streamlit application communicates with the FastAPI backend via HTTP
- **Dependencies:** None

---

**TR-03: Python Version**

- **ID:** TR-03
- **Title:** Python 3.10+ Compatibility
- **Description:** All backend and frontend code must be compatible with Python 3.10 or higher.
- **Priority:** High
- **Acceptance Criteria:**
  - No deprecated Python 3.9 or earlier APIs are used
  - requirements.txt pins compatible package versions
- **Dependencies:** None

---

**TR-04: PDF Processing Library**

- **ID:** TR-04
- **Title:** PDF Text Extraction
- **Description:** PDF text extraction must be performed using PyMuPDF (fitz) or pdfplumber, with page number metadata preserved.
- **Priority:** Critical
- **Acceptance Criteria:**
  - Library successfully extracts text from standard PDF documents
  - Page number is captured for each page's content
  - The library is installable via pip without system-level dependencies that are unavailable in the deployment environment
- **Dependencies:** FR-04

---

**TR-05: Embedding Model**

- **ID:** TR-05
- **Title:** Sentence Transformer Embeddings
- **Description:** Text embeddings must be generated using a Sentence Transformers model running locally.
- **Priority:** Critical
- **Acceptance Criteria:**
  - The selected model is downloaded and cached locally on first run
  - Embedding generation does not require an external API call
  - The model produces embeddings of a consistent, documented dimensionality
  - The recommended model is `all-MiniLM-L6-v2` (384 dimensions) unless a superior alternative is justified in DESIGN.md
- **Dependencies:** FR-06

---

**TR-06: Vector Database**

- **ID:** TR-06
- **Title:** Vector Storage and Retrieval
- **Description:** Document chunk embeddings must be stored in and retrieved from a vector database. The selected database must be operable within free-tier constraints.
- **Priority:** Critical
- **Acceptance Criteria:**
  - Embeddings are stored with associated metadata
  - Similarity search returns the top-K nearest neighbors for a query vector
  - The selected database is justified in DESIGN.md with a full comparison matrix
  - Document-level filtering is supported for multi-document sessions
- **Dependencies:** FR-06, FR-08

---

**TR-07: LLM Provider**

- **ID:** TR-07
- **Title:** Groq LLM API Integration
- **Description:** Language model inference must use the Groq API. The specific model must be selected based on evaluation documented in DESIGN.md.
- **Priority:** Critical
- **Acceptance Criteria:**
  - API calls are made to the Groq endpoint
  - The API key is loaded from an environment variable
  - Streaming is enabled for all response generation calls
  - A fallback model is configured for when the primary model is unavailable
- **Dependencies:** FR-09, FR-12

---

**TR-08: Configuration Management**

- **ID:** TR-08
- **Title:** Environment-Based Configuration
- **Description:** All secrets and environment-specific configuration must be loaded from environment variables, not hardcoded.
- **Priority:** Critical
- **Acceptance Criteria:**
  - A `.env` file template (`.env.example`) is provided in the repository
  - The `.env` file is listed in `.gitignore`
  - `python-dotenv` or equivalent is used to load variables at startup
  - All configurable parameters (chunk size, top-K, model name, etc.) are in the configuration layer
- **Dependencies:** SR-01

---

**TR-09: API Communication Protocol**

- **ID:** TR-09
- **Title:** Frontend–Backend Communication
- **Description:** The Streamlit frontend must communicate with the FastAPI backend over HTTP using a REST or streaming HTTP interface.
- **Priority:** Critical
- **Acceptance Criteria:**
  - All requests use defined endpoint contracts
  - Request and response schemas are documented in DESIGN.md
  - Streaming responses use Server-Sent Events (SSE) or chunked HTTP transfer
- **Dependencies:** TR-01, TR-02

---

## 10. Security Requirements

---

**SR-01: API Key Protection**

- **ID:** SR-01
- **Title:** Secret Management
- **Description:** No API keys, tokens, or credentials may be committed to source control or exposed to the frontend.
- **Priority:** Critical
- **Acceptance Criteria:**
  - `.env` is in `.gitignore`
  - No secrets appear in Streamlit frontend code
  - Deployment platforms are configured with environment variables through their secrets management UI
- **Dependencies:** TR-08

---

**SR-02: CORS Configuration**

- **ID:** SR-02
- **Title:** Cross-Origin Resource Sharing
- **Description:** The FastAPI backend must configure CORS appropriately for the deployment environment.
- **Priority:** High
- **Acceptance Criteria:**
  - In development, localhost origins are allowed
  - In production, only the Streamlit deployment origin is allowed (or all origins if both are on the same domain)
  - CORS is implemented using FastAPI's CORSMiddleware
- **Dependencies:** TR-01

---

**SR-03: File Upload Validation**

- **ID:** SR-03
- **Title:** Uploaded File Validation
- **Description:** The backend must validate uploaded files before processing.
- **Priority:** High
- **Acceptance Criteria:**
  - Only `.pdf` MIME type is accepted
  - Files exceeding the defined size limit (default: 20 MB) are rejected
  - Malformed PDF files that cannot be parsed are rejected with an error response
- **Dependencies:** FR-01, FR-04

---

**SR-04: No Persistent User Data**

- **ID:** SR-04
- **Title:** Session-Scoped Data Only
- **Description:** Uploaded documents and conversation history must not be persisted between sessions unless explicitly designed to do so.
- **Priority:** High
- **Acceptance Criteria:**
  - Uploaded files are stored temporarily in memory or a temp directory and cleaned up after the session
  - Vector store entries are scoped to a session identifier and cleaned up on session clear or expiry
  - No user data is written to a permanent database
- **Dependencies:** FR-16

---

## 11. Data Requirements

---

**DAR-01: Document Metadata Schema**

- **ID:** DAR-01
- **Title:** Per-Document Metadata
- **Description:** Each uploaded document must have a metadata record tracking its identity and processing state.
- **Priority:** Critical
- **Acceptance Criteria:**
  - Metadata includes: document_id (UUID), filename, page_count, chunk_count, upload_timestamp, session_id
  - Metadata is stored in session state
  - Metadata is updated after processing completes
- **Dependencies:** FR-04, FR-05

---

**DAR-02: Chunk Metadata Schema**

- **ID:** DAR-02
- **Title:** Per-Chunk Metadata
- **Description:** Each text chunk stored in the vector database must carry metadata sufficient for citation generation.
- **Priority:** Critical
- **Acceptance Criteria:**
  - Chunk metadata includes: chunk_id, document_id, document_name, page_number, chunk_index, chunk_text
  - Metadata is stored alongside the vector in the vector database
  - Metadata is returned with retrieval results
- **Dependencies:** FR-05, FR-06

---

**DAR-03: Conversation History Schema**

- **ID:** DAR-03
- **Title:** Chat Message Structure
- **Description:** Each conversation turn must be stored in a defined schema.
- **Priority:** Critical
- **Acceptance Criteria:**
  - Each message includes: role (user/assistant), content, timestamp
  - Assistant messages also include: retrieved_chunks (list of chunk metadata), sources (list of citation objects)
  - History is stored in Streamlit session state
- **Dependencies:** FR-11

---

## 12. UI Requirements

---

**UIR-01: Neo-Brutalist Design Language**

- **ID:** UIR-01
- **Title:** Neo-Brutalist Visual Style
- **Description:** The interface must follow a Neo-Brutalist design language characterized by bold borders, high contrast, flat color blocks, and minimal decoration.
- **Priority:** High
- **Acceptance Criteria:**
  - Elements use thick (2–4px) solid black or high-contrast borders
  - Color palette uses bold, saturated primary colors with white and near-black neutrals
  - Typography uses a bold, legible sans-serif font
  - Shadows are hard/offset (box-shadow: 4px 4px 0px black) rather than soft/blurred
  - No gradients, glassmorphism, or rounded corners on primary UI elements
  - Hover states include offset/translate effects
- **Dependencies:** None

---

**UIR-02: Responsive Layout**

- **ID:** UIR-02
- **Title:** Responsive Grid Layout
- **Description:** The interface must function correctly at screen widths from 375px (mobile) to 1440px (desktop).
- **Priority:** High
- **Acceptance Criteria:**
  - The chat panel is the primary content area and expands to fill available width
  - The document sidebar collapses or moves below the chat on small screens
  - No horizontal scroll bar appears on any supported screen width
- **Dependencies:** NFR-04

---

**UIR-03: Chat Interface Structure**

- **ID:** UIR-03
- **Title:** Chat Message Layout
- **Description:** The chat interface must display user and assistant messages in a clearly differentiated, chronological layout.
- **Priority:** Critical
- **Acceptance Criteria:**
  - User messages are right-aligned with a distinct background
  - Assistant messages are left-aligned with a different background
  - Each message includes a timestamp
  - Messages scroll automatically as new content arrives
- **Dependencies:** FR-07, FR-09

---

**UIR-04: Citation Panel**

- **ID:** UIR-04
- **Title:** Source Citation Display
- **Description:** Source citations must be displayed in an expandable panel below each assistant response.
- **Priority:** Critical
- **Acceptance Criteria:**
  - Each citation is displayed as a labeled card or chip
  - The card shows document name and page number
  - Expanding the card reveals the raw retrieved text passage
  - The citation panel is visually subordinate to the main response
- **Dependencies:** FR-10

---

**UIR-05: Upload Zone**

- **ID:** UIR-05
- **Title:** Upload Zone Affordance
- **Description:** The upload zone must be visually distinct and communicate its purpose without instruction text.
- **Priority:** High
- **Acceptance Criteria:**
  - The zone has a dashed border in the Neo-Brutalist style
  - An icon and label indicate drag-and-drop or click-to-upload functionality
  - The zone changes appearance when a file is dragged over it
- **Dependencies:** FR-02

---

## 13. Accessibility Requirements

---

**AR-01: Keyboard Navigation**

- **ID:** AR-01
- **Title:** Keyboard Accessibility
- **Description:** All interactive elements must be operable via keyboard.
- **Priority:** Medium
- **Acceptance Criteria:**
  - All buttons, inputs, and links are reachable via Tab key
  - Focus states are visually visible
  - Enter key submits the chat input
- **Dependencies:** UIR-03

---

**AR-02: Color Contrast**

- **ID:** AR-02
- **Title:** Text Contrast Ratio
- **Description:** Text must meet minimum contrast ratios.
- **Priority:** Medium
- **Acceptance Criteria:**
  - Normal text achieves a minimum contrast ratio of 4.5:1 against its background
  - Large text achieves a minimum contrast ratio of 3:1
  - This applies to both light and dark themes
- **Dependencies:** UIR-01

---

**AR-03: Screen Reader Labels**

- **ID:** AR-03
- **Title:** ARIA Labels on Controls
- **Description:** Interactive controls without visible text labels must have ARIA labels.
- **Priority:** Medium
- **Acceptance Criteria:**
  - Icon-only buttons have `aria-label` attributes
  - File upload inputs have associated labels
  - Status messages use `role="status"` or `aria-live` where appropriate
- **Dependencies:** UIR-01

---

## 14. Deployment Requirements

---

**DR-01: Backend Deployment — Free Tier**

- **ID:** DR-01
- **Title:** Backend Free-Tier Deployment
- **Description:** The FastAPI backend must be deployable to a free-tier hosting platform that provides a public HTTPS URL.
- **Priority:** Critical
- **Acceptance Criteria:**
  - The backend is deployed and publicly accessible via HTTPS
  - Deployment uses no paid tier
  - Environment variables (API keys, configuration) are set via the platform's secrets interface
  - The deployment platform is documented in DESIGN.md with justification
- **Dependencies:** NFR-07

---

**DR-02: Frontend Deployment — Free Tier**

- **ID:** DR-02
- **Title:** Frontend Free-Tier Deployment
- **Description:** The Streamlit frontend must be deployable to a free-tier hosting platform.
- **Priority:** Critical
- **Acceptance Criteria:**
  - The frontend is deployed and publicly accessible via HTTPS
  - Deployment uses no paid tier
  - The backend URL is configurable via environment variable
- **Dependencies:** NFR-07

---

**DR-03: Independent Deployability**

- **ID:** DR-03
- **Title:** Decoupled Deployment
- **Description:** Frontend and backend must be independently deployable.
- **Priority:** High
- **Acceptance Criteria:**
  - The frontend can be redeployed without touching the backend
  - The backend can be redeployed without touching the frontend
  - The backend URL in the frontend is configurable via environment variable
- **Dependencies:** TR-09

---

**DR-04: Deployment Documentation**

- **ID:** DR-04
- **Title:** Deployment Instructions
- **Description:** Step-by-step deployment instructions must be provided.
- **Priority:** High
- **Acceptance Criteria:**
  - README includes deployment steps for both frontend and backend
  - Required environment variables are listed with descriptions
  - Common deployment issues and their solutions are documented
- **Dependencies:** DR-01, DR-02

---

## 15. Performance Requirements

---

**PR-01: Embedding Generation Speed**

- **ID:** PR-01
- **Title:** Embedding Throughput
- **Description:** Embedding generation must be fast enough to support the document processing latency targets.
- **Priority:** High
- **Acceptance Criteria:**
  - The Sentence Transformer model processes at least 50 chunks per second on a CPU-only environment
  - Batch embedding is used when processing multiple chunks to maximize throughput
- **Dependencies:** TR-05

---

**PR-02: Retrieval Speed**

- **ID:** PR-02
- **Title:** Vector Search Latency
- **Description:** The vector similarity search must complete within acceptable latency bounds.
- **Priority:** High
- **Acceptance Criteria:**
  - Top-K retrieval from a collection of up to 10,000 chunks must complete within 500ms
- **Dependencies:** TR-06

---

**PR-03: LLM Response Latency**

- **ID:** PR-03
- **Title:** LLM API Latency
- **Description:** The Groq API must return the first token within a time acceptable for a responsive UI.
- **Priority:** High
- **Acceptance Criteria:**
  - Time-to-first-token from Groq must not exceed 3 seconds under normal conditions
  - This is validated in production deployment testing
- **Dependencies:** TR-07

---

## 16. Error Handling Requirements

---

**EHR-01: Upload Failure Handling**

- **ID:** EHR-01
- **Title:** Graceful Upload Failure
- **Description:** Upload and processing failures must be caught and communicated to the user without crashing the application.
- **Priority:** Critical
- **Acceptance Criteria:**
  - File type rejection returns HTTP 400 with a descriptive message
  - File size rejection returns HTTP 413 with a descriptive message
  - Text extraction failure returns HTTP 422 with advice to check the PDF
  - The frontend displays the error message and remains functional
- **Dependencies:** FR-18

---

**EHR-02: LLM API Failure Handling**

- **ID:** EHR-02
- **Title:** Groq API Failure Handling
- **Description:** Groq API failures must be handled gracefully without crashing the application.
- **Priority:** Critical
- **Acceptance Criteria:**
  - Rate limit errors (HTTP 429) trigger a retry with exponential backoff (up to 3 attempts)
  - After exhausting retries, a user-friendly error message is shown
  - Server errors (HTTP 5xx) from Groq trigger the fallback model
  - If the fallback model also fails, a user-friendly error message is shown
- **Dependencies:** FR-09, TR-07

---

**EHR-03: Vector Database Failure Handling**

- **ID:** EHR-03
- **Title:** Vector Store Failure Handling
- **Description:** Vector database errors must not crash the application.
- **Priority:** High
- **Acceptance Criteria:**
  - Failed inserts during ingestion log the error and surface it to the user
  - Failed queries return a graceful error response rather than an exception
- **Dependencies:** TR-06

---

**EHR-04: Network Error Handling**

- **ID:** EHR-04
- **Title:** Frontend Network Error Handling
- **Description:** The Streamlit frontend must handle network errors when communicating with the backend.
- **Priority:** High
- **Acceptance Criteria:**
  - Connection refused errors display a "backend unavailable" message
  - Timeout errors display a retry prompt
  - Network errors do not leave the UI in a broken state
- **Dependencies:** TR-09

---

## 17. Logging Requirements

---

**LR-01: Structured Application Logging**

- **ID:** LR-01
- **Title:** Structured Logging
- **Description:** The backend must emit structured log messages at appropriate severity levels.
- **Priority:** High
- **Acceptance Criteria:**
  - Python's standard logging module is used
  - Log levels are: DEBUG, INFO, WARNING, ERROR, CRITICAL
  - Each log entry includes: timestamp, level, module, message
  - In production, log level is configurable via environment variable
- **Dependencies:** None

---

**LR-02: Request Logging**

- **ID:** LR-02
- **Title:** API Request Logging
- **Description:** All API requests and responses must be logged at the INFO level.
- **Priority:** Medium
- **Acceptance Criteria:**
  - Each request logs: method, path, status code, duration
  - Uploaded filenames are logged (not content)
  - Query text is logged (truncated to 100 characters)
- **Dependencies:** TR-01, LR-01

---

**LR-03: Error Logging**

- **ID:** LR-03
- **Title:** Exception and Error Logging
- **Description:** All caught exceptions must be logged with stack traces at ERROR level.
- **Priority:** High
- **Acceptance Criteria:**
  - `logger.exception()` is used for all caught exceptions
  - Stack traces are included in ERROR log entries
  - No exception is silently swallowed
- **Dependencies:** LR-01

---

## 18. Monitoring Requirements

---

**MR-01: Health Check Endpoint**

- **ID:** MR-01
- **Title:** Backend Health Check
- **Description:** The backend must expose a health check endpoint for deployment platform monitoring.
- **Priority:** High
- **Acceptance Criteria:**
  - `GET /health` returns HTTP 200 with `{"status": "ok"}` when the service is running
  - The endpoint checks connectivity to the vector database
  - The deployment platform is configured to use this endpoint for health monitoring
- **Dependencies:** TR-01

---

**MR-02: Usage Tracking (Lightweight)**

- **ID:** MR-02
- **Title:** Basic Usage Metrics
- **Description:** The backend should log basic usage metrics for portfolio and monitoring purposes.
- **Priority:** Low
- **Acceptance Criteria:**
  - Total documents processed per session is logged
  - Total queries per session is logged
  - This information is available in deployment platform logs
- **Dependencies:** LR-01

---

## 19. Scalability Considerations

The following scalability considerations are documented for completeness. They are explicitly out of scope for the initial implementation but should not be designed around.

- The session model (in-memory conversation state, per-session vector namespacing) is not horizontally scalable. Scaling would require a distributed session store (e.g., Redis) and a cloud-native vector database.
- The Sentence Transformer model loads into memory on startup. Multiple instances would load multiple model copies; a model serving layer (e.g., Triton) would be required for efficient scaling.
- Free-tier deployment platforms impose memory and CPU limits that cap the number of concurrent sessions.
- The current architecture supports one session per deployment instance. Multi-tenancy would require authentication and per-user data isolation.

These are acknowledged limitations appropriate for the portfolio scope of this project.

---

## 20. Risks and Mitigations

| ID | Risk | Probability | Impact | Mitigation |
|----|------|-------------|--------|------------|
| RK-01 | Groq free-tier rate limits cause frequent errors during demos | Medium | High | Implement retry with backoff; document limits; implement fallback model |
| RK-02 | Selected vector database free tier is deprecated or limited | Low | High | Select a database with a long-term free tier; document the evaluated alternatives |
| RK-03 | Sentence Transformer model download fails in deployment environment | Low | High | Cache model in repository or use lazy loading with error handling |
| RK-04 | Free-tier backend host has cold-start delays > 60 seconds | Medium | Medium | Add health check retry logic; document expected cold-start behavior |
| RK-05 | Scanned PDFs with no extractable text cause silent failures | High | Medium | Detect and reject image-only PDFs with a clear error message |
| RK-06 | Streamlit session state is lost on page refresh | High | Medium | Document this behavior; provide export-before-refresh guidance |
| RK-07 | Free-tier vector database has insufficient storage for demo | Low | Medium | Monitor chunk count; implement per-session cleanup on clear |
| RK-08 | CORS misconfiguration blocks frontend–backend communication in production | Medium | High | Test CORS configuration in staging before final deployment |

---

## 21. Success Metrics

| ID | Metric | Target | Measurement Method |
|----|--------|--------|-------------------|
| SM-01 | First-response latency (time to first token) | < 5 seconds | Manual timing during UAT |
| SM-02 | Document processing time (50-page PDF) | < 60 seconds | Timed test during UAT |
| SM-03 | Citation accuracy (response grounded in retrieved content) | ≥ 90% of tested queries | Manual review of 20 test queries |
| SM-04 | Error rate during normal operation | < 5% of requests | Log review |
| SM-05 | Mobile usability | No broken layout on 375px viewport | Manual browser test |
| SM-06 | Deployment accessibility | Public HTTPS URL works without authentication | Manual verification |
| SM-07 | Zero paid services | $0 monthly operational cost | Account billing review |

---

## 22. Acceptance Criteria

The project is considered complete and ready for portfolio presentation when:

1. A user can navigate to a public HTTPS URL without any login
2. A user can upload a PDF document and receive a success confirmation within 3 minutes
3. A user can ask a natural language question and receive a grounded, streamed response with source citations
4. A user can ask follow-up questions that reference previous answers
5. A user can upload multiple documents and receive answers that cite both
6. A user can remove a document from the session
7. A user can download the chat history as a file
8. A user can toggle between dark and light themes
9. The interface is usable on a 375px mobile viewport
10. No paid services are required for the system to function
11. The repository README contains sufficient documentation to redeploy the project from scratch
12. All error states display user-friendly messages without exposing stack traces

---

*End of REQUIREMENTS.md*
