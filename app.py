import os
import re
import pandas as pd
from rapidfuzz import fuzz
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from fastapi import FastAPI
from fastapi.responses import JSONResponse, RedirectResponse
import gradio as gr
import uvicorn

SUFFIXES = {"ltd","limited","co","company","corp","corporation","inc","incorporated","plc","public","llc","lp","llp","ulc","pc","pllc","sa","ag","nv","se","bv","oy","ab","aps","as","kft","zrt","rt","sarl","sas","spa","gmbh","ug","bvba","cvba","nvsa","pte","pty","bhd","sdn","kabushiki","kaisha","kk","godo","dk","dmcc","pjsc","psc","jsc","ltda","srl","s.r.l","group","holdings","limitedpartnership"}
COUNTRY_EQUIVALENTS = {"uk":"united kingdom","u.k.":"united kingdom","england":"united kingdom","great britain":"united kingdom","britain":"united kingdom","usa":"united states","u.s.a.":"united states","us":"united states","america":"united states","united states of america":"united states","uae":"united arab emirates","u.a.e.":"united arab emirates","south korea":"republic of korea","korea":"republic of korea","north korea":"democratic people's republic of korea","russia":"russian federation","czechia":"czech republic","côte d’ivoire":"ivory coast","cote d'ivoire":"ivory coast","iran":"islamic republic of iran","venezuela":"bolivarian republic of venezuela","taiwan":"republic of china","hong kong sar":"hong kong","macao sar":"macau","prc":"china"}
THRESHOLD = 70

def _normalize_tokens(text):
    if not isinstance(text, str): return ""
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    return " ".join([w for w in text.split() if w not in SUFFIXES]).strip()

def _clean_domain(domain):
    if not isinstance(domain, str): return ""
    domain = domain.lower().strip()
    domain = re.sub(r"^https?://", "", domain)
    domain = re.sub(r"/.*$", "", domain)
    domain = re.sub(r"^www\.", "", domain)
    parts = domain.split(".")
    return parts[-2] if len(parts) >= 2 else domain

def _extract_domain_from_email(email):
    if not isinstance(email, str) or "@" not in email: return ""
    domain = email.split("@")[-1].lower().strip()
    domain = re.sub(r"^www\.", "", domain)
    domain = re.sub(r"/.*$", "", domain)
    return domain

def compare_company_domain(company, domain):
    if not isinstance(company, str) or not isinstance(domain, str):
        return "Unsure – Please Check", 0, "missing input"
    c = _normalize_tokens(company)
    d = _clean_domain(domain)
    if d in c.replace(" ", "") or c.replace(" ", "") in d:
        return "Likely Match", 100, "direct containment"
    score = max(fuzz.token_sort_ratio(c, d), fuzz.partial_ratio(c, d))
    if score >= 85:
        return "Likely Match", score, "strong fuzzy"
    elif score >= THRESHOLD:
        return "Unsure – Please Check", score, "weak fuzzy"
    return "Likely NOT Match", score, "low similarity"

def run_matching(master_file, picklist_file, highlight_changes=True, progress=gr.Progress(track_tqdm=True)):
    try:
        df_master = pd.read_excel(master_file.name)
        df_picklist = pd.read_excel(picklist_file.name)
        df_out = df_master.copy()
        corrected_cells = set()

        # Example simple operation for stability test
        df_out["File_Status"] = "Processed"

        out_file = f"{os.path.splitext(master_file.name)[0]}_Results.xlsx"
        df_out.to_excel(out_file, index=False)
        return out_file
    except Exception as e:
        return f"❌ Error: {str(e)}"

demo = gr.Interface(
    fn=run_matching,
    inputs=[
        gr.File(label="Upload MASTER Excel file (.xlsx)"),
        gr.File(label="Upload PICKLIST Excel file (.xlsx)"),
        gr.Checkbox(label="Highlight changed values (blue)", value=True),
    ],
    outputs=gr.File(label="Download Processed File"),
    title="📊 Master–Picklist + Domain Matching Tool",
    description="Upload MASTER & PICKLIST Excel files to process and download results.",
    allow_flagging="never",
)

app = FastAPI()

@app.get("/")
def root():
    return RedirectResponse(url="/gradio", status_code=307)

app = gr.mount_gradio_app(app, demo, path="/gradio")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), log_level="info")
