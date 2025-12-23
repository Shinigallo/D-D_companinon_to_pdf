import json
import sys
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, BooleanObject, DictionaryObject
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def load_character_data(cah_file):
    """Carica i dati del personaggio dal file .cah (JSON)"""
    with open(cah_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def calculate_modifier(score):
    """Calcola il modificatore da un punteggio di caratteristica"""
    return (score - 10) // 2

def get_proficiency_bonus(level):
    """Calcola il bonus di competenza basato sul livello"""
    return 2 + (level - 1) // 4

def extract_character_info(data):
    """Estrae le informazioni principali dal JSON del personaggio"""
    char_info = {}
    
    # Informazioni base
    char_info['CharacterName'] = data.get('name', '')
    char_info['PlayerName'] = data.get('player', '')
    char_info['Background'] = data.get('background', {}).get('backgroundId', '').replace('_', ' ').title()
    
    # Razza
    race_data = data.get('race', {})
    char_info['Race '] = race_data.get('raceId', '').replace('_', ' ').title()
    subrace = race_data.get('subraceId', '')
    if subrace:
        char_info['Race '] += f" ({subrace.replace('_', ' ').title()})"
    
    # Classi e livello
    jobs = data.get('jobs', [])
    total_level = sum(job.get('level', 0) for job in jobs)
    char_info['ClassLevel'] = f"{jobs[0].get('jobId', '').title()} {total_level}" if jobs else ''
    
    # Allineamento
    alignment = data.get('alignmentName', '').replace('_', ' ').title()
    char_info['Alignment'] = alignment
    
    # XP
    char_info['XP'] = str(data.get('xp', 0))
    
    # Punteggi caratteristica e modificatori
    ability_mapping = {
        'strength': ('STR', 'STRmod'),
        'dexterity': ('DEX', 'DEXmod '),
        'constitution': ('CON', 'CONmod'),
        'intelligence': ('INT', 'INTmod'),
        'wisdom': ('WIS', 'WISmod'),
        'charisma': ('CHA', 'CHamod')
    }
    
    for ability, (score_field, mod_field) in ability_mapping.items():
        ability_data = data.get(ability, {})
        score = ability_data.get('score', 10)
        modifier = calculate_modifier(score)
        
        char_info[score_field] = str(score)
        char_info[mod_field] = f"+{modifier}" if modifier >= 0 else str(modifier)
    
    # HP
    char_info['HPMax'] = str(data.get('hp', 0))
    char_info['HPCurrent'] = str(data.get('hp', 0))
    
    # CA (AC)
    char_info['AC'] = str(data.get('baseAc', 10) + data.get('extraAC', 0))
    
    # Velocità
    speed = data.get('race', {}).get('speed', {}).get('normal', 30)
    char_info['Speed'] = f"{speed} ft."
    
    # Bonus di competenza
    prof_bonus = get_proficiency_bonus(total_level)
    char_info['ProfBonus'] = f"+{prof_bonus}"
    
    # Tiri salvezza
    save_mapping = {
        'strength': 'ST Strength',
        'dexterity': 'ST Dexterity',
        'constitution': 'ST Constitution',
        'intelligence': 'ST Intelligence',
        'wisdom': 'ST Wisdom',
        'charisma': 'ST Charisma'
    }
    
    save_checkbox_mapping = {
        'strength': 'Check Box 11',
        'dexterity': 'Check Box 18',
        'constitution': 'Check Box 19',
        'intelligence': 'Check Box 20',
        'wisdom': 'Check Box 21',
        'charisma': 'Check Box 22'
    }
    
    for ability, save_field in save_mapping.items():
        ability_data = data.get(ability, {})
        has_save = ability_data.get('save', False)
        score = ability_data.get('score', 10)
        modifier = calculate_modifier(score)
        
        if has_save:
            modifier += prof_bonus
            # Mark the checkbox
            if ability in save_checkbox_mapping:
                char_info[save_checkbox_mapping[ability]] = 'Yes'
        
        char_info[save_field] = f"+{modifier}" if modifier >= 0 else str(modifier)
    
    # Abilità
    skills = data.get('skills', [])
    skill_mapping = {
        'ACROBATICS': ('Acrobatics', 'dexterity'),
        'ANIMAL_HANDLING': ('Animal', 'wisdom'),
        'ARCANA': ('Arcana', 'intelligence'),
        'ATHLETICS': ('Athletics', 'strength'),
        'DECEPTION': ('Deception ', 'charisma'),
        'HISTORY': ('History ', 'intelligence'),
        'INSIGHT': ('Insight', 'wisdom'),
        'INTIMIDATION': ('Intimidation', 'charisma'),
        'INVESTIGATION': ('Investigation ', 'intelligence'),
        'MEDICINE': ('Medicine', 'wisdom'),
        'NATURE': ('Nature', 'intelligence'),
        'PERCEPTION': ('Perception ', 'wisdom'),
        'PERFORMANCE': ('Performance', 'charisma'),
        'PERSUASION': ('Persuasion', 'charisma'),
        'RELIGION': ('Religion', 'intelligence'),
        'SLEIGHT_OF_HAND': ('SleightofHand', 'dexterity'),
        'STEALTH': ('Stealth ', 'dexterity'),
        'SURVIVAL': ('Survival', 'wisdom')
    }
    
    skill_checkbox_mapping = {
        'ACROBATICS': 'Check Box 23',
        'ANIMAL_HANDLING': 'Check Box 24',
        'ARCANA': 'Check Box 25',
        'ATHLETICS': 'Check Box 26',
        'DECEPTION': 'Check Box 27',
        'HISTORY': 'Check Box 28',
        'INSIGHT': 'Check Box 29',
        'INTIMIDATION': 'Check Box 30',
        'INVESTIGATION': 'Check Box 31',
        'MEDICINE': 'Check Box 32',
        'NATURE': 'Check Box 33',
        'PERCEPTION': 'Check Box 34',
        'PERFORMANCE': 'Check Box 35',
        'PERSUASION': 'Check Box 36',
        'RELIGION': 'Check Box 37',
        'SLEIGHT_OF_HAND': 'Check Box 38',
        'STEALTH': 'Check Box 39',
        'SURVIVAL': 'Check Box 40'
    }
    
    for skill in skills:
        skill_type = skill.get('typeName', '')
        proficiency = skill.get('proficiencyName', 'NONE')
        
        if skill_type in skill_mapping:
            skill_name, ability = skill_mapping[skill_type]
            ability_score = data.get(ability, {}).get('score', 10)
            modifier = calculate_modifier(ability_score)
            
            if proficiency == 'FULL':
                modifier += prof_bonus
                if skill_type in skill_checkbox_mapping:
                     char_info[skill_checkbox_mapping[skill_type]] = 'Yes'
            elif proficiency == 'EXPERT':
                modifier += prof_bonus * 2
                if skill_type in skill_checkbox_mapping:
                     char_info[skill_checkbox_mapping[skill_type]] = 'Yes'
            
            char_info[skill_name] = f"+{modifier}" if modifier >= 0 else str(modifier)
    
    # Initiativa
    dex_mod = calculate_modifier(data.get('dexterity', {}).get('score', 10))
    char_info['Initiative'] = f"+{dex_mod}" if dex_mod >= 0 else str(dex_mod)
    
    # Percezione passiva
    perception_bonus = 0
    for skill in skills:
        if skill.get('typeName') == 'PERCEPTION':
            wis_score = data.get('wisdom', {}).get('score', 10)
            wis_mod = calculate_modifier(wis_score)
            proficiency = skill.get('proficiencyName', 'NONE')
            
            if proficiency == 'FULL':
                perception_bonus = wis_mod + prof_bonus
            elif proficiency == 'EXPERT':
                perception_bonus = wis_mod + (prof_bonus * 2)
            else:
                perception_bonus = wis_mod
    
    char_info['Passive'] = str(10 + perception_bonus)
    
    # Magie
    spells = data.get('spells', [])
    if spells:
        # Classe incantatore e caratteristica
        spellcaster_class = ''
        spellcasting_ability = ''
        
        for job in jobs:
            job_id = job.get('jobId', '').lower()
            if job_id in ['wizard', 'sorcerer', 'warlock', 'bard', 'cleric', 'druid', 'paladin', 'ranger']:
                spellcaster_class = job.get('jobId', '').title()
                
                # Determina la caratteristica da incantesimo
                if job_id in ['wizard']:
                    spellcasting_ability = 'Intelligence'
                    ability_score = data.get('intelligence', {}).get('score', 10)
                elif job_id in ['sorcerer', 'bard', 'warlock']:
                    spellcasting_ability = 'Charisma'
                    ability_score = data.get('charisma', {}).get('score', 10)
                elif job_id in ['cleric', 'druid', 'paladin', 'ranger']:
                    spellcasting_ability = 'Wisdom'
                    ability_score = data.get('wisdom', {}).get('score', 10)
                break
        
        if spellcasting_ability:
            char_info['Spellcasting Class 2'] = spellcaster_class
            char_info['SpellcastingAbility 2'] = spellcasting_ability
            
            # CD Tiro Salvezza Incantesimi
            spell_mod = calculate_modifier(ability_score)
            spell_save_dc = 8 + prof_bonus + spell_mod
            char_info['SpellSaveDC  2'] = str(spell_save_dc)
            
            # Bonus di attacco con incantesimo
            spell_attack_bonus = prof_bonus + spell_mod
            char_info['SpellAtkBonus 2'] = f"+{spell_attack_bonus}" if spell_attack_bonus >= 0 else str(spell_attack_bonus)
        
        # Slot incantesimi (il PDF usa 19-27 per livelli 1-9)
        spell_slots = data.get('spellSlots', {})
        for level in range(1, 10):
            slot_key = f'Lvl{level}'
            if slot_key in spell_slots:
                slots = spell_slots[slot_key]
                pdf_level = 18 + level  # 19-27
                char_info[f'SlotsTotal {pdf_level}'] = str(slots)
                char_info[f'SlotsRemaining {pdf_level}'] = str(slots)
        
        # Organizza gli incantesimi per livello
        spells_by_level = {}
        for spell in spells:
            level = spell.get('level', 0)
            if level not in spells_by_level:
                spells_by_level[level] = []
            
            spell_info = {
                'name': spell.get('name', ''),
                'prepared': spell.get('prepared', False),
                'ritual': 'ritual' in spell.get('tags', [])
            }
            spells_by_level[level].append(spell_info)
        
        # Trucchetti (Cantrips - livello 0) - Non ci sono campi per cantrips nel PDF standard
        # Gli incantesimi iniziano da livello 1
        
        # Incantesimi di livello 1-9
        # Il PDF usa una numerazione strana: Spells 1014-1022 per livello 1, ecc.
        spell_field_start = {
            1: 1014,
            2: 1023,
            3: 1031,
            4: 1039,
            5: 1047,
            6: 1055,
            7: 1063,
            8: 1071,
            9: 1079
        }
        
        for level in range(1, 10):
            if level in spells_by_level and level in spell_field_start:
                start_num = spell_field_start[level]
                for i, spell in enumerate(spells_by_level[level][:9], 0):  # Max 9 incantesimi per livello
                    spell_name = spell['name']
                    if spell['prepared']:
                        spell_name = "✓ " + spell_name
                    if spell['ritual']:
                        spell_name = spell_name + " (R)"
                    
                    field_num = start_num + i
                    char_info[f'Spells {field_num}'] = spell_name
    
    return char_info

def fill_pdf(template_path, output_path, field_data):
    """Compila il PDF sovrapponendo il testo alle coordinate dei campi"""
    # 1. Crea il PDF con i testi usando ReportLab
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    
    reader = PdfReader(template_path)
    
    print("Generazione overlay testo...")
    
    # Itera su ogni pagina del template per trovare i campi e le loro coordinate
    for page_num, page in enumerate(reader.pages):
        if "/Annots" in page:
            for annot in page["/Annots"]:
                obj = annot.get_object()
                if "/T" in obj:
                    field_name = obj["/T"]
                    
                    if field_name in field_data:
                        text_to_draw = field_data[field_name]
                        
                        # Ottieni coordinate (Rect è [x1, y1, x2, y2])
                        rect = obj.get("/Rect")
                        if rect:
                            x1 = float(rect[0])
                            y1 = float(rect[1])
                            x2 = float(rect[2])
                            y2 = float(rect[3])
                            
                            # Calcola altezza e larghezza
                            width = x2 - x1
                            height = y2 - y1
                            
                            # Stima dimensione font (60% dell'altezza, max 10pt)
                            font_size = min(height * 0.6, 10)
                            
                            # Posiziona il testo
                            if field_name.startswith("Check Box"):
                                # Per i checkbox, disegna un pallino pieno centrato
                                c.setFont("Helvetica", 12)  # Dimensione fissa per il pallino
                                text_width = c.stringWidth("•", "Helvetica", 12)
                                text_x = x1 + (width - text_width) / 2
                                text_y = y1 + (height - 12) / 2 + 2 # Aggiustamento verticale
                                c.drawString(text_x, text_y, "•")
                            else:
                                # Per i campi di testo normali
                                text_x = x1 + 2
                                text_y = y1 + (height - font_size) / 2 + 1
                                c.setFont("Helvetica", font_size)
                                c.drawString(text_x, text_y, text_to_draw)
        
        # Passa alla prossima pagina nel canvas ReportLab
        c.showPage()
    
    c.save()
    packet.seek(0)
    
    # 2. Unisci il PDF originale con l'overlay
    new_pdf = PdfReader(packet)
    writer = PdfWriter()
    
    print("Unione layer...")
    
    # Copia le pagine originali e unisci l'overlay
    for i, page in enumerate(reader.pages):
        if i < len(new_pdf.pages):
            overlay_page = new_pdf.pages[i]
            page.merge_page(overlay_page)
        
        # Opzionale: Rimuovi le annotazioni originali per evitare duplicati/conflitti
        # (Se non le rimuoviamo, il campo vuoto rimane sotto al testo, che va bene)
        # Rimuoviamo i campi form originali per rendere il PDF "non editabile"
        if "/Annots" in page:
             del page["/Annots"]
            
        writer.add_page(page)
    
    # Rimuovi la struttura del form (AcroForm) dal root object se presente
    if "/AcroForm" in writer._root_object:
        del writer._root_object["/AcroForm"]
    
    # Salva il risultato
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)
    
    print(f"✓ File salvato con overlay grafico: {output_path.stat().st_size} bytes")

