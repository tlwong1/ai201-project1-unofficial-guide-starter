# The Unofficial Guide: JHU Graduate Student Survival System

---

## Domain

This system covers graduate student life and policy at Johns Hopkins University, drawing from official but scattered institutional documents. JHU publishes most of what graduate students need to know. The problem is where it's published: across department PDF handbooks, e-catalogue policy pages, and student org bylaws that nobody reads front to back. If you want to know what happens when you miss a registration deadline or what disability accommodations you're entitled to, you're doing a lot of manual digging through documents that weren't written to be user-friendly. This system answers those questions directly, with citations back to the source.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | JHU E-Catalogue | PDF | https://e-catalogue.jhu.edu/ksas-wse/graduate-policies/graduate-policies.pdf |
| 2 | JHU E-Catalogue | PDF | https://e-catalogue.jhu.edu/university-wide-policies-information/rights-privileges-responsibilities/student-conduct-code/student-conduct-code.pdf |
| 3 | JHU E-Catalogue | TXT | https://e-catalogue.jhu.edu/university-wide-policies-information/rights-privileges-responsibilities/student-disability-services/student-disability-services.pdf |
| 4 | JHU E-Catalogue | PDF | https://e-catalogue.jhu.edu/university-wide-policies-information/admission-aid/tuition-fees/tuition-fees.pdf |
| 5 | JHU Student Affairs | PDF | https://studentaffairs.jhu.edu/gro/wp-content/uploads/sites/12/2020/03/GRO-By-laws_03-30-2020.pdf |
| 6 | JHU Provost | PDF | https://provost.jhu.edu/wp-content/uploads/2025/05/PhD-Funding-and-Wage-Types_030425.pdf |
| 7 | WSE Materials Science | PDF | https://engineering.jhu.edu/materials/wp-content/uploads/2025/11/PhD-Graduate-Student-Manual-2025-2026.pdf |
| 8 | JHU School of Education | TXT | https://education.jhu.edu/current-students/academic-support-registration/registration-enrollment/ |
| 9 | KSAS | TXT | https://krieger.jhu.edu/our-community/graduate-fellowships/ |
| 10 | JHU Student Affairs | PDF | https://studentaffairs.jhu.edu/stfe/wp-content/uploads/sites/4/2024/06/Student-Health-and-Well.Being-6.26.24-red.pdf |

---

## Chunking Strategy

**Chunk size:** 2000 characters (approximately 500 tokens, using a 4 characters-per-token ratio)

**Overlap:** 300 characters (approximately 75 tokens)

**Why these choices fit your documents:** These are dense policy PDFs, not short reviews. A complete answer to something like "how do I appeal a grade" might run three or four paragraphs in the source document. Chunks under 200 tokens would cut those explanations in half, leaving neither piece useful on its own. Chunks over 800 tokens start bundling unrelated topics together, which makes it harder to retrieve the right section for a given query. The 300-character overlap handles boundary cases: when a key fact like a deadline or a dollar figure lands right at the edge of a chunk, it shows up in both adjacent chunks instead of getting cut off in one. LangChain's RecursiveCharacterTextSplitter was used, breaking on paragraph breaks first, then sentences, to follow the document's natural structure rather than chopping at arbitrary character counts.

