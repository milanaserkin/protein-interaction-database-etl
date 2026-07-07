import sqlite3
import pandas as pd

# 1. LOAD THE DATA
print("Loading CSV files...")
benchmark_df = pd.read_csv("Table_Docking_Benchmark_5.5.csv")
seq_df = pd.read_csv("pdb_sequences.csv")

# 2. CONNECT TO SQLITE
conn = sqlite3.connect('Protein_Protein_Interactions.db')
cursor = conn.cursor()

# 3. BUILD THE SCHEMA (Entities & Attributes)
print("Building database schema...")

cursor.executescript('''
    -- Table 1: Complex
    CREATE TABLE IF NOT EXISTS Complex (
        complex_id TEXT PRIMARY KEY,
        complex_type TEXT,
        rmsd REAL,
        isa REAL,
        difficulty TEXT,
        multimer_status TEXT
    );

    -- Table 2: Protein
    CREATE TABLE IF NOT EXISTS Protein (
        pdb_protein TEXT PRIMARY KEY,
        protein_name TEXT
    );

    -- Table 3: Complex_Protein (Junction)
    CREATE TABLE IF NOT EXISTS Complex_Protein (
        complex_id TEXT,
        pdb_protein TEXT,
        role TEXT,
        PRIMARY KEY (complex_id, pdb_protein, role),
        FOREIGN KEY (complex_id) REFERENCES Complex(complex_id),
        FOREIGN KEY (pdb_protein) REFERENCES Protein(pdb_protein)
    );

    -- Table 4: Structure (Merged files, chains, sequences, and hetatms)
    CREATE TABLE IF NOT EXISTS Structure (
        structure_id INTEGER PRIMARY KEY AUTOINCREMENT,
        pdb_protein TEXT,
        complex_id TEXT,
        filename TEXT,
        chain_id TEXT,
        state TEXT,
        sequence TEXT,
        hetatms TEXT,
        FOREIGN KEY (pdb_protein) REFERENCES Protein(pdb_protein),
        FOREIGN KEY (complex_id) REFERENCES Complex(complex_id),
        UNIQUE(filename, chain_id)
    );
''')

# 4. LOAD THE DATA (Transforming and Inserting)
print("Populating tables (Normalization in progress)...")

# --- Load Table 1: Complex ---
def calc_difficulty(rmsd):
    try:
        val = float(rmsd)
        if val <= 1.5: return 'rigid'
        elif val <= 2.2: return 'medium'
        else: return 'difficult'
    except:
        return 'unknown'

benchmark_df['difficulty'] = benchmark_df['rmsd'].apply(calc_difficulty)

complex_data = benchmark_df[['complex_id', 'complex_type', 'rmsd', 'isa', 'difficulty', 'multimer']].copy()
complex_records = list(complex_data.itertuples(index=False, name=None))
cursor.executemany('INSERT OR IGNORE INTO Complex VALUES (?, ?, ?, ?, ?, ?)', complex_records)

# --- Load Table 2: Protein ---
proteins_1 = benchmark_df[['pdb_1', 'protein_1']].rename(columns={'pdb_1': 'pdb', 'protein_1': 'name'})
proteins_2 = benchmark_df[['pdb_2', 'protein_2']].rename(columns={'pdb_2': 'pdb', 'protein_2': 'name'})
all_proteins = pd.concat([proteins_1, proteins_2]).drop_duplicates(subset=['pdb']).dropna(subset=['pdb'])

protein_records = list(all_proteins.itertuples(index=False, name=None))
cursor.executemany('INSERT OR IGNORE INTO Protein VALUES (?, ?)', protein_records)

# --- Load Table 3: Complex_Protein ---
participants = []
lookup = {} 

for _, row in benchmark_df.iterrows():
    cid = row['complex_id']
    base = cid[0:4] # Grab just the 4-letter PDB code for matching
    
    # Receptor
    if pd.notna(row['pdb_1']):
        participants.append((cid, row['pdb_1'], 'Receptor'))
        lookup[(base, 'Receptor')] = (cid, row['pdb_1'], str(row['hetatms_1']))
        
    # Ligand
    if pd.notna(row['pdb_2']):
        participants.append((cid, row['pdb_2'], 'Ligand'))
        lookup[(base, 'Ligand')] = (cid, row['pdb_2'], str(row['hetatms_2']))

cursor.executemany('INSERT OR IGNORE INTO Complex_Protein VALUES (?, ?, ?)', participants)

# --- Load Table 4: Structure ---
structure_data = []

for _, row in seq_df.iterrows():
    f = row['filename']
    chain = row['chain_id']
    seq = row['sequence']
    
    if len(f) >= 12 and f.endswith('.pdb'):
        base_cid = f[0:4]
        role = 'Ligand' if f[5] == 'l' else 'Receptor'
        state = 'Bound' if f[7] == 'b' else 'Unbound'
        
        # Now it will perfectly match '1AHW' and pull the full data
        protein_info = lookup.get((base_cid, role))
        if protein_info:
            full_cid = protein_info[0]
            pdb_prot = protein_info[1]
            hetatms_val = protein_info[2]
        else:
            full_cid = None
            pdb_prot = None
            hetatms_val = None
            
        final_cid = full_cid if state == 'Bound' else None
        
        structure_data.append((pdb_prot, final_cid, f, chain, state, seq, hetatms_val))

cursor.executemany('''
    INSERT OR IGNORE INTO Structure (pdb_protein, complex_id, filename, chain_id, state, sequence, hetatms) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', structure_data)

# 5. SAVE AND CLOSE
conn.commit()
conn.close()

print("\n SUCCESS! Database 'Protein_Protein_Interactions.db' created and fully populated.")
