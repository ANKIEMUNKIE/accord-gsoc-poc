# GSoC 2025 Proposal
## Agentic Workflow for Drafting Accord Project Templates

**Organization:** Accord Project
**Project:** Project 1 — Agentic Workflow for Drafting Templates
**Mentors:** Sanket Shevkar, Niall Roche
**Project Size:** 90 hours / 8 weeks
**Category:** Risky/Exploratory
**Proposal Submitted:** March 2026

---

## 1. About Me

**Name:** Ankit Kumar Yadav
**Email:** ay97948328@gmail.com
**GitHub:** https://github.com/ANKIEMUNKIE
**Location:** Chennai, Tamil Nadu, India
**Time Zone:** IST (UTC+5:30)
**University:** SRM University
**Degree:** B.Tech, CSE Data Science — 2nd Year

### Background

I am a 2nd year B.Tech student at SRM University, Chennai, specializing in Data Science. I am passionate about building AI-powered developer tools that make complex workflows accessible to non-experts. Over the past year I have built several Python projects involving LLM APIs and agentic systems.

**Relevant Skills:**
- **Python:** 2+ years of experience; used for backend scripting, data pipelines, and API integrations
- **LLM APIs:** Hands-on experience with OpenAI, Anthropic, Groq, and Google AI APIs
- **Agentic Frameworks:** Hands-on experience with CrewAI for multi-agent workflows; familiar with LangChain
- **TypeScript / Node.js:** Basic proficiency; comfortable reading and writing TS code
- **Git / GitHub:** Daily driver for version control; familiar with PRs, reviews, issues

### Why Accord Project?

I first encountered Accord Project while researching how AI can assist in legal document automation. The stack — Concerto for data modelling, TemplateMark for document generation, and TypeScript for smart contract logic — is uniquely positioned to become the backbone of AI-assisted contract drafting. The idea of using agents to automate this pipeline excites me because it sits at the intersection of legal AI, agentic systems, and open-source tooling — all areas I deeply care about.

---

## 2. Project Overview

### Problem Statement

Today, creating an Accord Project template requires a person to have:
1. **Legal/domain expertise** — understanding of the contract being modeled
2. **Concerto knowledge** — the data modeling language's syntax and type system
3. **TemplateMark knowledge** — the template markup format
4. **TypeScript knowledge** — for contract execution logic

This high barrier to entry slows adoption and limits who can create templates. Junior legal engineers, law students, and domain experts without programming backgrounds are effectively excluded.

### Proposed Solution

Build an **agentic workflow system** where a team of specialized AI agents collaborate to generate a complete, validated Accord Project template from a plain English requirement description. The user only needs to describe what they want — the agents handle everything else.

```
User: "Create an NDA between two companies with 3-year confidentiality, governed by California law"
          ↓  (10-30 seconds)
System: Produces validated model.cto + template.tem.md + package.json + README
```

---

## 3. Technical Architecture

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                       │
│         CLI (like claude-code)  |  Web UI (future)           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Agentic Orchestrator Layer                   │
│         CrewAI  |  LangGraph  |  (pluggable backend)         │
│                                                               │
│   Agent 1: Requirements Analyst                               │
│   Agent 2: Concerto Data Modeler                              │
│   Agent 3: TemplateMark Author                                │
│   Agent 4: Package Composer                                   │
│   Agent 5: QA Validator                                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Tool Calling Layer                         │
│   validate_concerto_model  |  validate_templatemark           │
│   fetch_accord_examples    |  save_template_files             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                Accord Project CLI Tools (external)           │
│   @accordproject/concerto-tools                               │
│   @accordproject/template-engine                              │
│   (invoked via subprocess / MCP server)                       │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Agent Design

The system uses **5 specialist agents** with distinct roles, prompts, and tool access:

#### Agent 1: Requirements Analyst
- **Role:** Parse natural language → structured specification
- **Input:** Raw user requirements string
- **Output:** Structured spec (contract type, parties, fields, clauses, jurisdiction)
- **Tools:** `fetch_accord_examples` — retrieves reference templates from Accord library
- **Key Design:** Extracts field names with their data types (String, Integer, DateTime, etc.)

#### Agent 2: Concerto Data Modeler
- **Role:** Generate and validate the `.cto` Concerto model
- **Input:** Structured spec from Agent 1
- **Output:** Validated `.cto` file content
- **Tools:** `validate_concerto_model`, `fetch_accord_examples`
- **Key Design:** Iterative loop — generates, validates, fixes until model is clean

