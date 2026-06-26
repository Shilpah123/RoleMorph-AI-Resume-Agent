# RoleMorph: AI Resume Optimization Agent System
## Kaggle Competition Submission

**Version:** 1.0  
**Multi-Agent Architecture:** 9 Specialized Agents

---

## 🎯 Project Overview

RoleMorph transforms how candidates present their real experience—using 9 coordinated AI agents to align resumes with job descriptions while preserving truth and integrity. It helps job seekers bridge the gap between their genuine skills and ATS requirements without fabricating or inflating credentials.

### Key Features
- **9 Specialized Agents** working in a coordinated pipeline
- **Semantic ATS Scoring** (beyond keyword matching)
- **Real-time Agent Workflow Visualization**
- **Before/After Score Comparison**
- **Explainability Panel** showing agent actions
- **Interview-Safe** (no fabrication or hallucination)

---

## 💡 Why RoleMorph Matters

In today's job market, candidates often apply to hundreds of roles with minimal response rates—not due to lack of skill, but due to poor alignment with ATS systems. RoleMorph addresses this gap by helping candidates present their existing experience in a way that is both optimized and truthful.

Unlike typical resume tools, RoleMorph does not generate experience—it restructures and enhances existing experience through explainable multi-agent collaboration.

---

## 🤖 Multi-Agent Architecture

### The 9-Agent System

Each agent has a specialized cognitive role in the pipeline:

1. **Job Analysis Agent** → understands hiring intent and role structure
2. **Keyword Surfacer** → extracts high-impact ATS keywords
3. **Gap Analysis Agent** → identifies missing or weak alignment areas
4. **Transferable Skills Mapper** → bridges cross-domain experience
5. **Summary Quality Scorer** → evaluates narrative strength
6. **Summary Rewriter Agent** → rewrites for clarity and alignment
7. **Bullet Optimizer Agent** → enhances impact of experience points
8. **ATS Scoring Agent** → computes deterministic compatibility score
9. **Resume Orchestrator** → coordinates full pipeline execution

### Agent Workflows

**Analyze Match** (5 agents):
```
Resume + Job Description
        ↓
 Job Analysis Agent
        ↓
  Keyword Surfacer
        ↓
 Gap Analysis Agent
        ↓
Transferable Skills Mapper
        ↓
  ATS Scoring Agent
        ↓
   Score Output
```

**Customize Resume** (all 9 agents):
```
Resume + Job Description
        ↓
 Job Analysis Agent
        ↓
  Keyword Surfacer
        ↓
 Gap Analysis Agent
        ↓
Transferable Skills Mapper
        ↓
Summary Quality Scorer
        ↓
Summary Rewriter Agent
        ↓
 Bullet Optimizer Agent
        ↓
  ATS Scoring Agent
        ↓
 Resume Orchestrator
        ↓
Optimized Resume Output
```

---

## 📁 Files Included

### Core Application
- `final_app.py` - Main UI and orchestration
- `generic_rewriter.py` - Core resume processing logic
- `document_utils.py` - Document handling utilities

### Agents (agents/ folder)
- `job_analysis_agent.py`
- `keyword_surfacer.py`
- `gap_analysis_agent.py`
- `transferable_skills_mapper.py`
- `summary_quality_scorer.py`
- `summary_rewriter_agent.py`
- `bullet_optimizer_agent.py`
- `ats_scoring_agent.py`
- `resume_orchestrator.py`

### Documentation
- `AGENT_ARCHITECTURE.md` - Detailed agent documentation
- `README.md` - Full project documentation
- `requirements.txt` - Python dependencies

### Launcher
- `RUN_NO_CACHE.bat` - Launch script (Windows)

---

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Running the Application

**Windows:**
```bash
RUN_NO_CACHE.bat
```

**Linux/Mac:**
```bash
python final_app.py
```

### Usage

1. **Upload Resume** - Click "Browse Resume (.docx)" and select your .docx file
2. **Paste Job Description** - Copy/paste the complete job description
3. **Analyze Match** - See ATS score and skill analysis (5 agents execute)
4. **Customize Resume** - Generate optimized resume (all 9 agents execute)
5. **View Results** - Click "📊 View Results" to see detailed analysis

---

## 🎨 UI Features

### Analysis Dashboard
- **ATS Compatibility Score** with progress bar
- **Confidence Level** (HIGH/MEDIUM/LOW)
- **Match Score** percentage
- **Before/After Score Comparison** (for customization)

### Agent Workflow Panel
- Real-time visualization of agent execution
- ✓ Green checkmarks for executed agents
- ○ Gray circles for pending agents

### RoleMorph Actions Panel
- Explainability showing what each agent did
- Examples:
  - "✓ Identified 8 strong skill matches"
  - "✓ Extracted 12 key requirements"
  - "✓ Rewrote professional summary"
  - "✓ Enhanced 6 bullet points"

---

## 🔍 Technical Highlights

### Semantic Intelligence
- Word boundary matching (prevents false positives)
- Skill normalization (maps resume skills to job equivalents)
- Role adjacency detection (e.g., Technical Writer ↔ Medical Writer)
- Transferable skills mapping across domains

### No Fabrication
- All agents preserve factual accuracy
- No hallucination of experience
- Interview-safe outputs
- Only reorders/enhances existing content

### ATS Scoring Components
- Keyword Match (40% weight)
- Skills Match (25% weight)
- Experience Match (20% weight)
- Title Alignment (10% weight)
- Education Match (5% weight)

**The scoring system is deterministic and explainable, ensuring consistent evaluation across runs.**

---

## 📊 Performance & Evaluation

RoleMorph demonstrates consistent and explainable improvements in resume-job alignment:

- **ATS Score Improvement:** ~10–20 point average uplift
- **Processing Time:** 5–10 seconds (analysis), 15–20 seconds (optimization)
- **Output Quality:** High factual fidelity with no hallucination
- **Reliability:** Deterministic scoring across repeated runs
- **Format Support:** .docx only (Word 2007+)


## 🛠️ System Requirements

- Python 3.8+
- Windows/Linux/Mac
- 4GB RAM minimum
- OpenAI API key (optional - for enhanced features)



## 📝 License

This project is submitted for the Kaggle AI Agents Competition.


