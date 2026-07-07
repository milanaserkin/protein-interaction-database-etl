import pandas as pd

# 1. Load both datasets
seq_df = pd.read_csv("pdb_sequences.csv")
# Make sure this matches the exact name of your Job 1 CSV!
benchmark_df = pd.read_csv("Table_Docking_Benchmark_5.5.csv") 

print(f"Total sequences loaded: {len(seq_df)}")

# 2. Parse the filenames based on the README rules
def parse_filename(filename):
    if len(filename) >= 12 and filename.endswith(".pdb"):
        return pd.Series({
            'complex_code': filename[0:4],
            'role': filename[5],      # 'l' (ligand) or 'r' (receptor)
            'state': filename[7]      # 'b' (bound) or 'u' (unbound)
        })
    return pd.Series({'complex_code': 'ERR', 'role': 'E', 'state': 'E'})

print("Applying README rules to filenames...")
# Apply the rules and stick the new columns onto our dataframe
parsed_info = seq_df['filename'].apply(parse_filename)
seq_df = pd.concat([seq_df, parsed_info], axis=1)

# 3. Perform Sanity Checks
print("\n Valdation")

# Check for valid roles and states
print(f"Roles found: {list(seq_df['role'].unique())} (Should only be 'l' and 'r')")
print(f"States found: {list(seq_df['state'].unique())} (Should only be 'b' and 'u')")

# Check for empty sequences
empty_seqs = seq_df[seq_df['sequence'].isnull() | (seq_df['sequence'] == '')]
print(f"Empty sequences found: {len(empty_seqs)} (Should be 0)")

# 4. Cross-Reference with Job 1 Data
print("\n--- CROSS-REFERENCE WITH BENCHMARK TABLE ---")

# Extract the 4-letter base code from the scraped table (e.g., "1AHW_AB:C" -> "1AHW")
benchmark_df['base_code'] = benchmark_df['complex_id'].str[0:4]
valid_table_codes = set(benchmark_df['base_code'])

# Get the unique 4-letter codes from our extracted PDB files
pdb_codes = set(seq_df['complex_code'])

# Compare the two lists
matched = pdb_codes.intersection(valid_table_codes)
unmatched = pdb_codes - valid_table_codes

print(f"Unique protein complexes in sequence data: {len(pdb_codes)}")
print(f"Direct matches with Benchmark Table: {len(matched)}")

if len(unmatched) > 0:
    print(f"\nNote: {len(unmatched)} PDB codes don't directly match the table.")
    print("As the README stated, these are likely artificial codes (like 9QFW or BAAD) created for uniqueness:")
    print(list(unmatched))
else:
    print("\n Perfect mapping! All PDB codes exist in the benchmark table.")
