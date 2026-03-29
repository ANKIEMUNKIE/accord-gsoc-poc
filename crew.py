"""
crew.py - CrewAI Crew orchestration for Accord Project Template Generation

Defines the tasks for each agent and wires them into a sequential CrewAI pipeline.
The pipeline: Requirements → Concerto Model → TemplateMark → Package → QA
"""

import os
from crewai import Crew, Task, Process
from agents import (
    get_llm,
    create_requirements_analyst,
    create_concerto_modeler,
    create_templatemark_author,
    create_package_composer,
    create_qa_validator,
)


class TemplateCrew:
    """
    Orchestrates a 5-agent pipeline to generate a complete, validated
    Accord Project template from a plain English requirements description.
    """

    def __init__(self, requirements: str, model: str = "gpt-4o-mini", output_dir: str = "./output"):
        self.requirements = requirements
        self.output_dir = output_dir
        self.llm = get_llm(model)

        # Instantiate all specialist agents
        self.analyst       = create_requirements_analyst(self.llm)
        self.modeler       = create_concerto_modeler(self.llm)
        self.author        = create_templatemark_author(self.llm)
        self.composer      = create_package_composer(self.llm)
        self.qa_validator  = create_qa_validator(self.llm)

    def _create_tasks(self):
        """Define tasks for each agent in sequence. Each task feeds context to the next."""

        task1_analyze = Task(
            description=f"""
            Analyze the following template requirements provided by the user:
            
            ---
            {self.requirements}
            ---
            
            Extract and structure the following information:
            1. Template/Contract type (e.g., NDA, Service Agreement, Late Payment Clause)
            2. All parties involved with their roles
            3. Key legal clauses required
            4. All data fields needed (name, type, description for each)
            5. Jurisdiction / governing law (if mentioned)
            6. Any special conditions or constraints
            7. Whether this is a Contract (full agreement) or a Clause (single provision)
            
            Also fetch a relevant example using the fetch_accord_examples tool to
            understand the expected Accord Project structure for this template type.
            
            Output a clear, structured requirements specification that the downstream
            Concerto modeling agent can use directly.
            """,
            expected_output=(
                "A structured requirements specification including: contract type, parties, "
                "data fields (with types), key clauses, jurisdiction, and reference example notes. "
                "Format it clearly with sections for each component."
            ),
            agent=self.analyst,
        )

        task2_model = Task(
            description=f"""
            Using the structured requirements specification from the Requirements Analyst,
            generate a complete and valid Concerto data model (.cto file).
            
            Requirements:
            - Use a proper namespace: org.accordproject.<templatename>@1.0.0
            - Import the correct base type from Accord Project (Contract or Clause)
            - Define all required fields with correct Concerto types:
              String, Integer, Double, Boolean, DateTime, Long
            - Use enumerations where appropriate (e.g., for status fields)
            - Add relationships (-->) where entities reference other entities
            - Include decorators (@description) for important fields
            - Follow Accord Project naming conventions (PascalCase for types, camelCase for fields)
            
            After generating the model, ALWAYS call validate_concerto_model tool to check it.
            If validation fails, fix the errors and re-validate.
            
            Output ONLY the final validated .cto file content.
            Output directory: {self.output_dir}
            """,
            expected_output=(
                "A complete, valid Concerto .cto file content as a string, prefixed with "
                "namespace declaration, all imports, and type definitions. "
                "Include a note confirming it passed validation."
            ),
            agent=self.modeler,
            context=[task1_analyze],
        )

        task3_template = Task(
            description=f"""
            Using the Concerto model from the previous agent, write a complete
            TemplateMark template file (.tem.md).
            
            Requirements:
            - Use proper Markdown formatting (headers, sections, paragraphs)
            - Reference ALL relevant Concerto model fields using {{{{fieldName}}}} syntax
            - Use TemplateMark blocks where appropriate:
              * {{{{#if condition}}}} ... {{{{/if}}}} for optional clauses
              * {{{{#ulist arrayField}}}}{{{{this}}}}{{{{/ulist}}}} for unordered lists
              * {{{{#olist arrayField}}}}{{{{this}}}}{{{{/olist}}}} for ordered lists
              * {{{{#with objectField}}}} ... {{{{/with}}}} for nested objects
            - The template text must be legally coherent and professionally written
            - Include a clear title, recitals, numbered articles/sections, and signature blocks
            
            After writing the template, call validate_templatemark tool with both the
            template content and the Concerto model content to check for cross-reference errors.
            Fix any issues and re-validate.
            
            Output ONLY the final validated .tem.md file content.
            """,
            expected_output=(
                "A complete, professionally written TemplateMark (.tem.md) template content "
                "with proper Markdown structure and Handlebars variable references. "
                "Include a note confirming it passed cross-reference validation."
            ),
            agent=self.author,
            context=[task1_analyze, task2_model],
        )

        task4_package = Task(
            description=f"""
            Assemble the complete Accord Project template package using the model
            and template content from the previous agents.
            
            You must call the save_template_files tool with:
            1. output_dir: "{self.output_dir}"
            2. model_content: the complete .cto file content from Agent 2
            3. template_content: the complete .tem.md content from Agent 3
            4. package_json_content: Generate a valid package.json with:
               - name: @accordproject/<template-name-from-requirements>
               - version: "1.0.0"
               - description: a clear one-line description
               - keywords: ["accord-project", "template", relevant legal keywords]
               - author: "GSoC 2025 Agentic Workflow"
               - license: "Apache-2.0"
               - accordproject section with templateType, language, runtime
            5. readme_content: Generate a README.md with:
               - Template description
               - Data fields table (field | type | description)
               - Usage instructions
               - Example data (JSON)
            
            Call the save_template_files tool and confirm all files were saved.
            """,
            expected_output=(
                "Confirmation that all template files have been saved to disk with their paths. "
                "Also include the package.json content for reference."
            ),
            agent=self.composer,
            context=[task1_analyze, task2_model, task3_template],
        )

        task5_qa = Task(
            description=f"""
            Perform a final QA review of the complete Accord Project template that was generated.
            
            Review the following from the previous agents' outputs:
            1. The Concerto model (.cto) content
            2. The TemplateMark template (.tem.md) content
            
            Run both validation tools:
            - validate_concerto_model on the .cto content
            - validate_templatemark on the .tem.md content with the .cto model
            
            Then produce a QA Report with:
            ✅ PASSED checks (list each thing that is correct)
            ❌ ISSUES found (describe the problem and exact fix needed)
            📋 SUMMARY: overall quality score (1-10) and recommendation
            
            If there are critical issues, describe exactly how to fix them.
            """,
            expected_output=(
                "A detailed QA Report listing passed checks, any issues found with remediation "
                "steps, and an overall quality score with recommendation. "
                "The report should be actionable and clear."
            ),
            agent=self.qa_validator,
            context=[task2_model, task3_template],
        )

        return [task1_analyze, task2_model, task3_template, task4_package, task5_qa]

    def run(self) -> str:
        """Execute the multi-agent pipeline and return the final QA report."""
        import time
        tasks = self._create_tasks()

        crew = Crew(
            agents=[
                self.analyst,
                self.modeler,
                self.author,
                self.composer,
                self.qa_validator,
            ],
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
            max_rpm=3,
        )

        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = crew.kickoff()
                return str(result)
            except Exception as e:
                error_str = str(e)
                if "rate_limit" in error_str.lower() or "429" in error_str or "ratelimit" in error_str.lower():
                    wait = 60
                    print(f"\n⏳ Rate limit hit. Waiting {wait}s before retry {attempt+1}/{max_retries}...\n")
                    time.sleep(wait)
                else:
                    raise e
        return "Max retries reached. Check ./output — files may already be saved!"