# Comprehensive User Journey & Data Flow: Dissertation Generation

**Use Case:** A user aims to generate a full dissertation draft.
**Input Prompt:** A long, detailed prompt describing the research question, scope, and desired tone.
**Input Context:** 10 heterogeneous files, including PDFs, DOCX documents, one audio file (e.g., an interview), and one video link (e.g., a lecture).
**Selected Work Type:** "Dissertation"

This document maps the end-to-end user journey, system processes, data flows, and agent swarm interactions from the initial user action in the chat interface to the final delivery of the dissertation.

---

## Phase 1: Task Initiation and Context Provisioning

This phase covers the user's actions to initiate the task, write the prompt, and upload the necessary context files.

### Step 1.1: User Navigates to the Chat Interface
1.  **User Action:** User logs into the platform and clicks on the "Chat" or "New Project" button.
2.  **System Action (Frontend):**
    *   The Next.js router navigates the user to the `/chat` page.
    *   The `src/app/chat/page.tsx` component is rendered.
    *   The layout (`src/app/layout.tsx`) ensures the standard `Header` and `Sidebar` are present.
    .   A new, empty chat session state is initialized in the client.
3.  **UI State:**
    *   The main content area displays the `WelcomeScreen` component (`src/components/WelcomeScreen.tsx`), as there is no chat history yet for this session.
    *   The `PromptEditor` (`src/components/chat/PromptEditor.tsx`) is visible at the bottom of the screen, ready for input.
    *   The `ContextUploadMenu` (`src/components/chat/ContextUploadMenu.tsx`) is visible, likely represented by a paperclip or upload icon.

### Step 1.2: User Composes the Core Prompt
1.  **User Action:** The user clicks into the `PromptEditor`'s textarea and types or pastes their detailed dissertation prompt.
    *   *Example Prompt Snippet:* "Generate a dissertation exploring the impact of quantum computing on cryptographic security. The primary thesis should argue that... The structure must include an introduction, a detailed literature review of the attached papers, a methodology section based on the 'research_framework.docx' document, an analysis of the interview transcript, and a conclusion summarizing the findings. The tone should be formal and academic."
2.  **System Action (Frontend):**
    *   The `PromptEditor` component manages the state of the input text.
    *   The component might include features like character/word count, which update in real-time.
    *   No backend calls are made at this stage.

### Step 1.3: User Selects the "Dissertation" Work Type
1.  **User Action:** The user interacts with a dropdown menu or a similar UI element within the chat interface to specify the type of output they want. They select "Dissertation".
2.  **System Action (Frontend):**
    *   A `select` or `dropdown-menu` component (`src/components/ui/select.tsx`) updates the client-side session state.
    *   `session.state.workType = 'dissertation'`.
    *   This selection might dynamically adjust other UI elements. For example, it could reveal more advanced options or context slots relevant to long-form academic writing.
3.  **Data Structure (Client-Side):**
    ```json
    {
      "sessionId": "temp-session-xyz123",
      "prompt": "Generate a dissertation exploring...",
      "workType": "dissertation",
      "files": []
    }
    ```

### Step 1.4: User Initiates File Upload
1.  **User Action:** The user clicks the upload icon, which triggers the `ContextUploadMenu`. This menu presents options like "Upload from Computer" or "Import from URL". The user chooses to upload files.
2.  **System Action (Frontend):**
    *   The `useFileUpload` hook (`src/hooks/useFileUpload.ts`) is likely invoked.
    *   A file selection dialog from the operating system is displayed.
    *   Alternatively, the user can drag and drop files onto the `FileUploadZone` component (`src/components/ui/FileUploadZone.tsx`).

### Step 1.5: User Selects and Uploads 10 Files
1.  **User Action:** The user selects 10 files of varying formats (e.g., 5 PDFs, 3 DOCX, 1 MP3, 1 MOV).
2.  **System Action (Frontend):**
    *   The `useFileUpload` hook receives the `FileList` object from the browser.
    *   For each file, the hook performs initial client-side validation:
        *   Check file type against a list of allowed extensions/MIME types.
        *   Check file size against the maximum allowed limit (e.g., 100MB per file).
    *   For each valid file, a unique `fileId` is generated client-side (e.g., a UUID).
    *   The UI updates to show a list of files being uploaded. Each file is represented by a `FileTile` component (`src/components/ui/FileTile.tsx`).
