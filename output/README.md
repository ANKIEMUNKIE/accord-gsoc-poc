# Non-Disclosure Agreement

This is a template for a Non-Disclosure Agreement (NDA) between two companies.

## Data Fields
| Field | Type | Description |
| --- | --- | --- |
| Company A Name | string | The name of the disclosing company. |
| Company B Name | string | The name of the receiving company. |
| Confidential Information | string | A description of the confidential information being shared. |
| Term | integer | The duration of the confidentiality obligation, specified as 2 years. |
| Effective Date | date | The date when the agreement becomes effective. |
| Termination Date | date | The date when the agreement terminates, calculated based on the effective date and term. |

## Usage
To use this template, simply fill in the required data fields and execute the contract.

## Example Data
{
  "companyA": {
    "name": "Company A"
  },
  "companyB": {
    "name": "Company B"
  },
  "confidentialInformation": "Confidential information",
  "term": 2,
  "effectiveDate": "2024-01-01",
  "terminationDate": "2026-01-01"
}