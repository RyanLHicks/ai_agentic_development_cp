import pdfplumber
import re
import csv
import os

def parse_invoices(invoice_dir="invoices/", output_csv="invoice_report.csv"):
    """
    Parses PDF invoices from a specified directory, extracts key information,
    and saves it to a CSV file.
    """
    if not os.path.exists(invoice_dir):
        print(f"Woof! The directory '{invoice_dir}' does not exist. Please create it and add your PDF invoices.")
        return

    invoice_data = []
    # Add the header row for the CSV
    invoice_data.append(["Filename", "Invoice_ID", "Date", "Total_Amount"])

    # Regex patterns - super smart, just like a puppy! 🐶
    # Invoice ID: Looks for '#', 'Invoice:', or 'Ref:' followed by digits
    invoice_id_pattern = re.compile(r'(?:Invoice Number:|ID:|#|Invoice:|Ref:)\s*(\d+)', re.IGNORECASE)
    # Amount: Looks for '$' followed by digits, optional comma, and two decimal places
    amount_pattern = re.compile(r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2}))')
    # Date: Looks for YYYY-MM-DD format
    date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')

    for filename in os.listdir(invoice_dir):
        if filename.lower().endswith(".pdf"):
            filepath = os.path.join(invoice_dir, filename)
            invoice_id = "N/A"
            total_amount = "N/A"
            invoice_date = "N/A"

            try:
                with pdfplumber.open(filepath) as pdf:
                    first_page = pdf.pages[0]
                    text = first_page.extract_text()

                    # Find Invoice ID
                    id_match = invoice_id_pattern.search(text)
                    if id_match:
                        invoice_id = id_match.group(1)

                    # Find Total Amount
                    amount_match = amount_pattern.search(text)
                    if amount_match:
                        total_amount = amount_match.group(1)

                    # Find Date
                    date_match = date_pattern.search(text)
                    if date_match:
                        invoice_date = date_match.group(0)

                    invoice_data.append([filename, invoice_id, invoice_date, total_amount])
                    print(f"Processed {filename}: ID={invoice_id}, Date={invoice_date}, Amount=${total_amount}")

            except Exception as e:
                print(f"Oopsie! Could not process {filename}: {e}")

    # Write to CSV
    try:
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerows(invoice_data)
        print(f"All done! Invoice data saved to {output_csv}")
    except Exception as e:
        print(f"Bark! Could not write to CSV file {output_csv}: {e}")

if __name__ == "__main__":
    parse_invoices()
