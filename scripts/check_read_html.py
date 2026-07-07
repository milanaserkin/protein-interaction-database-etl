import pandas as pd
import random

# 1. Load your saved CSV
csv_file = "Table_Docking_Benchmark_5.5.csv"
print(f"Loading {csv_file}...")
csv_df = pd.read_csv(csv_file)

# 2. Fetch the live HTML data again
url = "https://zlab.wenglab.org/benchmark/"
print(f"Fetching live data from {url}...")
tables = pd.read_html(url, match="Complex")

# 3. Clean the live HTML exactly the same way so we can compare apples-to-apples
html_df = tables[0].dropna(axis=1, how='all')
html_df.columns = [
    'info_link', 'complex_id', 'complex_type', 'pdb_1', 'protein_1', 'hetatms_1', 
    'pdb_2', 'protein_2', 'hetatms_2', 'rmsd', 'isa', 'multimer'
]
html_df = html_df.drop('info_link', axis=1)
html_df = html_df[html_df['complex_type'].astype(str).str.len() == 2]

# Reset indexes to make sure the row numbers don't cause false alarms
csv_df = csv_df.reset_index(drop=True)
html_df = html_df.reset_index(drop=True)

# --- STATS CHECK ---
print("\n--- OVERALL STATS CHECK ---")
print(f"CSV Total Rows: {len(csv_df)} | HTML Total Rows: {len(html_df)}")
print(f"CSV Total Columns: {len(csv_df.columns)} | HTML Total Columns: {len(html_df.columns)}")

if len(csv_df) == len(html_df) and len(csv_df.columns) == len(html_df.columns):
    print(" Table dimensions match perfectly!")
else:
    print(" Warning: Table dimensions do not match.")

# --- RANDOM 20 ROWS CHECK ---
print("\n--- RANDOM 20 ROWS CHECK ---")
sample_ids = random.sample(list(csv_df['complex_id']), 20)

all_matched = True

for cid in sample_ids:
    # Grab the specific row from both dataframes
    csv_row = csv_df[csv_df['complex_id'] == cid].iloc[0]
    html_row = html_df[html_df['complex_id'] == cid].iloc[0]
    
    row_is_perfect = True
    
    # Check column by column
    for col in csv_df.columns:
        # Convert both to strings and strip away invisible whitespace
        csv_val = str(csv_row[col]).strip()
        html_val = str(html_row[col]).strip()
        
        # In Pandas, empty cells might become 'nan' strings. Let's make them uniform.
        if csv_val.lower() == 'nan': csv_val = 'BLANK'
        if html_val.lower() == 'nan': html_val = 'BLANK'
        
        if csv_val != html_val:
            if row_is_perfect: 
                print(f" Complex {cid}: MISMATCH FOUND!")
                row_is_perfect = False
                all_matched = False
            # Print exactly what the difference is!
            print(f"    - Column '{col}' -> CSV has: '{csv_val}' | HTML has: '{html_val}'")
            
    if row_is_perfect:
        print(f"Complex {cid}: 100% match!")

# Final Verdict
if all_matched:
    print("\n ALL CLEAR! All 20 random rows matched perfectly after handling types and whitespace.")
else:
    print("\n Still seeing mismatches? Look at the specific columns above to see why.")
