# Resume Assets

## Project Title
**Cloud-Native Serverless RAG System**

## One-Line Description
Designed and deployed a highly-scalable, stateless Retrieval-Augmented Generation (RAG) backend utilizing Chroma Cloud, Supabase Storage, and Groq LLMs.

## Resume Bullet Points

- **Architected a stateless RAG backend** utilizing FastAPI, decoupling vector indices (Chroma Cloud) and binary storage (Supabase) to support horizontally scalable, zero-persistence containerized deployments.
- **Resolved severe memory limit constraints** by profiling and migrating from local PyTorch `sentence-transformers` (380MB overhead) to serverless Gemini Embeddings, reducing container cold-start times by 90% and fitting within 512MB deployment limits.
- **Implemented a reliable multi-provider AI pipeline** combining LLaMA-3 (via Groq) for rapid generation with Gemini for embeddings, yielding high-performance document Q&A with sub-second retrieval latency.
- **Developed a precise citation engine** that maps generated answers directly back to chunk-level page numbers and public Supabase document URLs for seamless source verification.
- **Engineered an end-to-end production CI/CD configuration** using Docker and Render specifications, establishing rigorous functional and disaster recovery validations for cloud environments.

## Interview Talking Points

- **The Problem with Local Tutorials**: Most tutorials use local SQLite Chroma DBs and load `sentence-transformers` into memory. Explain how you hit a wall when deploying to Render's free tier because the container ran out of memory (OOM) and the local SQLite file kept getting wiped on every redeploy.
- **The Solution**: Explain how you separated state from compute. Moved the vectors to Chroma Cloud. Moved the PDFs to Supabase Object Storage. Moved the embeddings to the Gemini API.
- **The Result**: A truly cloud-native, stateless application. The container boots instantly because it doesn't need to load PyTorch into memory, and your documents survive redeployments because the storage is externalized.
