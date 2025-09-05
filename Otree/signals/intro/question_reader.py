# question_loader.py
from pathlib import Path
import openpyxl

class QuestionSpec(dict):
    """Einfacher Container: {'label': str, 'choices': [[1,'A'],...], 'correct': int}"""
    pass

def load_questions(xlsx_path: str | Path, sheet: str | None = None) -> list[QuestionSpec]:
    """
    Erwartetes Excel-Layout (ab Zeile 2):
      A: Frage-Text (Label)
      B: Position der richtigen Antwort (1..4)
      C: Antwort 1
      D: Antwort 2
      E: Antwort 3
      F: Antwort 4
    """
    xlsx_path = Path(xlsx_path)
    wb = openpyxl.load_workbook(xlsx_path, data_only=True, read_only=True)
    ws = wb[sheet] if sheet else wb.active

    out: list[QuestionSpec] = []
    for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if not row or all(v is None for v in row):
            continue
        label, correct_pos, *opts = row
        opts = list(opts[:4])  # genau 4 Optionen verwenden

        # Basisvalidierung
        if label is None or correct_pos is None or len(opts) != 4 or any(o is None for o in opts):
            raise ValueError(f"Ungültige Zeile {idx}: {row}")
        if not (1 <= int(correct_pos) <= 4):
            raise ValueError(f"Ungültige richtige Position in Zeile {idx}: {correct_pos}")

        choices = [[i + 1, str(opts[i])] for i in range(4)]  # IntegerField-kompatibel
        out.append(QuestionSpec(label=str(label), choices=choices, correct=int(correct_pos)))

    if not out:
        raise ValueError("Keine Fragen gefunden.")
    return out
