import pandas as pd
import os
import re

FOLDER = r"C:\Users\Marius\Desktop\NorthData everywhere\BW"
OUTPUT = r"C:\Users\Marius\Desktop\NorthData everywhere\BW_Targets.csv"

def get_gf_names(val):
    if pd.isna(val) or str(val).strip() == "":
        return []
    names = re.split(r'[;,]', str(val))
    result = []
    for n in names:
        n = re.sub(r'\b(Dr\.?|Prof\.?|Dipl\.?-?Ing\.?|MBA)\b', '', n, flags=re.IGNORECASE).strip()
        if len(n) > 3:
            result.append(n)
    return result

results = []

for filename in os.listdir(FOLDER):
    if not (filename.endswith(".csv") or filename.endswith(".csv.csv")):
        continue
    
    filepath = os.path.join(FOLDER, filename)
    print(f"Procesez: {filename}")
    
    df = None
    for enc in ["utf-8", "latin-1", "cp1252"]:
        for sep in [";", ",", "\t"]:
            try:
                df = pd.read_csv(filepath, encoding=enc, sep=sep, 
                                 low_memory=False, on_bad_lines='skip')
                if len(df.columns) >= 5:
                    break
            except Exception:
                continue
        if df is not None and len(df.columns) >= 5:
            break
    
    if df is None or len(df.columns) < 5:
        print(f"  ⚠ Nu pot citi: {filename}")
        continue
    
    # Debug: afișează coloanele
    print(f"  Coloane: {list(df.columns[:8])}")
    
    # Găsește coloanele
    col_name = None
    col_ort = None
    col_gf = None
    col_branche = None
    
    for col in df.columns:
        col_lower = col.lower()
        if 'name' in col_lower and col_name is None:
            col_name = col
        if 'ort' in col_lower and col_ort is None:
            col_ort = col
        if ('vertreter' in col_lower or 'geschäftsführer' in col_lower or 
            'ges.' in col_lower) and col_gf is None:
            col_gf = col
        if ('branche' in col_lower or 'wz' in col_lower) and col_branche is None:
            col_branche = col
    
    print(f"  GF col: {col_gf}, Branche col: {col_branche}")
    
    if not col_gf:
        print(f"  ⚠ Coloana GF negăsită — coloane disponibile: {list(df.columns)}")
        continue
    
    branche_din_fisier = filename.replace(".csv.csv", "").replace(".csv", "")
    
    for _, row in df.iterrows():
        firma = str(row[col_name]).strip() if col_name else ""
        ort = str(row[col_ort]).strip() if col_ort else ""
        branche = str(row[col_branche]).strip() if col_branche else branche_din_fisier
        gf_names = get_gf_names(row[col_gf])
        
        for gf in gf_names:
            results.append({
                "GF_Name": gf,
                "Firma": firma,
                "Ort": ort,
                "Branche": branche,
                "LinkedIn_Suche": f"{gf} {firma}",
            })

if results:
    df_out = pd.DataFrame(results).drop_duplicates(subset=["GF_Name", "Firma"])
    df_out.to_csv(OUTPUT, index=False, sep=";", encoding="utf-8-sig")
    print(f"\n✓ Done: {len(df_out)} persoane → {OUTPUT}")
    print(df_out.head(3).to_string())
else:
    print("⚠ Niciun rezultat.")
