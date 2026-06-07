"""
app.py
Gradio web interface for the JHU Unofficial Guide RAG system.
Run with: python app.py
Then open http://localhost:7860 in your browser.
"""

import gradio as gr
from query import query


def handle_query(question: str):
    if not question.strip():
        return "Please enter a question.", ""

    result = query(question, verbose=False)

    sources = "\n".join(f"• {s}" for s in dict.fromkeys(result["sources"]))
    return result["answer"], sources


with gr.Blocks(title="JHU Unofficial Guide") as demo:
    gr.Markdown("# JHU Unofficial Guide")
    gr.Markdown(
        "Ask questions about JHU graduate student policies, tuition, "
        "disability services, registration, fellowships, and more. "
        "Answers are grounded in official JHU documents."
    )

    with gr.Row():
        inp = gr.Textbox(
            label="Your question",
            placeholder="e.g. What is the full-time graduate tuition?",
            lines=2,
        )

    btn = gr.Button("Ask", variant="primary")

    with gr.Row():
        answer = gr.Textbox(label="Answer", lines=10)
        sources = gr.Textbox(label="Sources", lines=10)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

    gr.Examples(
        examples=[
            ["What is the full-time graduate tuition for 2025-2026?"],
            ["How do I request disability accommodations at JHU?"],
            ["What is the non-refundable registration fee at the School of Education?"],
            ["What is the Dissertation Prize Fellowship?"],
            ["What happens if I don't enroll and don't get a leave of absence?"],
        ],
        inputs=inp,
    )

if __name__ == "__main__":
    demo.launch()
