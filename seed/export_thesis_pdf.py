"""
Word COM Field Updater and PDF Exporter
Automates Microsoft Word 2016/365 to:
1. Open the 16K graduation thesis docx document
2. Update all fields and Table of Contents with exact page numbers
3. Save the finalized Word .docx
4. Export the print-ready .pdf version
"""

import os
import sys
import time

def export_pdf():
    docx_path = os.path.abspath("docs/graduation_thesis_wuhu_university.docx")
    pdf_path = os.path.abspath("docs/graduation_thesis_wuhu_university.pdf")

    if not os.path.exists(docx_path):
        print(f"Error: {docx_path} does not exist!")
        sys.exit(1)

    print(f"Opening Word to process: {docx_path}")
    import win32com.client
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0

    try:
        doc = word.Documents.Open(docx_path)
        print("Document opened successfully.")

        # Update all fields in document body, headers, footers
        print("Updating document fields...")
        try:
            doc.Fields.Update()
        except Exception as e:
            print("Note on doc.Fields.Update():", e)

        # Update Table of Contents specifically
        try:
            if doc.TablesOfContents.Count > 0:
                print(f"Updating {doc.TablesOfContents.Count} Table(s) of Contents...")
                for toc in doc.TablesOfContents:
                    toc.Update()
        except Exception as e:
            print("Note on Table of Contents update:", e)

        # Save the updated docx with refreshed fields
        doc.Save()
        print("Document saved with updated fields.")

        # Export as PDF (17 = wdFormatPDF)
        print(f"Exporting to PDF: {pdf_path}")
        doc.SaveAs(pdf_path, FileFormat=17)
        doc.Close(False)

        if os.path.exists(pdf_path):
            print(f"PDF successfully exported! Size: {os.path.getsize(pdf_path)} bytes")
        else:
            print("Warning: PDF file was not created.")
    except Exception as e:
        print(f"Error during Word automation: {e}")
        raise e
    finally:
        word.Quit()
        print("Word application terminated cleanly.")

if __name__ == "__main__":
    export_pdf()
