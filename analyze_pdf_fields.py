import json
from pathlib import Path
from PyPDF2 import PdfReader

# Leggi il PDF template e mostra TUTTI i nomi dei campi
template_pdf = Path("5E_CharacterSheet_Fillable.pdf")

print("="*70)
print("ANALISI CAMPI PDF - D&D 5E Character Sheet")
print("="*70)

try:
    reader = PdfReader(template_pdf)
    print(f"\nNumero totale di pagine: {len(reader.pages)}")
    
    all_fields = []
    
    for page_num, page in enumerate(reader.pages, 1):
        print(f"\n{'='*70}")
        print(f"PAGINA {page_num}")
        print(f"{'='*70}")
        
        if "/Annots" in page:
            annotations = page["/Annots"]
            page_fields = []
            
            for annot in annotations:
                annot_obj = annot.get_object()
                if annot_obj.get("/T"):
                    field_name = annot_obj.get("/T")
                    field_type = annot_obj.get("/FT", "Unknown")
                    field_value = annot_obj.get("/V", "")
                    
                    page_fields.append({
                        'name': field_name,
                        'type': str(field_type),
                        'value': str(field_value)
                    })
            
            if page_fields:
                print(f"\nTrovati {len(page_fields)} campi:")
                for i, field in enumerate(page_fields, 1):
                    print(f"{i:3}. '{field['name']}'")
                    all_fields.append(field['name'])
            else:
                print("Nessun campo trovato")
        else:
            print("Pagina senza campi form")
    
    print(f"\n{'='*70}")
    print(f"TOTALE CAMPI NEL PDF: {len(all_fields)}")
    print(f"{'='*70}")
    
    # Salva tutti i nomi dei campi in un file
    output_file = Path("pdf_fields.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("TUTTI I CAMPI DEL PDF:\n")
        f.write("="*70 + "\n\n")
        for field in sorted(all_fields):
            f.write(f"{field}\n")
    
    print(f"\n✓ Lista completa salvata in: {output_file}")
    
    # Prova a identificare i campi principali
    print(f"\n{'='*70}")
    print("CAMPI PROBABILI PER DATI PRINCIPALI:")
    print(f"{'='*70}")
    
    keywords = {
        'Nome': ['name', 'character', 'char'],
        'Classe': ['class', 'classe'],
        'Livello': ['level', 'lvl', 'lv'],
        'Razza': ['race', 'razza'],
        'Background': ['background'],
        'Allineamento': ['alignment', 'align'],
        'Forza': ['str', 'strength', 'for'],
        'Destrezza': ['dex', 'dexterity', 'des'],
        'Costituzione': ['con', 'constitution', 'cos'],
        'Intelligenza': ['int', 'intelligence'],
        'Saggezza': ['wis', 'wisdom', 'sag'],
        'Carisma': ['cha', 'charisma', 'car'],
        'HP': ['hp', 'hitpoints', 'hit points'],
        'CA': ['ac', 'armor', 'armour'],
        'Velocità': ['speed', 'vel'],
        'Iniziativa': ['init', 'initiative'],
        'Magie': ['spell', 'magic', 'magia']
    }
    
    for category, keys in keywords.items():
        matches = []
        for field in all_fields:
            field_lower = field.lower()
            for key in keys:
                if key in field_lower:
                    matches.append(field)
                    break
        
        if matches:
            print(f"\n{category}:")
            for match in matches[:5]:  # Mostra max 5
                print(f"  - {match}")
    
except Exception as e:
    print(f"✗ Errore: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*70}")
print("ANALISI COMPLETATA")
print(f"{'='*70}")
