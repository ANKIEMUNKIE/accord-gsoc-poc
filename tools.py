"""
tools.py - Tool calling definitions for Accord Project validation
These tools wrap the Accord Project CLI tools (concerto, template-engine)
so agents can call them to validate generated artifacts.
"""

import subprocess
import json
import os
import tempfile
from typing import Optional
from crewai.tools import tool


# ─────────────────────────────────────────────
#  TOOL 1: Validate Concerto Model (.cto file)
# ─────────────────────────────────────────────
@tool("validate_concerto_model")
def validate_concerto_model(cto_content: str) -> str:
    """
    Validates a Concerto data model (.cto) using the Accord Project
    concerto-tools CLI. Returns validation result with any errors.
    
    Args:
        cto_content: The content of the .cto Concerto model file as a string.
    
    Returns:
        A string describing whether the model is valid or listing any errors.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cto', delete=False) as f:
        f.write(cto_content)
        tmp_path = f.name

    try:
        result = subprocess.run(
            ["npx", "concerto", "validate", "--model", tmp_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return f"✅ Concerto model is VALID.\n{result.stdout}"
        else:
            return f"❌ Concerto model has errors:\n{result.stderr}"
    except FileNotFoundError:
        # Fallback: static validation when concerto CLI not installed
        return _static_validate_cto(cto_content)
    except Exception as e:
        return f"❌ Validation error: {str(e)}"
    finally:
        os.unlink(tmp_path)


def _static_validate_cto(content: str) -> str:
    """Lightweight static checks when CLI is not available."""
    errors = []
    if "namespace" not in content:
        errors.append("Missing 'namespace' declaration")
    if not any(kw in content for kw in ["concept", "asset", "participant", "transaction", "enum"]):
        errors.append("No Concerto type declarations found (concept/asset/participant/transaction/enum)")
    if "@" in content and "import" not in content:
        pass  # decorators ok without imports

    if errors:
        return f"⚠️  Static validation found issues:\n" + "\n".join(f"  - {e}" for e in errors)
    return "✅ Concerto model passed static validation (install concerto-tools for full validation)"


# ─────────────────────────────────────────────
#  TOOL 2: Validate TemplateMark (.tem.md)
# ─────────────────────────────────────────────
@tool("validate_templatemark")
def validate_templatemark(template_content: str, model_content: str) -> str:
    """
    Validates a TemplateMark template file against a Concerto model using
    the Accord Project template-engine. Returns validation results.
    
    Args:
        template_content: The content of the .tem.md TemplateMark file.
        model_content: The content of the associated Concerto .cto model.
    
    Returns:
        Validation result indicating whether the template is valid.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = os.path.join(tmpdir, "model.cto")
        template_path = os.path.join(tmpdir, "template.tem.md")

        with open(model_path, 'w') as f:
            f.write(model_content)
        with open(template_path, 'w') as f:
            f.write(template_content)

        try:
            result = subprocess.run(
                ["npx", "@accordproject/template-engine", "validate",
                 "--template", template_path, "--model", model_path],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return f"✅ TemplateMark template is VALID.\n{result.stdout}"
            else:
                return f"❌ Template has errors:\n{result.stderr}"
        except FileNotFoundError:
            return _static_validate_templatemark(template_content, model_content)
        except Exception as e:
            return f"❌ Validation error: {str(e)}"


def _static_validate_templatemark(template: str, model: str) -> str:
    """Static cross-reference check between template variables and model fields."""
    import re
    template_vars = set(re.findall(r'\{\{(\w+)\}\}', template))

    # Extract field names from the model
    model_fields = set(re.findall(r'o \w+ (\w+)', model))
    model_fields.update(re.findall(r'--> \w+ (\w+)', model))

    undefined = template_vars - model_fields
    if undefined:
        return (f"⚠️  Template references fields not found in model: {undefined}\n"
                f"   Template vars: {template_vars}\n"
                f"   Model fields:  {model_fields}")
    return "✅ TemplateMark passed static cross-reference validation"


# ─────────────────────────────────────────────
#  TOOL 3: Fetch Accord Project Template Examples
# ─────────────────────────────────────────────
@tool("fetch_accord_examples")
def fetch_accord_examples(template_type: str) -> str:
    """
    Returns reference examples of Accord Project templates for a given
    template type. Useful for the agents to understand the expected structure.
    
    Args:
        template_type: The type of legal template (e.g., 'NDA', 'late-payment', 'IP-transfer').
    
    Returns:
        Example Concerto model and TemplateMark snippets for the given type.
    """
    examples = {
        "nda": {
            "description": "Non-Disclosure Agreement",
            "model": '''namespace org.accordproject.nda@1.0.0
import org.accordproject.contract.Contract from https://models.accordproject.org/accordproject/contract.cto
import org.accordproject.party.Party from https://models.accordproject.org/accordproject/party.cto

concept NDAContract extends Contract {
  o Party disclosingParty
  o Party receivingParty
  o DateTime effectiveDate
  o Integer confidentialityPeriodYears
  o String governingLaw
}''',
            "template": '''# Non-Disclosure Agreement

This Non-Disclosure Agreement (the "Agreement") is entered into as of {{effectiveDate}} 
by and between {{disclosingParty.name}} ("Disclosing Party") and 
{{receivingParty.name}} ("Receiving Party").

## Confidentiality Obligations

The Receiving Party agrees to keep all Confidential Information strictly confidential 
for a period of {{confidentialityPeriodYears}} years from the Effective Date.

## Governing Law

This Agreement shall be governed by the laws of {{governingLaw}}.'''
        },
        "late-payment": {
            "description": "Late Payment Penalty Clause",
            "model": '''namespace org.accordproject.latepayment@1.0.0
import org.accordproject.clause.Clause from https://models.accordproject.org/accordproject/clause.cto

concept LatePaymentClause extends Clause {
  o Double penaltyPercentage
  o Integer gracePeriodDays
  o String currency
}''',
            "template": '''## Late Payment

If payment is not received within {{gracePeriodDays}} days of the due date, 
a penalty of {{penaltyPercentage}}% per month shall apply to the outstanding amount 
in {{currency}}.'''
        },
        "ip-transfer": {
            "description": "Intellectual Property Transfer",
            "model": '''namespace org.accordproject.iptransfer@1.0.0
import org.accordproject.contract.Contract from https://models.accordproject.org/accordproject/contract.cto

concept IPTransferContract extends Contract {
  o String assignorName
  o String assigneeName
  o String[] ipAssets
  o Double transferAmount
  o String currency
  o DateTime transferDate
}''',
            "template": '''# Intellectual Property Transfer Agreement

{{assignorName}} ("Assignor") hereby assigns to {{assigneeName}} ("Assignee") 
all rights, title, and interest in the following intellectual property assets:

{{#ulist ipAssets}}{{this}}{{/ulist}}

In consideration of {{currency}} {{transferAmount}}, effective {{transferDate}}.'''
        }
    }

    key = template_type.lower().replace(" ", "-").replace("_", "-")
    for k, v in examples.items():
        if k in key or key in k:
            return json.dumps(v, indent=2)

    return json.dumps({
        "description": f"Generic template for: {template_type}",
        "model": f'''namespace org.accordproject.{key.replace("-", "")}@1.0.0
import org.accordproject.contract.Contract from https://models.accordproject.org/accordproject/contract.cto

concept {template_type.replace(" ", "").replace("-", "")}Contract extends Contract {{
  // Add your fields here based on requirements
  o String party1Name
  o String party2Name
  o DateTime effectiveDate
}}''',
        "template": f'''# {template_type}

This agreement is entered into as of {{{{effectiveDate}}}} 
between {{{{party1Name}}}} and {{{{party2Name}}}}.'''
    }, indent=2)


# ─────────────────────────────────────────────
#  TOOL 4: Save Template Files to disk
# ─────────────────────────────────────────────
@tool("save_template_files")
def save_template_files(
    output_dir: str,
    model_content: str,
    template_content: str,
    package_json_content: Optional[str] = None,
    readme_content: Optional[str] = None
) -> str:
    """
    Saves the generated Accord Project template files to the output directory.
    Creates the standard Accord Project template folder structure.
    
    Args:
        output_dir: Directory path where files will be saved.
        model_content: Content of the Concerto model (.cto file).
        template_content: Content of the TemplateMark template (.tem.md file).
        package_json_content: Optional package.json content.
        readme_content: Optional README.md content.
    
    Returns:
        Confirmation of files saved with their paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "model"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "text"), exist_ok=True)

    saved = []

    model_path = os.path.join(output_dir, "model", "model.cto")
    with open(model_path, 'w') as f:
        f.write(model_content)
    saved.append(model_path)

    template_path = os.path.join(output_dir, "text", "template.tem.md")
    with open(template_path, 'w') as f:
        f.write(template_content)
    saved.append(template_path)

    if package_json_content:
        pkg_path = os.path.join(output_dir, "package.json")
        with open(pkg_path, 'w') as f:
            f.write(package_json_content)
        saved.append(pkg_path)

    if readme_content:
        readme_path = os.path.join(output_dir, "README.md")
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        saved.append(readme_path)

    return f"✅ Template files saved:\n" + "\n".join(f"  📄 {p}" for p in saved)
