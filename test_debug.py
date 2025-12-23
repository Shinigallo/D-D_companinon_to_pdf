import json
import sys
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter

# Test veloce
print("="*50)
print("TEST DEBUG")
print("="*50)

# Controlla directory
input_dir = Path("input")
output_dir = Path("output")
template_pdf = Path("5E_CharacterSheet_Fillable.pdf")

print(f"\n1. Directory input esiste? {input_dir.exists()}")
print(f"2. Directory output esiste? {output_dir.exists()}")
print(f"3. Template PDF esiste? {template_pdf.exists()}")

# Crea output se non esiste
output_dir.mkdir(exist_ok=True)
print(f"4. Directory output creata/verificata")

# Lista file .cah
cah_files = list(input_dir.glob("*.cah"))
print(f"\n5. File .cah trovati: {len(cah_files)}")
for f in cah_files:
    print(f"   - {f.name}")

# Prova a leggere un file
if cah_files:
    test_file = cah_files[0]
    print(f"\n6. Test lettura {test_file.name}...")
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"   ✓ File JSON letto correttamente")
        print(f"   Nome personaggio: {data.get('name', 'N/A')}")
    except Exception as e:
        print(f"   ✗ Errore: {e}")

# Prova a leggere il PDF template
print(f"\n7. Test lettura PDF template...")
try:
    reader = PdfReader(template_pdf)
    print(f"   ✓ PDF letto correttamente")
    print(f"   Numero pagine: {len(reader.pages)}")
    
    # Prova a vedere i campi della prima pagina
    if reader.pages[0].get("/Annots"):
        print(f"   ✓ La prima pagina ha campi form")
    else:
        print(f"   ⚠ La prima pagina NON ha campi form")
        
except Exception as e:
    print(f"   ✗ Errore: {e}")

# Prova a creare un PDF di test
print(f"\n8. Test scrittura PDF...")
try:
    output_test = output_dir / "test_output.pdf"
    reader = PdfReader(template_pdf)
    writer = PdfWriter()
    
    for page in reader.pages:
        writer.add_page(page)
    
    # Prova a compilare un campo semplice
    test_data = {'CharacterName': 'TEST'}
    
    for i, page in enumerate(writer.pages):
        try:
            writer.update_page_form_field_values(page, test_data)
        except Exception as e:
            print(f"   ⚠ Pagina {i+1}: {e}")
    
    with open(output_test, 'wb') as f:
        writer.write(f)
    
    print(f"   ✓ PDF di test creato: {output_test}")
    print(f"   ✓ File esiste? {output_test.exists()}")
    print(f"   ✓ Dimensione: {output_test.stat().st_size} bytes")
    
except Exception as e:
    print(f"   ✗ Errore: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("TEST COMPLETATO")
print("="*50)