#### Agent 3: TemplateMark Author
- **Role:** Write the legal template text with Handlebars variable bindings
- **Input:** Structured spec + validated Concerto model
- **Output:** Validated `.tem.md` template file
- **Tools:** `validate_templatemark`, `fetch_accord_examples`
- **Key Design:** Cross-reference check ensures every `{{variable}}` exists in the model

#### Agent 4: Package Composer
- **Role:** Assemble the complete Accord Project package
- **Input:** Validated model + template from previous agents
- **Output:** `package.json`, `README.md`, all files saved to disk
- **Tools:** `save_template_files`
- **Key Design:** Generates correct Accord Project metadata schema in `package.json`

#### Agent 5: QA Validator
- **Role:** Final quality review with actionable report
- **Input:** All artifacts from previous agents
- **Output:** QA report with pass/fail checks and quality score
- **Tools:** `validate_concerto_model`, `validate_templatemark`
- **Key Design:** Produces a score (1-10) and specific remediation steps for issues

### 3.3 Tool Calling Design

Tools are designed as **thin wrappers** over Accord Project CLI commands, enabling agents to call real validation tooling:

```python
@tool("validate_concerto_model")
def validate_concerto_model(cto_content: str) -> str:
    """Invokes: npx concerto validate --model <temp_file>"""
    # Writes content to temp file, runs CLI, returns stdout/stderr
    # Falls back to static validation if CLI not installed
```

This design means:
- Agents get **real feedback** from the actual Accord Project toolchain
- The system **degrades gracefully** if tools are not installed (static fallback)
- Tools are **orchestrator-agnostic** — same tools work with CrewAI, LangGraph, or any framework

### 3.4 LLM Model Flexibility

The system supports multiple LLM providers via a unified interface:

| Provider | Models |
|----------|--------|
| OpenAI | gpt-4o, gpt-4o-mini |
| Anthropic | claude-3-5-sonnet |
| Google | gemini-1.5-pro |
| Local | ollama/llama3 (stretch goal) |

---

## 4. CLI Interface

The CLI mirrors the developer experience of `gemini-cli` and `claude-code`:

```bash
# Interactive mode
$ python main.py
╔═══════════════════════════════════════════════════════╗
║     Accord Project Template Generator (GSoC POC)      ║
╚═══════════════════════════════════════════════════════╝

📝 Template Requirements > Create a late payment penalty clause
                            with 1.5% monthly interest and 10-day grace period

🚀 Starting agentic workflow...
  [Agent 1] Analyzing requirements...
  [Agent 2] Generating Concerto model...
  [Agent 3] Writing TemplateMark template...
  [Agent 4] Composing package...
  [Agent 5] Running QA validation...

✅ Template generated! Files saved to ./output/

# Single-shot mode
$ python main.py -r "NDA between two parties" --model claude-3-5-sonnet --output ./my-nda
```

---

## 5. Expected Outcomes

All outcomes from the project description will be delivered:

| # | Outcome | Delivery |
|---|---------|----------|
| 1 | Define Agent Personas and Tasks (orchestrator-agnostic) | `agents.py` — clean agent definitions usable with any framework |
| 2 | Tool calling for Accord Project tools (concerto, template-engine) | `tools.py` — 4 tools wrapping real CLI validation |
| 3 | Option to choose AI models | `--model` flag supporting 4+ providers |
| 4 | CLI interface (interactive + single-shot) | `main.py` with rich terminal UI |

### Stretch Goals (if time allows)
- Web UI alongside CLI using FastAPI + React
- TypeScript logic file generation (Agent 6: Logic Engineer)
- MCP server wrapping the agentic workflow
- Integration into Template Playground

---

## 6. Implementation Plan (8 Weeks)

### Week 1 — Setup & Deep Dive
- Fork Accord Project repos: `concerto`, `template-engine`, `template-playground`
- Study Concerto language spec, TemplateMark spec, and existing template examples
- Set up development environment with all Accord Project CLI tools
- First PR: Fix any existing bug (to establish contribution history)
- Finalize agent persona design with mentors' feedback

### Week 2 — Tool Layer
- Implement all 4 tools in `tools.py`
- Write unit tests for each tool (valid input, invalid input, CLI fallback)
- Test tools against real Accord Project CLI tools
- Document tool signatures and expected inputs/outputs

