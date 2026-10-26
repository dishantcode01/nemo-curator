from pypdf import PdfReader
from pathlib import Path

input_file = Path("data/raw/RBI_KYC.pdf")
output_file = Path("data/raw/kyc_raw.txt")

reader = PdfReader(input_file)

text = ""

for page in reader.pages:
    page_text = page.extract_text()
    if page_text:
        text += page_text + "\n"

output_file.write_text(text, encoding="utf-8")

print(f"Pages extracted : {len(reader.pages)}")
print(f"Characters      : {len(text):,}")
print(f"Words           : {len(text.split()):,}")
print(f"Output          : {output_file}")
