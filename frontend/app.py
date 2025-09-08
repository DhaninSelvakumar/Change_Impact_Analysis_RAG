import streamlit as st
import requests
import json
import os
import plotly.express as px
import pandas as pd
from pathlib import Path
import tempfile

st.set_page_config(
    page_title="Change Impact Analysis",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">📄 Change Impact Analysis System</h1>', unsafe_allow_html=True)
st.markdown("**Powered by RAG + LLaMA** | Analyze document changes and their impacts")

# Sidebar
st.sidebar.header("Configuration")
backend_url = st.sidebar.text_input("Backend URL", value="http://127.0.0.1:8000")

# Test connection
try:
    response = requests.get(f"{backend_url}/", timeout=5)
    if response.status_code == 200:
        st.sidebar.success("✅ Backend Connected")
    else:
        st.sidebar.error("❌ Backend Error")
except:
    st.sidebar.error("❌ Backend Unavailable")

# Ensure tmpdirs persist in session
if "old_tmpdir" not in st.session_state:
    st.session_state.old_tmpdir = None
if "new_tmpdir" not in st.session_state:
    st.session_state.new_tmpdir = None

# Main interface
col1, col2 = st.columns(2)

with col1:
    st.subheader("📁 Old Version")
    old_files = st.file_uploader(
        "Upload files from the OLD version",
        type=["txt", "md", "py", "json", "csv"],
        accept_multiple_files=True
    )
    old_folder = None
    if old_files:
        st.session_state.old_tmpdir = tempfile.TemporaryDirectory()
        old_folder = st.session_state.old_tmpdir.name
        for file in old_files:
            file_path = Path(old_folder) / file.name
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
        st.success(f"Uploaded {len(old_files)} old files")

with col2:
    st.subheader("📁 New Version")
    new_files = st.file_uploader(
        "Upload files from the NEW version",
        type=["txt", "md", "py", "json", "csv"],
        accept_multiple_files=True
    )
    new_folder = None
    if new_files:
        st.session_state.new_tmpdir = tempfile.TemporaryDirectory()
        new_folder = st.session_state.new_tmpdir.name
        for file in new_files:
            file_path = Path(new_folder) / file.name
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
        st.success(f"Uploaded {len(new_files)} new files")

# Analysis section
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🔍 Analyze Changes", type="primary", use_container_width=True):
        if not old_folder or not new_folder:
            st.error("Please upload files for both old and new versions")
        else:
            with st.spinner("Analyzing changes... This may take a few minutes."):
                try:
                    response = requests.post(
                        f"{backend_url}/analyze/",
                        params={"old_folder": old_folder, "new_folder": new_folder},
                        timeout=300
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.analysis_results = data
                        st.success("Analysis completed successfully!")
                        st.rerun()
                    else:
                        st.error(f"Analysis failed: {response.json().get('detail', 'Unknown error')}")
                except requests.exceptions.Timeout:
                    st.error("Analysis timed out. Please try again.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Display results
if 'analysis_results' in st.session_state:
    data = st.session_state.analysis_results
    
    st.markdown("---")
    st.header("📊 Analysis Results")
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    differences = data.get('differences', [])
    
    with col1:
        st.metric("Total Changes", len(differences))
    with col2:
        modified_count = len([d for d in differences if d['type'] == 'modified'])
        st.metric("Modified Files", modified_count)
    with col3:
        deleted_count = len([d for d in differences if d['type'] == 'deleted'])
        st.metric("Deleted Files", deleted_count)
    
    # Changes breakdown
    if differences:
        st.subheader("🔹 Changes Detected")
        df = pd.DataFrame(differences)
        type_counts = df['type'].value_counts()
        fig = px.pie(values=type_counts.values, names=type_counts.index, title="Change Type Distribution")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📋 Detailed Changes")
        for i, diff in enumerate(differences):
            with st.expander(f"{diff['file']} - {diff['type'].title()}", expanded=i < 3):
                st.write(f"**Type**: {diff['type']}")
                st.write(f"**Description**: {diff['description']}")
                if 'details' in diff and isinstance(diff['details'], dict):
                    if 'additions' in diff['details']:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Lines Added", diff['details']['additions'])
                        with col2:
                            st.metric("Lines Deleted", diff['details']['deletions'])
                    if 'diff_preview' in diff['details'] and diff['details']['diff_preview']:
                        st.code(diff['details']['diff_preview'][:500], language='diff')
    
    # Impact analysis
    st.subheader("🎯 Impact Analysis")
    impact_analysis = data.get('impact_analysis', 'No analysis available')
    st.markdown(impact_analysis)
    
    if data.get('related_contexts_count', 0) > 0:
        st.info(f"Found {data['related_contexts_count']} related documents that may be impacted")
    
    # Export results
    st.subheader("💾 Export Results")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Download as JSON"):
            st.download_button(
                label="Download JSON",
                data=json.dumps(data, indent=2),
                file_name="change_impact_analysis.json",
                mime="application/json"
            )
    with col2:
        if st.button("Download Report"):
            report = f"""# Change Impact Analysis Report
            
## Summary
- Total Changes: {len(differences)}
- Modified Files: {len([d for d in differences if d['type'] == 'modified'])}
- Deleted Files: {len([d for d in differences if d['type'] == 'deleted'])}
- Added Files: {len([d for d in differences if d['type'] == 'added'])}

## Impact Analysis
{impact_analysis}

## Changes Detail
"""
            for diff in differences:
                report += f"\n### {diff['file']} ({diff['type']})\n{diff['description']}\n"
            st.download_button(
                label="Download Report",
                data=report,
                file_name="change_impact_report.md",
                mime="text/markdown"
            )

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit, FastAPI, RAG, and LLaMA")
