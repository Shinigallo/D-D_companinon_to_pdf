# Compilatore Schede D&D 5E

Applicazione Python per compilare automaticamente schede personaggio PDF di D&D 5E partendo da file .cah.

## Installazione

1. Installa Python 3.8 o superiore
2. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

## Utilizzo

```bash
python fill_dnd_sheet.py input/NomePersonaggio.cah
```

Il PDF compilato verrà salvato nella cartella `output/`.

## Esempio

```bash
python fill_dnd_sheet.py input/Arkan.cah
```

Questo creerà il file `output/Arkan_sheet.pdf`.

## Struttura

- `5E_CharacterSheet_Fillable.pdf` - Template della scheda personaggio
- `input/` - Cartella con i file .cah dei personaggi
- `output/` - Cartella dove vengono salvate le schede compilate
- `fill_dnd_sheet.py` - Script principale

## Dati compilati

L'applicazione compila automaticamente:
- Nome, classe, livello, razza, allineamento
- Punteggi caratteristica e modificatori
- Tiri salvezza
- Abilità con bonus di competenza
- Punti ferita, CA, velocità
- Bonus di competenza
- Iniziativa e percezione passiva

# D-D_companinon_to_pdf
