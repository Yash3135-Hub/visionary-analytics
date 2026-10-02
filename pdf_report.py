import os
import tempfile
from datetime import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from utils import clean_text_for_pdf

def generate_pdf_report(filename, total_sales, average_sales, max_sales, total_records,
                         top_category_col=None, top_category=None, top_value=None,
                         heatmap_img=None, ai_analysis=None):

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(255, 75, 75)
    pdf.cell(0, 12, "Visionary Analytics", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(90, 90, 90)
    pdf.cell(0, 8, "AI-Powered Analytics Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 8, "Generated on: " + datetime.now().strftime("%d-%m-%Y %H:%M"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 8, "Source File: " + clean_text_for_pdf(filename), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(6)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "KPI Summary", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "Total Sales: {:,.0f}".format(total_sales), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 8, "Average Sales: {:,.2f}".format(average_sales), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 8, "Highest Value: {:,.0f}".format(max_sales), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 8, "Total Records: {:,}".format(total_records), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    if top_category is not None:
        pdf.ln(2)
        pdf.cell(0, 8, "Top Performing {}: {} ({:,.0f})".format(
            clean_text_for_pdf(str(top_category_col)),
            clean_text_for_pdf(str(top_category)),
            top_value
        ), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(4)

    if heatmap_img:
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 10, "Correlation Heatmap", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(heatmap_img)
            tmp_path = tmp.name

        pdf.image(tmp_path, w=170)
        os.remove(tmp_path)
        pdf.ln(4)

    if ai_analysis:
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 10, "AI Sales Analysis (Gemini)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, clean_text_for_pdf(ai_analysis))
    else:
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(150, 150, 150)
        pdf.multi_cell(0, 6, "AI analysis was not generated for this session.")

    return bytes(pdf.output())