3.  **UI State (`FileTile`):**
    *   Each `FileTile` displays the filename, size, and a progress bar (`src/components/ui/progress.tsx`).
    *   The initial state of the progress bar is 0%.
    *   A cancel button is available for each file.

### Step 1.6: File Uploading Process (Parallel)
1.  **System Action (Frontend):**
    *   The `useFileUpload` hook initiates the upload process for all 10 files in parallel to improve efficiency.
    *   For each file, it makes an API call to the backend to get a secure, pre-signed upload URL.
2.  **System Action (Backend - API):**
    *   **Endpoint:** `POST /api/v1/files/request-upload`
    *   **Request Payload (for each file):**
        ```json
        {
          "fileName": "Quantum_Cryptography_Review.pdf",
          "fileType": "application/pdf",
          "fileSize": 5242880
        }
        ```
    *   The backend authenticates the user.
    *   It generates a pre-signed URL for a cloud storage provider (e.g., AWS S3, Google Cloud Storage). This URL grants temporary, secure write access to a specific key in a storage bucket.
    *   **Response Payload (for each file):**
        ```json
        {
          "fileId": "server-generated-uuid-abc456",
          "uploadUrl": "https://s3.amazonaws.com/handywriterz-uploads/...",
          "storageKey": "user-uploads/user-123/server-generated-uuid-abc456"
        }
        ```
3.  **System Action (Frontend):**
    *   Upon receiving the `uploadUrl`, the frontend starts the actual file upload using an HTTP `PUT` request directly to the cloud storage URL.
    *   The request body is the raw file content.
    *   The `onUploadProgress` event of the HTTP client (e.g., Axios) is used to update the progress bar in the corresponding `FileTile`.
    *   As each file successfully uploads, its `FileTile` UI updates to a "Completed" state (e.g., a green checkmark). The client-side session state is updated.
4.  **Data Structure (Client-Side after uploads):**
    ```json
    {
      "sessionId": "temp-session-xyz123",
      "prompt": "Generate a dissertation exploring...",
      "workType": "dissertation",
      "files": [
        { "clientFileId": "uuid-1", "serverFileId": "server-generated-uuid-abc456", "status": "completed", "name": "Quantum_Cryptography_Review.pdf" },
        { "clientFileId": "uuid-2", "serverFileId": "server-generated-uuid-def789", "status": "completed", "name": "research_framework.docx" },
        // ... 8 more files
      ]
    }
    ```

### Step 1.7: User Adds a Video Link
1.  **User Action:** The user selects the "Import from URL" option and pastes a link to a video lecture (e.g., a YouTube or Vimeo link).
2.  **System Action (Frontend):**
    *   The UI validates the URL format.
    *   The URL is added to the session state. It's treated differently from file uploads but is still part of the context.
3.  **Data Structure (Client-Side with video link):**
    ```json
    {
      "sessionId": "temp-session-xyz123",
      "prompt": "Generate a dissertation exploring...",
      "workType": "dissertation",
      "files": [
        // ... 10 file objects
      ],
      "links": [
        { "type": "video", "url": "https://www.youtube.com/watch?v=some_video_id" }
      ]
    }
    ```

### Step 1.8: User Submits the Task
1.  **User Action:** Once the prompt is written and all files/links are added, the user clicks the final "Submit" or "Generate" button.
2.  **System Action (Frontend):**
    *   The submit button is disabled to prevent duplicate requests.
    *   A loading indicator appears.
    *   The frontend packages the entire session state into a single API request to initiate the main task.

---

## Phase 2: Task Ingestion and Swarm Configuration

This phase describes how the backend receives the task, validates it, and configures the necessary AI agent swarms to handle the complex request. This leverages the "Swarm Intelligence V2" and "Hierarchical Swarms" concepts from the project's guiding principles.