def main():
    if len(sys.argv) < 2:
        print("Uso: python fill_dnd_sheet.py <file.cah>")
        print("Esempio: python fill_dnd_sheet.py input/Arkan.cah")
        print("\nOppure elabora tutti i file .cah nella cartella input/:")
        print("python fill_dnd_sheet.py --all")
        return
    
    # Template PDF
    template_pdf = Path("5E_CharacterSheet_Fillable.pdf")
    
    if not template_pdf.exists():
        print(f"Errore: Template PDF non trovato: {template_pdf}")
        return
    
    # Directory di input e output
    input_dir = Path("input")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Lista dei file da processare
    files_to_process = []
    
    if sys.argv[1] == "--all":
        # Elabora tutti i file .cah nella cartella input
        if not input_dir.exists():
            print(f"Errore: Cartella {input_dir} non trovata!")
            return
        
        files_to_process = list(input_dir.glob("*.cah"))
        if not files_to_process:
            print(f"Nessun file .cah trovato in {input_dir}")
            return
        
        print(f"Trovati {len(files_to_process)} file .cah da processare\n")
    else:
        # Elabora un singolo file
        cah_file = Path(sys.argv[1])
        
        # Se il path non è assoluto e non esiste, prova nella cartella input
        if not cah_file.is_absolute() and not cah_file.exists():
            cah_file = input_dir / cah_file.name
        
        if not cah_file.exists():
            print(f"Errore: File {cah_file} non trovato!")
            return
        
        files_to_process = [cah_file]
    
    # Processa ogni file
    for cah_file in files_to_process:
        try:
            print(f"{'='*50}")
            print(f"Caricamento personaggio da {cah_file.name}...")
            char_data = load_character_data(cah_file)
            
            print("Estrazione informazioni...")
            char_info = extract_character_info(char_data)
            
            # File di output
            output_file = output_dir / f"{cah_file.stem}_sheet.pdf"
            
            print(f"Compilazione PDF...")
            fill_pdf(template_pdf, output_file, char_info)
            
            print(f"✓ Scheda creata con successo: {output_file}")
            print(f"  Personaggio: {char_info.get('CharacterName', 'N/A')}")
            print(f"  Classe/Livello: {char_info.get('ClassLevel', 'N/A')}")
            print(f"  Razza: {char_info.get('Race ', 'N/A')}")
            
            # Info sugli incantesimi se presenti
            if 'SpellcastingClass' in char_info:
                print(f"  Incantatore: {char_info.get('SpellcastingClass', 'N/A')}")
                print(f"  CD Incantesimi: {char_info.get('SpellSaveDC', 'N/A')}")
            print()
            
        except Exception as e:
            print(f"✗ Errore durante l'elaborazione di {cah_file.name}: {e}")
            print()

if __name__ == "__main__":
    main()
