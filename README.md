# Accord Project Agentic Template Generator
### GSoC 2025 — Project 1: Agentic Workflow for Drafting Templates

> **Proof of Concept** demonstrating a multi-agent AI system that generates valid Accord Project templates from plain English requirements.

---

## 🎯 What This Does

You type a legal template requirement in plain English. Five specialized AI agents collaborate to produce a complete, validated Accord Project template package.

```
"Create a non-disclosure agreement between two companies with a 3-year confidentiality period"
          ↓
  [Requirements Analyst Agent]   →  Structured spec + fetches examples
          ↓
  [Concerto Modeler Agent]       →  Generates & validates .cto model
          ↓
  [TemplateMark Author Agent]    →  Writes & validates .tem.md template
          ↓
  [Package Composer Agent]       →  Assembles package.json + README + saves files
          ↓
  [QA Validator Agent]           →  Final review + quality score
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Interface (main.py)                    │
│              Interactive mode  |  Single-shot mode            │
└────────────────────────┬────────────────────────────────────┘
                         │ User Requirements (natural language)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  CrewAI Orchestrator (crew.py)               │
│                   Sequential Agent Pipeline                   │
└──┬──────────┬──────────┬──────────┬──────────┬─────────────┘
   │          │          │          │          │
   ▼          ▼          ▼          ▼          ▼
┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐
│Agent1│  │Agent2│  │Agent3│  │Agent4│  │Agent5│
│Req.  │  │Cncrt │  │Tmplt │  │Pkg   │  │QA    │
│Anlst │  │Modlr │  │Auth  │  │Comp  │  │Valid │
└──┬───┘  └──┬───┘  └──┬───┘  └──┬───┘  └──┬───┘
   │          │          │          │          │
   ▼          ▼          ▼          ▼          ▼
┌─────────────────────────────────────────────────────────────┐
│                      Tool Layer (tools.py)                   │
│  validate_concerto_model  |  validate_templatemark           │
│  fetch_accord_examples    |  save_template_files             │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Accord Project CLI Tools (external)             │
│    @accordproject/concerto-tools  |  @accordproject/template-engine  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/accord-gsoc-poc
cd accord-gsoc-poc
pip install -r requirements.txt
```

### 2. Set your API key

```bash
cp .env.example .env
# Edit .env and add your API key
```

```env
OPENAI_API_KEY=sk-...          # for GPT models
ANTHROPIC_API_KEY=sk-ant-...   # for Claude models
GOOGLE_API_KEY=...             # for Gemini models
```

### 3. Run

**Interactive mode (like claude-code CLI):**
```bash
python main.py
```

**Single-shot mode:**
```bash
python main.py -r "Create an NDA between two companies with 2 year confidentiality"
python main.py -r "Late payment penalty clause with 1.5% monthly interest" --model claude-3-5-sonnet
python main.py -r "IP transfer agreement" --model gemini-1.5-pro --output ./my-template
```

---

## 🤖 Agents

| Agent | Role | Tools |
|-------|------|-------|
| Requirements Analyst | Parses natural language → structured spec | `fetch_accord_examples` |
| Concerto Modeler | Generates validated `.cto` model | `validate_concerto_model`, `fetch_accord_examples` |
| TemplateMark Author | Writes validated `.tem.md` template | `validate_templatemark`, `fetch_accord_examples` |
| Package Composer | Assembles full template package | `save_template_files` |
| QA Validator | Final review + quality score | `validate_concerto_model`, `validate_templatemark` |

---

## 🛠️ Tools

| Tool | Description |
|------|-------------|
| `validate_concerto_model` | Runs `concerto validate` CLI (falls back to static checks) |
| `validate_templatemark` | Runs `template-engine validate` CLI (falls back to static checks) |
| `fetch_accord_examples` | Returns reference Accord Project template examples |
| `save_template_files` | Saves all template files in standard Accord Project structure |

---

## 📁 Output Structure

```
output/
├── model/
│   └── model.cto          ← Concerto data model
├── text/
│   └── template.tem.md    ← TemplateMark template
├── package.json           ← Template metadata
└── README.md              ← Template documentation
```

---

## 🔧 Supported Models

| Flag | Model |
|------|-------|
| `--model gpt-4o-mini` | OpenAI GPT-4o mini (default, cheapest) |
| `--model gpt-4o` | OpenAI GPT-4o (best quality) |
| `--model claude-3-5-sonnet` | Anthropic Claude 3.5 Sonnet |
| `--model gemini-1.5-pro` | Google Gemini 1.5 Pro |

---

## 📋 Example Output

**Input:** `"Non-disclosure agreement between two tech companies, 3 year confidentiality, governed by California law"`

**Generated files:**

`model/model.cto`:
```concerto
namespace org.accordproject.nda@1.0.0

import org.accordproject.contract.Contract from https://models.accordproject.org/...

concept NDAContract extends Contract {
  o String disclosingPartyName
  o String receivingPartyName
  o DateTime effectiveDate
  o Integer confidentialityPeriodYears
  o String governingLaw
}
```

`text/template.tem.md`:
```markdown
# Non-Disclosure Agreement

This Agreement is entered into as of {{effectiveDate}} between 
{{disclosingPartyName}} and {{receivingPartyName}}.

The Receiving Party shall maintain confidentiality for 
{{confidentialityPeriodYears}} years. Governed by {{governingLaw}} law.
```

---

## 🗺️ GSoC Project Roadmap

This POC demonstrates the core concept. The full GSoC project will add:

- [ ] Full MCP server integration for Accord Project tools
- [ ] Support for template logic generation (TypeScript)  
- [ ] Web UI interface alongside CLI
- [ ] LangGraph / other orchestrator backends
- [ ] Template versioning and iterative refinement
- [ ] Integration with Template Playground

---

## 📄 License

Apache-2.0 — same as Accord Project

---

*Built for GSoC 2025 — Accord Project | Project 1: Agentic Workflow for Drafting Templates*