### Step 2.1: Backend Receives the Task
1.  **System Action (Backend - API):**
    *   **Endpoint:** `POST /api/v1/chat/generate`
    *   **Request Payload:**
        ```json
        {
          "prompt": "Generate a dissertation exploring...",
          "workType": "dissertation",
          "context": {
            "files": [
              { "fileId": "server-generated-uuid-abc456", "fileName": "Quantum_Cryptography_Review.pdf" },
              { "fileId": "server-generated-uuid-def789", "fileName": "research_framework.docx" },
              { "fileId": "server-generated-uuid-ghi012", "fileName": "interview_audio.mp3" }
              // ... 7 more files
            ],
            "links": [
              { "type": "video", "url": "https://www.youtube.com/watch?v=some_video_id" }
            ]
          }
        }
        ```
    *   The API performs final validation:
        *   Ensures all `fileId`s exist and belong to the authenticated user.
        *   Validates the URL format.
    *   A new `Task` record is created in the database with a `status` of `PENDING`.
    *   The task is placed into a message queue (e.g., RabbitMQ, SQS) for asynchronous processing.
    *   The API immediately returns a response to the frontend.
2.  **System Action (Frontend):**
    *   **API Response:**
        ```json
        {
          "taskId": "task-uuid-98765",
          "status": "QUEUED",
          "message": "Your request has been received and is being processed."
        }
        ```
    *   The frontend now knows the `taskId` and can use it to poll for updates or listen on a WebSocket for real-time progress.
    *   The UI transitions from the input form to a "processing" view, perhaps showing the `AgentActivityStream` component (`src/components/AgentActivityStream.tsx`).

### Step 2.2: Task Orchestrator Agent Activation
1.  **System Action (Backend - Worker):**
    *   A worker process picks up the task from the message queue.
    *   The worker instantiates a high-level **Task Orchestrator Agent**. This agent's job is not to write but to plan and coordinate.
2.  **Orchestrator Agent - Initial Analysis:**
    *   **Input:** The full task payload.
    *   **Thought Process:**
        1.  "The `workType` is 'dissertation'. This is a complex, long-form academic task. The 'Archimedes' Swarm for scientific discovery is the most appropriate top-level swarm."
        2.  "The context contains multiple file types: `PDF`, `DOCX`, `MP3`, and a video `URL`. I cannot process these directly. I need to spawn specialized sub-swarms for data extraction and analysis."
        3.  "The user's prompt provides the guiding directive for the entire project. I will use this as the guiding directive for the entire project."
    *   **Action:** The Orchestrator designs a hierarchical swarm structure for this specific task.

### Step 2.3: Dynamic Swarm Configuration
1.  **System Action (Orchestrator Agent):**
    *   The Orchestrator defines a plan with dependencies. Data extraction must complete before the main writing can begin.
    *   It dynamically configures and dispatches the following sub-swarms/agents to run in parallel:

    *   **1. Document Analysis Swarm (for PDFs and DOCX):**
        *   **Assigned Files:** All `.pdf` and `.docx` files.
        *   **Goal:** Extract text, structure, tables, and key semantic information.

    *   **2. Audio Processing Agent (for MP3):**
        *   **Assigned File:** `interview_audio.mp3`.
        *   **Goal:** Transcribe the audio and summarize the content.

    *   **3. Video Processing Agent (for the URL):**
        *   **Assigned Link:** The YouTube URL.
        *   **Goal:** Transcribe audio, analyze visual content, and summarize.

2.  **System Action (Backend):**
    *   The Orchestrator updates the main `Task` record in the database with the plan and sub-task IDs.
    *   It sends real-time updates via WebSocket to the frontend.
3.  **UI State (`AgentActivityStream`):**
    *   `[Orchestrator Agent]: Task received. Analyzing requirements.`
    *   `[Orchestrator Agent]: Detected 8 text documents, 1 audio file, and 1 video link.`
    *   `[Orchestrator Agent]: Configuring hierarchical swarm.`
    *   `[Orchestrator Agent]: Dispatching Document Analysis Swarm.`
    *   `[Orchestrator Agent]: Dispatching Audio Processing Agent.`
    *   `[Orchestrator Agent]: Dispatching Video Processing Agent.`