### Week 3 — Agent Definitions
- Implement all 5 agent definitions in `agents.py`
- Fine-tune agent prompts with real examples
- Test each agent independently with mock inputs
- Iterative prompt engineering to improve output quality

### Week 4 — CrewAI Orchestration
- Implement `crew.py` with full sequential pipeline
- Test end-to-end with 5+ different template types (NDA, late payment, IP transfer, service agreement, SLA)
- Measure and improve template quality based on QA agent scores
- Handle edge cases: vague requirements, conflicting fields, unsupported types
- Migrate existing Accord Project templates from Ergo logic layer to TypeScript, using the agentic workflow to automate the conversion process.
### Week 5 — CLI Interface
- Implement `main.py` with interactive and single-shot modes
- Add `--model` flag for multi-provider LLM support
- Add `--output` flag for custom output directories
- Add progress indicators and rich terminal formatting
- Write end-to-end integration tests

### Week 6 — MCP Integration
- Wrap `validate_concerto_model` and `validate_templatemark` as MCP tools
- Ensure agents can call tools via MCP protocol (not just subprocess)
- Test MCP tool calling with real Accord Project MCP server

### Week 7 — Polish & Documentation
- Write comprehensive README with setup, usage, and examples
- Add example templates in `/examples` directory
- Write a short tutorial: "Generate your first template in 30 seconds"
- Code cleanup, type annotations, docstrings

### Week 8 — Testing, Review & Submission
- Write full test suite (unit + integration)
- Peer review with mentors
- Address all feedback
- Final documentation and demo video
- Submit pull request to Accord Project main org

---

## 7. Proof of Concept

A working POC has already been built to validate the approach. It demonstrates:

- ✅ 5-agent CrewAI pipeline in Python
- ✅ 4 tool implementations (with real CLI invocation + static fallback)
- ✅ CLI interface with interactive and single-shot modes
- ✅ Multi-provider LLM support (OpenAI, Anthropic, Google)
- ✅ Real Accord Project output structure (model/, text/, package.json, README)

**Repository:** https://github.com/ANKIEMUNKIE/accord-gsoc-poc

**POC Output Example — Input:** `"Non-disclosure agreement, 2 years confidentiality, governed by NY law"`

Generated `model/model.cto`:
```concerto
namespace org.accordproject.nda@1.0.0

import org.accordproject.contract.Contract 
  from https://models.accordproject.org/accordproject/contract.cto

concept NDAContract extends Contract {
  o String disclosingPartyName
  o String receivingPartyName
  o DateTime effectiveDate
  o Integer confidentialityPeriodYears
  o String governingLaw
}
```

Generated `text/template.tem.md`:
```markdown
# Non-Disclosure Agreement

This Non-Disclosure Agreement is entered into as of {{effectiveDate}} 
between {{disclosingPartyName}} ("Disclosing Party") and 
{{receivingPartyName}} ("Receiving Party").

The Receiving Party shall maintain strict confidentiality for 
{{confidentialityPeriodYears}} years. This Agreement is governed 
by the laws of {{governingLaw}}.
```

---

## 8. Why I Will Succeed

1. **I have already built the POC** — this is not a "I will learn and build" proposal. The architecture is proven.

2. **Python is my strongest language** — the entire core system is Python, which means I can move fast.

3. **I understand the problem deeply** — I studied the Accord Project docs, the Concerto spec, and the existing template examples before writing a single line of code.

4. **The architecture is mentor-ready** — agent personas, tool interfaces, and the CLI are all designed to be clean, extensible, and easy for mentors to review.

5. **I am committed** — This is my primary focus for the summer. I have no conflicting internships or exams during the project period.

---

## 9. Questions for Mentors

1. Should agent definitions be agnostic to CrewAI specifically, or is CrewAI the preferred orchestrator?
2. Is there preference for the MCP tool integration to use the existing APAP MCP server (Project 4) or a new standalone server?
3. Are there specific template types the community would most like to see generated first?
4. What is the preferred way to run the Accord Project CLI tools in a CI/CD test environment?

---

## 10. References

- Accord Project GitHub: https://github.com/accordproject
- Concerto Language Spec: https://concerto.accordproject.org
- TemplateMark Spec: https://docs.accordproject.org/docs/markup-templatemark
- Template Playground: https://templateplay.accordproject.org
- CrewAI Docs: https://docs.crewai.com
- My POC Repository: https://github.com/ANKIEMUNKIE/accord-gsoc-poc
