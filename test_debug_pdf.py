from PyPDF2 import PdfReader
import os

def inspect_pdf(file_path):
    print(f"CWD: {os.getcwd()}")
    if not os.path.exists(file_path):
        print(f"Errore: File non trovato: {file_path}")
        return

    print(f"Ispeziono: {file_path}")
    reader = PdfReader(file_path)
    
    # Check AcroForm
    if "/AcroForm" in reader.trailer["/Root"]:
        acroform = reader.trailer["/Root"]["/AcroForm"]
        print(f"AcroForm presente: {acroform.keys()}")
        if "/NeedAppearances" in acroform:
            print(f"NeedAppearances: {acroform['/NeedAppearances']}")
        else:
            print("NeedAppearances: ASSENTE")
    else:
        print("AcroForm: ASSENTE (Nessun modulo trovato nel root)")

    # Check first page fields
    if "/Annots" in reader.pages[0]:
        print("\nCampi trovati nella pagina 1 (primi 5):")
        annots = reader.pages[0]["/Annots"]
        count = 0
        for annot in annots:
            obj = annot.get_object()
            if "/T" in obj:
                name = obj["/T"]
                value = obj.get("/V", "N/A")
                rect = obj.get("/Rect", "No Rect")
                print(f"  Campo: {name}")
                print(f"    Valore: {value}")
                print(f"    Rect: {rect}")
                count += 1
                if count >= 5: break
    else:
        print("\nNessuna annotazione/campo trovato nella pagina 1")

inspect_pdf("output/Arkan_sheet.pdf")