---

## Phase 3: Parallel Data Processing and Synthesis

This phase details the work of the specialized sub-swarms operating in parallel to process the heterogeneous source materials and populate a central knowledge base for the task.

### Step 3.1: Document Analysis Swarm in Action
1.  **System Action (Document Swarm):**
    *   The swarm receives a list of `fileId`s for the text-based documents.
    *   For each file:
        *   An agent securely downloads the file from cloud storage using its `storageKey`.
        *   It uses a library like `pdf-parse` for PDFs and `mammoth.js` for DOCX to extract raw text content.
        *   Another agent in the swarm processes the raw text to identify structure (headings, paragraphs, lists).
        *   A more advanced analysis agent performs:
            *   **Summarization:** Creates a concise summary of each document.
            *   **Entity Extraction:** Identifies key people, organizations, concepts, and technical terms.
            *   **Topic Modeling:** Determines the main themes of the document.
2.  **Data Flow:**
    *   The extracted and analyzed data is structured into a standardized JSON format.
    *   **Example Structured Data Object:**
        ```json
        {
          "sourceFileId": "server-generated-uuid-abc456",
          "sourceFileName": "Quantum_Cryptography_Review.pdf",
          "type": "document",
          "summary": "This paper reviews the current state of quantum-resistant cryptography...",
          "entities": ["Shor's Algorithm", "NIST", "Lattice-based cryptography"],
          "fullText": "...",
          "structure": [
            { "level": 1, "title": "Introduction", "content": "..." },
            { "level": 2, "title": "Background", "content": "..." }
          ]
        }
        ```
    *   This structured object is saved to a temporary, task-specific knowledge base (e.g., a vector database or a document store).
3.  **UI State (`AgentActivityStream`):**
    *   `[Document Swarm]: Processing Quantum_Cryptography_Review.pdf...`
    *   `[Document Swarm]: Extracting text and identifying 5 sections.`
    *   `[Document Swarm]: Analysis complete for Quantum_Cryptography_Review.pdf. Key entities found: Shor's Algorithm, NIST.`
    *   *(This repeats for all 8 documents)*

### Step 3.2: Audio Processing Agent in Action
1.  **System Action (Audio Agent):**
    *   The agent downloads `interview_audio.mp3` from storage.
    *   It uses a state-of-the-art Speech-to-Text (STT) API (e.g., Whisper) to transcribe the entire audio file.
    *   The agent then analyzes the resulting transcript to summarize key points, questions, and answers. It might also perform speaker diarization if the STT model supports it ("Speaker A:", "Speaker B:").
2.  **Data Flow:**
    *   The transcript and summary are saved to the task's knowledge base.
    *   **Example Structured Data Object:**
        ```json
        {
          "sourceFileId": "server-generated-uuid-ghi012",
          "sourceFileName": "interview_audio.mp3",
          "type": "audio_transcript",
          "summary": "Dr. Evans discusses the practical challenges of implementing post-quantum algorithms...",
          "fullTranscript": "[00:00:01] Interviewer: Dr. Evans, thank you for joining me...",
          "keyPoints": ["Challenge 1: Computational overhead.", "Challenge 2: Lack of standardization."]
        }
        ```
3.  **UI State (`AgentActivityStream`):**
    *   `[Audio Agent]: Processing interview_audio.mp3...`
    *   `[Audio Agent]: Transcribing audio. This may take a few minutes.`
    *   `[Audio Agent]: Transcription complete. Analyzing content.`
    *   `[Audio Agent]: Identified key discussion points on implementation challenges.`

