"""
PDF generation service using WeasyPrint.
"""
import logging
from io import BytesIO
import markdown

logger = logging.getLogger(__name__)


CORNELL_CSS = """
@page {
    size: A4;
    margin: 2cm 1.5cm;
    
    @top-center {
        content: "Cornell Notes";
        font-size: 10pt;
        color: #666;
    }
    
    @bottom-center {
        content: counter(page);
        font-size: 10pt;
    }
}

body {
    font-family: 'Georgia', 'Times New Roman', serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}

h1 {
    font-size: 18pt;
    color: #1a1a1a;
    border-bottom: 2px solid #333;
    padding-bottom: 0.5em;
    margin-top: 0;
    page-break-after: avoid;
}

h2 {
    font-size: 14pt;
    color: #2a2a2a;
    margin-top: 1.5em;
    border-left: 4px solid #4a90d9;
    padding-left: 0.5em;
    page-break-after: avoid;
}

h3 {
    font-size: 12pt;
    color: #3a3a3a;
    margin-top: 1em;
    page-break-after: avoid;
}

h4 {
    font-size: 11pt;
    color: #4a4a4a;
    font-style: italic;
}

p {
    margin: 0.5em 0;
    text-align: justify;
}

ul, ol {
    margin: 0.5em 0;
    padding-left: 1.5em;
}

li {
    margin: 0.25em 0;
}

code {
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 10pt;
    background-color: #f5f5f5;
    padding: 0.1em 0.3em;
    border-radius: 3px;
}

pre {
    background-color: #f5f5f5;
    padding: 1em;
    border-radius: 5px;
    overflow-x: auto;
    font-size: 9pt;
    page-break-inside: avoid;
}

pre code {
    background: none;
    padding: 0;
}

blockquote {
    border-left: 3px solid #ccc;
    margin: 1em 0;
    padding-left: 1em;
    color: #666;
    font-style: italic;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
    page-break-inside: avoid;
}

th, td {
    border: 1px solid #ddd;
    padding: 0.5em;
    text-align: left;
}

th {
    background-color: #f5f5f5;
    font-weight: bold;
}

hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 1.5em 0;
}

strong {
    color: #1a1a1a;
}

/* Cornell-specific sections */
.questions-cues {
    background-color: #fffbeb;
    padding: 1em;
    border-radius: 5px;
    margin: 1em 0;
}

.summary {
    background-color: #f0f9ff;
    padding: 1em;
    border-radius: 5px;
    margin: 1em 0;
}

.ad-libitum {
    background-color: #f0fdf4;
    padding: 1em;
    border-radius: 5px;
    margin: 1em 0;
}
"""


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cornell Notes</title>
    <style>
{css}
    </style>
</head>
<body>
{content}
</body>
</html>
"""


class PDFService:
    """Handles PDF generation from markdown using WeasyPrint."""
    
    def generate_pdf(self, markdown_content: str) -> bytes:
        """
        Convert markdown content to PDF.
        
        Args:
            markdown_content: Markdown string
            
        Returns:
            PDF bytes
        """
        from weasyprint import HTML, CSS
        
        # Convert markdown to HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=['tables', 'fenced_code', 'codehilite']
        )
        
        # Build full HTML document
        full_html = HTML_TEMPLATE.format(
            css=CORNELL_CSS,
            content=html_content
        )
        
        # Generate PDF
        pdf_buffer = BytesIO()
        HTML(string=full_html).write_pdf(
            pdf_buffer,
            stylesheets=[CSS(string=CORNELL_CSS)]
        )
        
        return pdf_buffer.getvalue()
    
    def generate_combined_pdf(self, notes: list) -> bytes:
        """
        Generate a single PDF from multiple notes.
        
        Args:
            notes: List of markdown content strings
            
        Returns:
            PDF bytes
        """
        # Combine all notes with page breaks
        combined = "\n\n---\n\n".join(notes)
        return self.generate_pdf(combined)


# Singleton instance
pdf_service = PDFService()
