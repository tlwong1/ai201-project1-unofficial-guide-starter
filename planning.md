# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
JHU publishes most of what graduate students need to know. The problem is where it's published: across department PDF handbooks, e-catalogue policy pages, and student org bylaws that nobody reads front to back. If you want to know what happens when you miss a registration deadline or what disability accommodations you're entitled to, you're doing a lot of manual digging through documents that weren't written to be user-friendly. This system is built to answer those questions directly, with citations back to the source.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | JHU E-Catalogue | KSAS/WSE Graduate Academic Policies | https://e-catalogue.jhu.edu/ksas-wse/graduate-policies/graduate-policies.pdf |
| 2 | JHU E-Catalogue | Student Conduct Code | https://e-catalogue.jhu.edu/university-wide-policies-information/rights-privileges-responsibilities/student-conduct-code/student-conduct-code.pdf |
| 3 | JHU E-Catalogue | Student Disability Services Policy | https://e-catalogue.jhu.edu/university-wide-policies-information/rights-privileges-responsibilities/student-disability-services/student-disability-services.pdf |
| 4 | JHU E-Catalogue | Tuition and Fees Schedule | https://e-catalogue.jhu.edu/university-wide-policies-information/admission-aid/tuition-fees/tuition-fees.pdf |
| 5 | JHU Student Affairs | GRO Bylaws | https://studentaffairs.jhu.edu/gro/wp-content/uploads/sites/12/2020/03/GRO-By-laws_03-30-2020.pdf |
| 6 | JHU Provost | PhD Student Funding and Wage Types | https://provost.jhu.edu/wp-content/uploads/2025/05/PhD-Funding-and-Wage-Types_030425.pdf |
| 7 | WSE Materials Science | PhD Graduate Student Manual 2025-2026 | https://engineering.jhu.edu/materials/wp-content/uploads/2025/11/PhD-Graduate-Student-Manual-2025-2026.pdf |
| 8 | JHU Education | Registration and Enrollment Guide | https://education.jhu.edu/current-students/academic-support-registration/registration-enrollment/ |
| 9 | KSAS | Graduate Fellowships | https://krieger.jhu.edu/our-community/graduate-fellowships/ |
| 10 | JHU Student Affairs | Student Health and Well-Being Overview | https://studentaffairs.jhu.edu/stfe/wp-content/uploads/sites/4/2024/06/Student-Health-and-Well.Being-6.26.24-red.pdf |
| 11 | JHU Registrar | Extended University Academic Calendar 2025-2026 | http://registrar.jhu.edu/wp-content/uploads/sites/50/2025-2026-Extended-University-Academic-Calendar.pdf |
| 12 | SAIS | Academic Calendar 2026-2027 | https://sais.jhu.edu/sites/default/files/Washington-DC-Academic-Calendar-2627AY-v2.pdf |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 500 tokens

**Overlap:** 75 tokens

**Reasoning:** These are dense policy PDFs, not short reviews. A complete answer to something 
like "how do I appeal a grade" might run three or four paragraphs in the source 
document. Chunks under 200 tokens would cut those explanations in half, leaving 
neither piece useful on its own. Chunks over 800 tokens start bundling unrelated 
topics together, which makes it harder to retrieve the right section for a given 
query.

500 tokens is the middle ground. It's a judgment call 
based on how these documents are structured, and it may need adjusting after 
testing. The 75-token overlap is there for boundary cases: when a key fact like 
a deadline or a dollar figure lands right at the edge of a chunk, it shows up in 
both adjacent chunks instead of getting cut off in one.

Splitting method: LangChain's RecursiveCharacterTextSplitter, breaking on 
paragraph breaks first, then sentences. It follows the document's natural 
structure rather than chopping at arbitrary character counts.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers

**Top-k:** 5

**Production tradeoff reflection:** all-MiniLM-L6-v2 runs locally with no API key and no rate limits, which makes 
it the right fit for this project. Its 256-token limit per chunk isn't a problem 
here since each chunk gets embedded independently.

Top-k is set to 5. Policy questions usually have answers concentrated in one or 
two sections, so 5 chunks gives the LLM what it needs without flooding the 
prompt with noise. If testing shows the right chunk keeps landing just outside 
the top 5, that's when to bump it up.

For a real deployment, the tradeoffs shift. Models like text-embedding-3-large 
or voyage-large-2 handle dense legal and policy language better than MiniLM, 
but they come with API costs and latency. A multilingual model would matter if 
the user base included non-English speakers. The bigger structural tradeoff is 
local vs. API: local embeddings are free and self-contained, but you can't 
upgrade them without redeploying the whole pipeline.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What is the full-time graduate tuition for the 2025-2026 academic year? | $66,670 |
| 2 | How does a student begin the process of requesting disability accommodations at JHU? | Complete the online SDS Application and provide documentation meeting SDS Guidelines for Documentation |
| 3 | What is the non-refundable fee charged when registering for courses at the School of Education? | $175 |
| 4 | What is the Dissertation Prize Fellowship and who is eligible for it? | A fellowship for final-year students to focus on dissertation completion, awarded each semester; students who received it in spring 2025 are ineligible |
| 5 | What health insurance coverage is included as part of a KSAS graduate fellowship? | Health insurance for the award semester |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
