import os
import pandas as pd
from Bio import SeqIO

# 1. Point the script to where the PDB files are hiding
pdb_folder = "benchmark5.5/structures"
sequence_data = []

print(f"Scanning folder: {pdb_folder}")

# 2. Get a list of every .pdb file in that folder
pdb_files = [f for f in os.listdir(pdb_folder) if f.endswith(".pdb")]
print(f"Found {len(pdb_files)} PDB files. Extracting sequences...")

# 3. Loop through each file one by one
for pdb_file in pdb_files:
    file_path = os.path.join(pdb_folder, pdb_file)
    
    try:
        # Biopython's SeqIO reads the PDB file and finds the amino acid chains
        # We use "pdb-atom" to get the sequence based on the actual 3D structure
        for record in SeqIO.parse(file_path, "pdb-atom"):
            # Biopython names chains like "1AHW:A". Let's grab just the "A" part.
            chain_id = record.id.split(":")[-1] if ":" in record.id else record.id
            sequence = str(record.seq)
            
            # Save the info
            sequence_data.append({
                "filename": pdb_file,
                "chain_id": chain_id,
                "sequence": sequence
            })
    except Exception as e:
        print(f"Warning: Could not read {pdb_file} because {e}")

# 4. Convert our list into a Pandas DataFrame and save it as a CSV
df_seqs = pd.DataFrame(sequence_data)
df_seqs.to_csv("pdb_sequences.csv", index=False)

print(f"\nSuccess! Extracted {len(df_seqs)} total chains and saved them to pdb_sequences.csv.")
print("\n First 3 Extracted Sequences")
print(df_seqs.head(3))