**Final chunk count:** 210 chunks across 10 documents.

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`, running locally with no API key or rate limits.

**Production tradeoff reflection:** For this project, local embeddings are the right call: free, fast, and self-contained. In a real deployment, the tradeoffs shift. Models like `text-embedding-3-large` (OpenAI) or `voyage-large-2` handle dense legal and policy language better than MiniLM, but they come with API costs and latency. A multilingual model like `multilingual-e5-large` would matter if the user base included non-English-speaking international students, which is plausible for a JHU system. The bigger structural tradeoff is local vs. API: local embeddings have no ongoing cost and no external dependency, but you can't upgrade them without redeploying the entire pipeline. One known limitation of `all-MiniLM-L6-v2` is its 256-token context window. Since chunks are approximately 500 tokens, the model silently truncates longer chunks before embedding, which can hurt recall when the relevant sentence falls in the second half of a chunk.

---

## Grounded Generation

**System prompt grounding instruction:**

```
You are a helpful assistant for Johns Hopkins University graduate students.
Answer the user's question using ONLY the context provided below.
Do not use any outside knowledge. If the answer is not in the context, say so clearly.
At the end of your answer, always list the source documents you drew from under a "Sources:" heading.
Be concise and direct.
```

**How source attribution is surfaced in the response:** The top-5 retrieved chunks are passed to the LLM with their source filenames embedded in the context string (e.g., `[1] Source: tuition-fees.pdf`). The system prompt instructs the model to cite sources in its response. Source filenames are also displayed separately in the Gradio UI's "Sources" panel, populated programmatically from ChromaDB metadata rather than relying on the LLM to list them correctly.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What is the full-time graduate tuition for the 2025-2026 academic year? | $66,670 | "$66,670" with citation to tuition-fees.pdf | Partially relevant (irrelevant PhD Manual chunk ranked first, correct chunk ranked 5th) | Accurate |
| 2 | How does a student begin the process of requesting disability accommodations at JHU? | Complete the online SDS Application and provide documentation meeting SDS Guidelines | Correctly described SDS Application process but added extra details from Health PDF not in expected answer | Partially relevant (correct SDS chunk ranked 3rd behind two PhD Manual chunks) | Partially accurate |
| 3 | What is the non-refundable fee charged when registering for courses at the School of Education? | $175 | "$175" with citation to Registration doc | Relevant | Accurate |
| 4 | What is the Dissertation Prize Fellowship and who is eligible for it? | A fellowship for final-year KSAS students to focus on dissertation writing without teaching obligations; students beyond sixth year in spring 2025 are ineligible | Fully correct description of the fellowship and eligibility criteria | Relevant | Accurate |
| 5 | What happens to a School of Education student who fails to enroll each semester and does not receive an approved leave of absence? | Made inactive and dropped from rolls in second week after semester start; must reapply for admission | Matched expected answer almost word for word | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** "How do I request disability accommodations?" and generally any query where the correct answer lives in a specific policy document but the PhD Graduate Student Manual ranks higher in retrieval.

**What the system returned:** For Q2, the correct SDS Application process was returned, but it was ranked 3rd in retrieval behind two irrelevant PhD Manual chunks. The LLM incorporated extra details from the Health and Well-Being PDF that weren't part of the expected answer, making the response partially accurate rather than accurate.

**Root cause (tied to a specific pipeline stage):** The root cause is at the ingestion and chunking stage. Several documents, particularly the Graduate Policies catalogue page and the Registration doc, contained significant navigation menu content (certificate program lists, sidebar links, social media footers) that wasn't fully stripped during cleaning. These nav-noise chunks were embedded and stored in ChromaDB alongside substantive content. Because nav text tends to mention many programs and services in passing, it produces embeddings that match loosely against a wide range of queries. This dilutes retrieval precision and pushes the relevant chunks down the ranking. Distance scores confirmed this: Q1 (tuition) returned scores of 0.748-0.781, Q2 (disability) returned 0.718-0.908, and Q3 (registration deadline) returned 1.234-1.308, all above the 0.5 threshold the spec identifies as indicating weak matches.

**What you would change to fix it:** Add stricter nav-pattern filtering to `ingest.py`, specifically targeting certificate program list blocks, social media link sections, and repeated sidebar navigation that appears in the scraped text files. After re-ingesting and re-chunking, re-embed and compare distance scores. A hybrid search approach combining semantic search with BM25 keyword matching would also help, since policy-specific terms like "SDS Application" would get higher weight in keyword matching than they do in pure semantic similarity.

---

## Spec Reflection

**One way the spec helped you during implementation:** The planning.md requirement to define 5 specific evaluation questions with verifiable expected answers before writing any code forced a useful constraint. When drafting the questions, it became clear that some initially proposed questions (like "what are the grounds for academic probation") couldn't be confirmed from the actual document text. This forced a closer reading of the source documents and produced better, more honest eval questions. Without that planning step, the evaluation would have been vague and hard to grade.

**One way your implementation diverged from the spec, and why:** The spec described chunk size in tokens (500 tokens, 75 overlap), but LangChain's `RecursiveCharacterTextSplitter` operates on characters, not tokens. The implementation approximated 500 tokens as 2000 characters using a 4 characters-per-token ratio. This is a standard approximation for English text but it introduces some imprecision. A more rigorous implementation would use a token-aware splitter like `tiktoken` to split on actual token counts rather than character proxies.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* The Documents table, Chunking Strategy section, and Architecture diagram from planning.md, plus the list of file types in the documents folder (mix of PDFs and .txt files).
- *What it produced:* A complete `ingest.py` script using pdfplumber for PDFs and BeautifulSoup for text files, with a nav-pattern cleaning function and JSON output per document.
- *What I changed or overrode:* The initial nav-pattern list didn't catch all the navigation noise in the scraped .txt files. After inspecting sample chunks and seeing certificate program lists and social media links appearing in output, I identified this as a known limitation and documented it rather than expanding the pattern list further, in the interest of moving through the pipeline incrementally as the spec recommended.

**Instance 2**

- *What I gave the AI:* The Retrieval Approach section and Architecture diagram from planning.md, plus the ChromaDB collection name and chunk structure from `chunks.json`.
- *What it produced:* `embed.py` with batched embedding using `all-MiniLM-L6-v2`, ChromaDB storage with source metadata, and a 3-query test at the end to verify retrieval before moving to generation.
- *What I changed or overrode:* The generated code initially used `chromadb.Client()` which creates an in-memory database that doesn't persist between runs. I directed the AI to switch to `chromadb.PersistentClient()` with a specified path so the vector store would survive between sessions without needing to re-embed every time.