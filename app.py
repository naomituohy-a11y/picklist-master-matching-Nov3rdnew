import os
import gradio as gr
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

# =========================
# 1) YOUR EXISTING CODE
# =========================
# Paste ALL your previous logic (helpers, compare_company_domain, run_matching, etc.)
# Keep/ensure your Gradio Interface is constructed like:
#
# demo = gr.Interface(
#     fn=run_matching,
#     inputs=[
#         gr.File(label="Upload MASTER Excel file (.xlsx)"),
#         gr.File(label="Upload PICKLIST Excel file (.xlsx)"),
#         gr.Checkbox(label="Highlight changed values (blue)", value=True)
#     ],
#     outputs=gr.File(label="Download Processed File"),
#     title="📊 Master–Picklist + Domain Matching Tool",
#     description="Upload MASTER & PICKLIST Excel files to auto-match, validate domains, map questions, and optionally highlight changed values.",
#     # ⬇️ This is IMPORTANT to avoid the JSON-schema /info crash
#     show_api=False
# )
#
# >>> YOUR EXISTING FUNCTION CODE HERE <<<


# =========================
# 2) FASTAPI WRAPPER
# =========================
app = FastAPI()

@app.get("/health")
def health():
    return JSONResponse({"status": "ok"})

# Mount Gradio onto FastAPI at root
# (This provides the UI at "/" and keeps /health for Railway)
app = gr.mount_gradio_app(app, demo, path="/")


# =========================
# 3) LAUNCH (Railway)
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "7860"))
    # Run uvicorn so FastAPI+Gradio both work cleanly on Railway
    uvicorn.run("app:app", host="0.0.0.0", port=port, log_level="info")