### Step 3.3: Video Processing Agent in Action
1.  **System Action (Video Agent):**
    *   The agent uses a library like `youtube-dl` to securely download the video content from the provided URL.
    *   It extracts the audio track and sends it to the STT service for transcription, similar to the Audio Agent.
    *   Simultaneously, it uses a computer vision model to process the video stream. It might perform:
        *   **Keyframe Extraction:** Saves important frames from the video (e.g., slides, diagrams).
        *   **Optical Character Recognition (OCR):** Extracts text from the keyframes (e.g., text on a presentation slide).
        *   **Scene Detection:** Identifies different segments of the video.
2.  **Data Flow:**
    *   All extracted information—transcript, summary, keyframe descriptions, OCR text—is saved to the knowledge base.
    *   **Example Structured Data Object:**
        ```json
        {
          "sourceUrl": "https://www.youtube.com/watch?v=some_video_id",
          "type": "video_analysis",
          "summary": "Lecture by Prof. Chen on the history of cryptography, ending with a discussion on quantum threats.",
          "transcript": "[00:00:01] Prof. Chen: Welcome everyone. Today we're going to talk about...",
          "visualElements": [
            { "timestamp": "00:15:32", "description": "Diagram of RSA encryption.", "ocrText": "Public Key: (e, n)" },
            { "timestamp": "00:45:10", "description": "Slide listing quantum-resistant algorithms.", "ocrText": "1. Lattice-based\n2. Code-based\n3. Hash-based" }
          ]
        }
        ```
3.  **UI State (`AgentActivityStream`):**
    *   `[Video Agent]: Processing video from youtube.com...`
    *   `[Video Agent]: Extracting audio and video streams.`
    *   `[Video Agent]: Transcribing lecture audio.`
    *   `[Video Agent]: Analyzing visual content for key information.`
    *   `[Video Agent]: Identified 3 key diagrams and 12 slides.`

### Step 3.4: Synthesis and Knowledge Base Finalization
1.  **System Action (Orchestrator Agent):**
    *   The Orchestrator monitors the progress of the sub-swarms.
    *   Once all data processing tasks are complete, it signals a final **Synthesizer Agent**.
2.  **System Action (Synthesizer Agent):**
    *   This agent reads all the structured data objects from the knowledge base.
    *   It creates a master summary and a unified "map" of all the provided context.
    *   It performs cross-referencing. For example, it might find that a concept mentioned in the audio interview ("computational overhead") is explained in detail in one of the PDF papers.
    *   It enriches the knowledge base with these connections and relationships.
    *   This unified knowledge base is now ready for the main writing swarm.
3.  **UI State (`AgentActivityStream`):**
    *   `[Orchestrator Agent]: All data sources processed.`
    *   `[Synthesizer Agent]: Building unified knowledge base.`
    *   `[Synthesizer Agent]: Cross-referencing sources... Found 25 connections between documents.`
    *   `[Synthesizer Agent]: Knowledge base complete.`

---

## Phase 4: Dissertation Generation (The "Archimedes" Swarm)

With the knowledge base prepared, the main writing swarm begins the process of generating the dissertation, following the user's prompt and the principles of scientific writing.

### Step 4.1: Outline and Thesis Generation
1.  **System Action (Orchestrator Agent):**
    *   The Orchestrator activates the main **"Archimedes" Swarm**.
    *   The first agent dispatched is the **Thesis & Outline Agent**.
2.  **System Action (Thesis & Outline Agent):**
    *   **Input:** The user's original prompt and the complete, synthesized knowledge base.
    *   **Goal:** Create a detailed, chapter-by-chapter outline and a strong, clear thesis statement.
    *   **Process:**
        1.  It re-reads the user's prompt to ensure the core requirements are met.
        2.  It formulates a thesis statement based on the prompt's instructions and the synthesized data.
        3.  It structures the dissertation, creating a logical flow.
            *   Chapter 1: Introduction
            *   Chapter 2: Literature Review
            *   Chapter 3: Methodology
            *   Chapter 4: Analysis of Findings
            *   Chapter 5: Discussion
            *   Chapter 6: Conclusion
        4.  For each chapter, it writes a brief description and lists the key points to be covered, referencing specific sources from the knowledge base.
