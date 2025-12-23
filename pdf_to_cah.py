import sys
import json
import re
from pathlib import Path
from PyPDF2 import PdfReader

def parse_pdf_to_cah(pdf_path, output_path):
    if not Path(pdf_path).exists():
        print(f"Error: File {pdf_path} not found.")
        return

    reader = PdfReader(pdf_path)
    fields = reader.get_fields()
    
    if not fields:
        print("Error: No form fields found. This PDF might be flattened or not a form.")
        return

    # Helper to get value safely
    def get_val(key, default=""):
        f = fields.get(key, {})
        if f and '/V' in f:
            val = f['/V']
            if val == '/Yes': return True
            if val == '/On': return True
            if val == '/Off': return False
            if isinstance(val, str) and val.startswith('/'): return val[1:] # e.g. /Choice
            return val
        return default

    # Initialize basic CAH structure
    cah_data = {
        "name": get_val("CharacterName"),
        "player": get_val("PlayerName"),
        "xp": int(get_val("XP", 0)) if get_val("XP", "0").isdigit() else 0,
        "hp": int(get_val("HPMax", 0)) if get_val("HPMax", "0").isdigit() else 0,
        "baseAc": int(get_val("AC", 10)) if get_val("AC", "10").isdigit() else 10,
        "alignmentName": get_val("Alignment").replace(" ", "_").upper(),
        "background": {
            "backgroundId": get_val("Background").replace(" ", "_").lower(),
            # Defaults
            "name": get_val("Background")
        },
        "race": {
            "raceId": get_val("Race ").replace(" ", "_").lower(), # Note space in field name 'Race '
            "speed": {
                "normal": int(get_val("Speed", "30").split()[0]) if get_val("Speed") else 30
            }
        },
        "jobs": [],
        "skills": [],
        "spells": [] 
    }

    # Parse Class and Level
    class_level_str = get_val("ClassLevel")
    if class_level_str:
        parts = class_level_str.split()
        level = 1
        job_name = "class"
        
        # Try to find the number
        for part in parts:
            if part.isdigit():
                level = int(part)
                break
        
        # Everything else is the name
        job_name = " ".join([p for p in parts if not p.isdigit()])
        
        cah_data["jobs"].append({
            "jobId": job_name.lower(),
            "level": level
        })

    # Stats and Saves
    stats_map = {
        "strength": {"score": "STR", "save_check": "Check Box 11"},
        "dexterity": {"score": "DEX", "save_check": "Check Box 18"},
        "constitution": {"score": "CON", "save_check": "Check Box 19"},
        "intelligence": {"score": "INT", "save_check": "Check Box 20"},
        "wisdom": {"score": "WIS", "save_check": "Check Box 21"},
        "charisma": {"score": "CHA", "save_check": "Check Box 22"}
    }

    for stat_key, map_data in stats_map.items():
        score_val = get_val(map_data["score"], "10")
        score = int(score_val) if score_val.isdigit() else 10
        save = get_val(map_data["save_check"]) == True
        
        cah_data[stat_key] = {
            "score": score,
            "save": save,
            "modifier": (score - 10) // 2
        }

    # Skills
    # Map Checkbox Field Name -> JSON Type Name
    skill_checkboxes = {
        'Check Box 23': 'ACROBATICS',
        'Check Box 24': 'ANIMAL_HANDLING',
        'Check Box 25': 'ARCANA',
        'Check Box 26': 'ATHLETICS',
        'Check Box 27': 'DECEPTION',
        'Check Box 28': 'HISTORY',
        'Check Box 29': 'INSIGHT',
        'Check Box 30': 'INTIMIDATION',
        'Check Box 31': 'INVESTIGATION',
        'Check Box 32': 'MEDICINE',
        'Check Box 33': 'NATURE',
        'Check Box 34': 'PERCEPTION',
        'Check Box 35': 'PERFORMANCE',
        'Check Box 36': 'PERSUASION',
        'Check Box 37': 'RELIGION',
        'Check Box 38': 'SLEIGHT_OF_HAND',
        'Check Box 39': 'STEALTH',
        'Check Box 40': 'SURVIVAL'
    }

    for cb_field, type_name in skill_checkboxes.items():
        if get_val(cb_field) == True:
            cah_data["skills"].append({
                "typeName": type_name,
                "proficiencyName": "FULL"
            })

    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cah_data, f, indent=2)
    
    print(f"Successfully converted {pdf_path} to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_cah.py <input.pdf> [output.cah]")
    else:
        input_pdf = Path(sys.argv[1])
        
        if len(sys.argv) > 2:
            output_cah = Path(sys.argv[2])
        else:
            # Se il PDF è in input/, scrivi il CAH in output/
            if "input" in input_pdf.parts:
                output_dir = Path("output")
                output_dir.mkdir(exist_ok=True)
                output_cah = output_dir / (input_pdf.stem + ".cah")
            else:
                output_cah = Path(input_pdf.stem + ".cah")
        
        parse_pdf_to_cah(input_pdf, output_cah)
