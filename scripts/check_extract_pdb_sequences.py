import os
import random
import pandas as pd
from Bio import SeqIO
import warnings

# Ignore those loud PDB warnings for our test so the terminal stays clean
warnings.filterwarnings('ignore')

csv_file = "pdb_sequences.csv"
pdb_folder = "benchmark5.5/structures"

print("Loading CSV...")
df_seqs = pd.read_csv(csv_file)

# 1. EXACT CHAIN COUNTING
pdb_files = [f for f in os.listdir(pdb_folder) if f.endswith(".pdb")]
print(f"\n SCANNING {len(pdb_files)} RAW FILES TO COUNT CHAINS")

expected_chain_count = 0
for filename in pdb_files:
    file_path = os.path.join(pdb_folder, filename)
    try:
        # Count exactly how many chains are physically inside this specific file
        chains_in_file = len(list(SeqIO.parse(file_path, "pdb-atom")))
        expected_chain_count += chains_in_file
    except Exception:
        pass

print("\n OVERALL COUNTS")
print(f"Total .pdb files in folder: {len(pdb_files)}")
print(f"Expected chains (counted directly from raw files): {expected_chain_count}")
print(f"Total sequences (rows) in CSV: {len(df_seqs)}")

if expected_chain_count == len(df_seqs):
    print("SUCCESS: The number of chains in the raw files matches the CSV rows perfectly!")
else:
    print(" WARNING: Mismatch! The CSV rows do not match the expected chain count.")


# 2. RANDOM 20 SEQUENCE CHECK
print("\n RANDOM 20 SEQUENCE CHECK ")
sample_indices = random.sample(range(len(df_seqs)), 20)

all_matched = True

for idx in sample_indices:
    row = df_seqs.iloc[idx]
    filename = row['filename']
    csv_chain = str(row['chain_id'])
    csv_sequence = str(row['sequence'])
    
    file_path = os.path.join(pdb_folder, filename)
    
    fresh_sequence = None
    try:
        for record in SeqIO.parse(file_path, "pdb-atom"):
            chain_id = record.id.split(":")[-1] if ":" in record.id else record.id
            if chain_id == csv_chain:
                fresh_sequence = str(record.seq)
                break
                
        if fresh_sequence == csv_sequence:
            print(f" {filename} (Chain {csv_chain}): 100% match!")
        else:
            print(f" {filename} (Chain {csv_chain}): MISMATCH FOUND!")
            all_matched = False
            
    except Exception as e:
        print(f" Error reading {filename}: {e}")
        all_matched = False

# 3. VERDICT
if all_matched:
    print("\n GOOD! The sequences in the CSV exactly match the raw PDB files.")
else:
    print("\n Mismatches found. Check the logs above.")