3.  **UI State (`AgentActivityStream`):**
    *   `[Orchestrator Agent]: Activating 'Archimedes' writing swarm.`
    *   `[Thesis & Outline Agent]: Formulating thesis statement.`
    *   `[Thesis & Outline Agent]: Designing dissertation structure.`
    *   `[Thesis & Outline Agent]: Outline generated. Requesting user approval.`
    *   *(Optional Interaction Point):* The system could present the outline to the user for approval before proceeding. For this journey, we assume it proceeds automatically.

### Step 4.2: Parallel Chapter Drafting
1.  **System Action (Orchestrator Agent):**
    *   The Orchestrator reviews the approved outline.
    *   It spawns multiple **Chapter Writer Agents** to work on different chapters in parallel, where possible. For example, the Literature Review and Methodology chapters can often be drafted simultaneously.
2.  **System Action (Chapter Writer Agent - e.g., for "Literature Review"):**
    *   **Input:** The outline for Chapter 2 and access to the full knowledge base.
    *   **Process:**
        1.  It queries the knowledge base for all documents, summaries, and entities relevant to the literature review.
        2.  It synthesizes the information from the various PDFs and the video lecture transcript.
        3.  It drafts the chapter, ensuring proper flow and academic tone.
        4.  Crucially, it keeps track of every piece of information used and its source (`sourceFileId`). This is vital for the next step.
3.  **System Action (Citation Agent):**
    *   This agent works alongside the writers. As a writer agent drafts a sentence using a source, it flags the source material.
    *   The Citation Agent retrieves the full metadata for that source and creates a properly formatted in-text citation (e.g., APA, MLA) and adds the full entry to a running bibliography file.
4.  **UI State (`AgentActivityStream`):**
    *   `[Orchestrator Agent]: Dispatching 5 Chapter Writer Agents.`
    *   `[Writer Agent 1]: Drafting Chapter 1: Introduction.`
    *   `[Writer Agent 2]: Drafting Chapter 2: Literature Review. Synthesizing 6 sources.`
    *   `[Citation Agent]: Added 'Smith (2021)' to bibliography.`
    *   `[Writer Agent 3]: Drafting Chapter 3: Methodology, based on research_framework.docx.`
    *   `[Citation Agent]: Added 'Chen (2023)' to bibliography.`

### Step 4.3: Review and Refinement
1.  **System Action (Editor Agent):**
    *   As each chapter draft is completed, it's passed to an **Editor Agent**.
    *   **Process:**
        1.  **Coherence Check:** Reads the chapter to ensure it's logical and well-argued.
        2.  **Consistency Check:** Cross-references with other completed chapters to ensure consistent terminology and arguments.
        3.  **Style & Tone Check:** Verifies the writing matches the requested "formal and academic" tone. It might use the user's "Dynamic Fingerprint" (from `GEMINI.md`) if one exists.
        4.  **Grammar & Plagiarism Check:** Performs a final polish.
    *   If the Editor Agent finds significant issues, it can send the chapter back to the original writer agent with specific feedback for revision.
2.  **UI State (`AgentActivityStream`):**
    *   `[Writer Agent 2]: Chapter 2 draft complete.`
    *   `[Editor Agent]: Reviewing Chapter 2.`
    *   `[Editor Agent]: Chapter 2 approved.`
    *   `[Writer Agent 4]: Chapter 4 draft complete.`
    *   `[Editor Agent]: Reviewing Chapter 4.`
    *   `[Editor Agent]: Found inconsistency. Sending Chapter 4 back for revision.`
    *   `[Writer Agent 4]: Revising Chapter 4 based on editor feedback.`

### Step 4.4: Final Assembly
1.  **System Action (Assembler Agent):**
    *   Once all chapters are written and approved by the Editor Agent, the **Assembler Agent** takes over.
    *   **Process:**
        1.  It orders the chapters correctly.
        2.  It generates a Title Page.
        3.  It creates a Table of Contents with correct page numbers.
        4.  It appends the final, formatted bibliography created by the Citation Agent.
        5.  It compiles everything into a single, cohesive document.
