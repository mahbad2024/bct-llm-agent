from bs4 import BeautifulSoup
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Preformatted
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

# Input and output files
HTML_FILE = "solution_paper.html"
PDF_FILE = "solution_paper_clean.html"

# Read HTML file
with open(HTML_FILE, "r", encoding="utf-8") as f:
    html = f.read()

# Parse HTML
soup = BeautifulSoup(html, "html.parser")

# Create clean PDF
doc = SimpleDocTemplate(
    PDF_FILE,
    pagesize=A4,
    topMargin=36,
    bottomMargin=36,
    leftMargin=40,
    rightMargin=40
)

styles = getSampleStyleSheet()
story = []

# Convert HTML elements
for el in soup.body.find_all(recursive=False):

    if el.name == "h1":
        story.append(Paragraph(el.get_text(strip=True), styles["Title"]))
        story.append(Spacer(1, 12))

    elif el.name == "h2":
        story.append(Paragraph(el.get_text(strip=True), styles["Heading2"]))
        story.append(Spacer(1, 10))

    elif el.name == "h3":
        story.append(Paragraph(el.get_text(strip=True), styles["Heading3"]))
        story.append(Spacer(1, 8))

    elif el.name == "p":
        story.append(Paragraph(el.get_text(" ", strip=True), styles["BodyText"]))
        story.append(Spacer(1, 6))

    elif el.name in ["ul", "ol"]:
        for li in el.find_all("li", recursive=False):
            story.append(
                Paragraph(f"• {li.get_text(' ', strip=True)}", styles["BodyText"])
            )
        story.append(Spacer(1, 6))

    elif el.name == "table":
        data = []

        for tr in el.find_all("tr"):
            row = [
                cell.get_text(" ", strip=True)
                for cell in tr.find_all(["th", "td"])
            ]
            data.append(row)

        table = Table(data)

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ]))

        story.append(table)
        story.append(Spacer(1, 12))

    elif el.name == "pre":
        story.append(Preformatted(el.get_text(), styles["Code"]))
        story.append(Spacer(1, 10))

# Build PDF
doc.build(story)

print(f"Clean PDF created successfully: {PDF_FILE}")