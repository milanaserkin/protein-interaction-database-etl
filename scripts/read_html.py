import pandas as pd

url = "https://zlab.wenglab.org/benchmark/"
print("Fetching and cleaning the dataset...")

# 1. Grab the table
tables = pd.read_html(url, match="Complex")
df = tables[0]

# 2. Drop any completely empty ghost columns
df = df.dropna(axis=1, how='all')

# 3. Name all exactly 12 columns so Pandas doesn't crash
df.columns = [
    'info_link', 'complex_id', 'complex_type', 'pdb_1', 'protein_1', 'hetatms_1', 
    'pdb_2', 'protein_2', 'hetatms_2', 'rmsd', 'isa', 'multimer'
]

# 4. Drop the useless 'info_link' column
df = df.drop('info_link', axis=1)

# 5. Filter out the junk rows! 
# The real data has a 2-letter complex type (like 'AA' or 'EI').
# This one line automatically removes the header row, the "Rigid-body (162)" row, and the footnotes!
df = df[df['complex_type'].astype(str).str.len() == 2]

# 6. Save the perfectly clean data
df.to_csv("Table_Docking_Benchmark_5.5.csv", index=False)

print(f"Success! Cleaned and saved {len(df)} valid protein complexes.")

