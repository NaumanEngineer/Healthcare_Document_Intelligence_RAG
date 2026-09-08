# Document Ingestion Design

## Objective

Convert approved healthcare documents into structured page-level text while preserving source traceability and provenance.

## Initial File Type

The first implementation supports:

- PDF

Additional formats may be introduced later after the PDF ingestion pipeline is validated.

## Initial Parser

The first implementation will use:

`PyMuPDF`

PyMuPDF is selected because it supports:

- page-level PDF access
- machine-readable text extraction
- lightweight implementation
- inspection of extraction results

The first prototype focuses on text-based PDFs.

Scanned-image PDFs requiring OCR are outside the initial implementation scope.

## Ingestion Flow

Raw PDF
→ Open document
→ Iterate pages
→ Extract text
→ Preserve page number
→ Preserve source filename
→ Attach document metadata
→ Return structured page records

## Page-Level Output

Each extracted page should produce a structured record containing at minimum:

- document_id
- page
- text
- source_file

Example:

```python
{
    "document_id": "DOC-001",
    "page": 1,
    "text": "Operational escalation guidance...",
    "source_file": "DOC-001_operational_escalation_policy.pdf"
}
