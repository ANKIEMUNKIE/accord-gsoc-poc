"""
agents.py - Specialist Agent definitions for Accord Project Template Generation

Each agent has a specific role, goal, and set of tools. The agents collaborate
in a sequential pipeline to produce a valid, complete Accord Project template.
"""

from crewai import Agent
from tools import (
    validate_concerto_model,
    validate_templatemark,
    fetch_accord_examples,
    save_template_files
)


def get_llm(model: str = "groq/llama-3.3-70b-versatile"):
    """Returns a configured LLM instance. Supports multiple model providers."""
    from crewai import LLM

    model_map = {
        # Groq (FREE - recommended for POC)
        "groq":                "groq/llama-3.3-70b-versatile",
        "groq/llama-3.3-70b-versatile": "groq/llama-3.3-70b-versatile",
        "groq/llama3-8b-8192": "groq/llama3-8b-8192",
        # OpenAI
        "gpt-4o":              "openai/gpt-4o",
        "gpt-4o-mini":         "openai/gpt-4o-mini",
        # Anthropic
        "claude-3-5-sonnet":   "anthropic/claude-3-5-sonnet-20241022",
        # Google
        "gemini-1.5-pro":      "google/gemini-1.5-pro",
    }
    return LLM(model=model_map.get(model, model), temperature=0.2)


def create_requirements_analyst(llm) -> Agent:
    """
    Agent 1: Requirements Analyst
    
    Parses user's natural language input and extracts structured requirements
    needed by downstream agents (model fields, parties, clauses, jurisdiction, etc.)
    """
    return Agent(
        role="Legal Template Requirements Analyst",
        goal=(
            "Analyze the user's natural language template requirements and extract "
            "a precise, structured specification: contract type, parties involved, "
            "key clauses, data fields needed, jurisdiction, and any special conditions."
        ),
        backstory=(
            "You are an experienced legal analyst with deep knowledge of contract law "
            "and the Accord Project ecosystem. You excel at translating vague business "
            "requirements into precise technical specifications that engineers can use. "
            "You always fetch relevant examples to anchor your analysis in real patterns."
        ),
        tools=[fetch_accord_examples],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


def create_concerto_modeler(llm) -> Agent:
    """
    Agent 2: Concerto Data Modeler
    
    Generates a valid Concerto (.cto) data model based on the structured
    requirements from the Requirements Analyst. Validates the model before
    passing it downstream.
    """
    return Agent(
        role="Concerto Data Model Engineer",
        goal=(
            "Generate a syntactically correct and semantically complete Concerto "
            "data model (.cto file) that captures all data fields, types, and "
            "relationships required by the template. Validate the model before output."
        ),
        backstory=(
            "You are a Concerto modeling expert who understands the full Accord Project "
            "type system: concepts, assets, participants, transactions, enumerations, "
            "relationships, decorators, and imports. You always produce well-namespaced "
            "models with proper inheritance from accordproject base types. "
            "You never output a model without running validation first."
        ),
        tools=[validate_concerto_model, fetch_accord_examples],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


def create_templatemark_author(llm) -> Agent:
    """
    Agent 3: TemplateMark Author
    
    Writes the TemplateMark (.tem.md) template text using Markdown + Handlebars
    syntax, referencing the fields defined in the Concerto model. Validates
    the template against the model before output.
    """
    return Agent(
        role="TemplateMark Legal Writer",
        goal=(
            "Write a complete, professional TemplateMark template (.tem.md) that "
            "uses Handlebars variable syntax ({{fieldName}}) to reference the Concerto "
            "model fields. The template must be legally coherent, well-structured, "
            "and pass cross-reference validation against the Concerto model."
        ),
        backstory=(
            "You are a legal document drafter who specializes in the Accord Project "
            "TemplateMark format. You understand how to use {{variables}}, "
            "{{#if conditions}}, {{#ulist arrays}}, {{#olist ordered}}, and "
            "{{#with object}} blocks. You always produce templates that are both "
            "legally sound and correctly bound to their Concerto data model. "
            "You validate your output before delivering it."
        ),
        tools=[validate_templatemark, fetch_accord_examples],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


def create_package_composer(llm) -> Agent:
    """
    Agent 4: Package Composer
    
    Assembles the final Accord Project template package: generates package.json,
    README, and saves all files to disk in the correct folder structure.
    """
    return Agent(
        role="Accord Project Template Package Composer",
        goal=(
            "Compose the final Accord Project template package by generating a valid "
            "package.json with correct metadata, a clear README.md explaining the "
            "template, and saving all artifacts to disk in the standard Accord Project "
            "directory structure: /model/ for .cto files, /text/ for .tem.md files."
        ),
        backstory=(
            "You are an Accord Project ecosystem expert who knows exactly how to package "
            "templates for publication and use. You ensure every template has proper "
            "metadata (name, version, description, author, license, accordproject config), "
            "clear documentation, and a well-organized file structure that follows "
            "Accord Project conventions. You always call the save tool to persist files."
        ),
        tools=[save_template_files],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


def create_qa_validator(llm) -> Agent:
    """
    Agent 5: QA Validator (Orchestrator-level review)
    
    Reviews the complete template package for correctness, completeness,
    and Accord Project best practices. Reports any issues with remediation hints.
    """
    return Agent(
        role="Accord Project Template Quality Assurance Engineer",
        goal=(
            "Perform a final quality review of the complete generated Accord Project "
            "template. Check that the Concerto model and TemplateMark template are "
            "consistent, validate both artifacts, and produce a QA report listing "
            "any issues found along with specific remediation suggestions."
        ),
        backstory=(
            "You are a senior Accord Project engineer who reviews template submissions "
            "for the Accord Project template library. You have a keen eye for subtle "
            "issues: unused model fields, missing required clauses, incorrect Handlebars "
            "syntax, namespace mismatches, and non-standard patterns. Your QA reports "
            "are thorough and actionable."
        ),
        tools=[validate_concerto_model, validate_templatemark],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