2.  **System Action (Backend):**
    *   The final document is saved in multiple formats (e.g., `.docx`, `.pdf`).
    *   The main `Task` record in the database is updated to `status: COMPLETED`.
3.  **UI State (`AgentActivityStream`):**
    *   `[Assembler Agent]: All chapters complete. Assembling final dissertation.`
    *   `[Assembler Agent]: Generating Table of Contents.`
    *   `[Assembler Agent]: Formatting bibliography.`
    *   `[Assembler Agent]: Final document compiled.`
    *   `[Orchestrator Agent]: Task complete. Your dissertation is ready.`

---

## Phase 5: Delivery and User Feedback Loop

This final phase covers the delivery of the generated document to the user and the process for handling revisions.

### Step 5.1: Presenting the Result
1.  **System Action (Backend):**
    *   Sends a final WebSocket message or push notification to the user.
2.  **System Action (Frontend):):**
    *   The UI updates to show the completed status.
    *   The `AgentActivityStream` is replaced with a results view.
    *   This view includes:
        *   A preview of the generated document.
        *   A `DownloadMenu` (`src/components/DownloadMenu.tsx`) with options for PDF and DOCX.
        *   A summary of the work done (e.g., "Analyzed 10 sources, wrote 6 chapters, 15,000 words").
        *   A new chat input for feedback or revision requests.

### Step 5.2: User Review and Revision Request
1.  **User Action:** The user downloads and reads the draft. They decide a section needs revision. They type a follow-up command into the chat.
    *   *Example Revision Prompt:* "In Chapter 4, please expand on the analysis of the interview with Dr. Evans and connect it more directly to the findings from the 'Quantum_Cryptography_Review.pdf' paper."
2.  **System Action (Frontend):**
    *   This new prompt is sent to the backend, linked to the original `taskId`.
3.  **System Action (Backend):**
    *   **Endpoint:** `POST /api/v1/chat/revise`
    *   The Orchestrator Agent for the original task is re-activated, but in a "revision" mode.
    *   **Orchestrator Thought Process:** "This is a revision request for an existing task. The user wants changes in Chapter 4, linking two specific sources. I don't need to re-run the entire swarm. I will dispatch a specialized agent for this surgical change."
    *   A **Revision Agent** is spawned.

### Step 5.3: Executing the Revision
1.  **System Action (Revision Agent):**
    *   **Input:** The revision prompt, the specific chapter to be edited (Chapter 4), and access to the original knowledge base.
    *   **Process:**
        1.  It queries the knowledge base for the transcript of the interview and the analysis of the specified PDF.
        2.  It identifies the relevant sections in the Chapter 4 draft.
        3.  It rewrites and expands those sections to incorporate the user's feedback.
        4.  The revised chapter is passed back through the **Editor Agent** for a quick consistency check.
        5.  The **Assembler Agent** re-compiles the document with the updated chapter.
2.  **UI State:**
    *   The UI shows a new activity stream for the revision task.
    *   `[Revision Agent]: Received request to revise Chapter 4.`
    *   `[Revision Agent]: Integrating interview analysis with literature review findings.`
    *   `[Revision Agent]: Revision complete. Re-assembling document.`
    *   The document preview and download links are updated with the new version.

### Step 5.4: Task Completion and Learning
1.  **User Action:** The user is satisfied with the revision and closes the session or downloads the final document.
2.  **System Action (Backend):**
    *   The task is marked as `FINALIZED`.
    *   **Continuous Learning (`GEMINI.md` Principle):** A final process is triggered to use the results for system improvement.
    *   The entire task—initial prompt, context files, agent interactions, generated drafts, user revision requests, and the final output—is packaged.
    *   This package is sent to a separate pipeline for:
        *   **Automated Fine-Tuning:** The data can be used to fine-tune the underlying language models to be better at dissertation writing.
        *   **System Analytics:** The performance (time taken, agent efficiency, number of revisions) is logged to identify bottlenecks and areas for improvement in the swarm logic.

This concludes the comprehensive user journey, demonstrating a sophisticated, multi-agent, hierarchical system capable of handling complex, multi-modal academic writing tasks from start to finish.
