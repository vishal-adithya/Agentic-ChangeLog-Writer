import os
import tempfile
import gradio as gr
import streamlit as st
from agent import agent_pipeline
from datetime import datetime


 
def normalize_date(raw: str) -> str:
    """
    gr.DateTime can hand back 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD'
    depending on config/version. Always collapse to YYYY-MM-DD since
    that's what the agent's system prompt expects.
    """
    if not raw:
        return ""
    raw = raw.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return raw
 
 
def run_agent(git_url, start_date, end_date, groq_key, github_token, progress=gr.Progress()):
    progress(0, desc="Validating inputs...")
 
    if not git_url:
        gr.Warning("Please provide a GitHub repo URL.")
        return "⚠️ Please provide a GitHub repo URL.", "", None
 
    start = normalize_date(start_date)
    end = normalize_date(end_date)
 
    if not start or not end:
        gr.Warning("Please select both a start and end date.")
        return "⚠️ Please select both a start and end date.", "", None
    if not groq_key:
        gr.Warning("Please provide a Groq API key in the sidebar.")
        return "⚠️ Please provide a Groq API key in the sidebar.", "", None
    if not github_token:
        gr.Warning("Please provide a GitHub token in the sidebar.")
        return "⚠️ Please provide a GitHub token in the sidebar.", "", None
 
    progress(0.25, desc="Setting up credentials...")
    os.environ["GROQ_API_KEY"] = groq_key
    os.environ["GITHUB_TOKEN"] = github_token
 
    question = f"{git_url}, from {start} to {end}"
 
    progress(0.5, desc="Fetching commits and writing changelog...")
    try:
        result = agent_pipeline(question)
    except Exception as e:
        gr.Warning(f"Agent error: {e}")
        return f"❌ Error running agent_pipeline: {e}", "", None
 
    progress(0.9, desc="Preparing download...")
    tmp_path = os.path.join(tempfile.gettempdir(), "changelog.md")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(result)
 
    progress(1.0, desc="Done")
    gr.Info("Changelog generated.")
    return result, result, tmp_path
 
 
with gr.Blocks(
    title="Changelog Writer",
    theme=gr.Theme.from_hub("nicognaw/nk-ui"),
    fill_width=True,
) as demo:
 
    with gr.Sidebar(position="left"):
        gr.Markdown("### Credentials")
        gr.Markdown("Stored only in memory for this session — never written to disk.")
        groq_key = gr.Textbox(
            label="Groq API Key",
            type="password",
            placeholder="GROQ_API_KEY",
        )
        github_token = gr.Textbox(
            label="GitHub Token",
            type="password",
            placeholder="GITHUB_TOKEN",
        )
 
    gr.Image("logo.png")
    gr.Markdown("Generate a changelog for a GitHub repo over a given date range.")
 
    with gr.Group():
        git_url = gr.Textbox(
            label="GitHub Repo URL",
            placeholder="https://github.com/vishal-adithya/changelog-test-repo",
        )
        with gr.Row():
            start_date = gr.DateTime(label="Start Date", include_time=False, type="string")
            end_date = gr.DateTime(label="End Date", include_time=False, type="string")
        with gr.Row():
            generate_btn = gr.Button("Generate Changelog", variant="primary", size="lg")
            clear_btn = gr.ClearButton(size="lg")
 
    with gr.Tabs():
        with gr.Tab("Rendered"):
            output_md = gr.Markdown()
        with gr.Tab("Raw Markdown"):
            output_code = gr.Code(language="markdown", interactive=False, show_line_numbers=False)
 
    download_btn = gr.DownloadButton("Download as .md")
 
    clear_btn.add([git_url, start_date, end_date, output_md, output_code])
 
    generate_btn.click(
        fn=run_agent,
        inputs=[git_url, start_date, end_date, groq_key, github_token],
        outputs=[output_md, output_code, download_btn],
    )
 
if __name__ == "__main__":
    demo.launch()