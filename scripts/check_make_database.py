import sqlite3
import pandas as pd

# 1. Connect to SQL and load the Raw CSVs (The "Source of Truth")
conn = sqlite3.connect('Protein_Protein_Interactions.db')
benchmark_df = pd.read_csv("Table_Docking_Benchmark_5.5.csv")
seq_df = pd.read_csv("pdb_sequences.csv")

print(" SOURCE-TO-TARGET VALIDATION SCRIPT")

# TEST 1: ROW COUNTS (CSV vs SQL)
print("\n--- TEST 1: ENTITY COUNTS ---")
# Expected from CSV
exp_complexes = len(benchmark_df)
# Since you merged files and sequences into the 'Structure' table, 
# the row count should now exactly match the total chains in seq_df
exp_structures = len(seq_df) 

# Actual from SQL
sql_complexes = pd.read_sql_query("SELECT COUNT(*) as c FROM Complex", conn).iloc[0]['c']
sql_structures = pd.read_sql_query("SELECT COUNT(*) as c FROM Structure", conn).iloc[0]['c']

print(f"Complexes: Expected {exp_complexes} | SQL has {sql_complexes} -> {' MATCH' if exp_complexes == sql_complexes else '❌ FAIL'}")
print(f"Structure/Chain Rows: Expected {exp_structures} | SQL has {sql_structures} -> {' MATCH' if exp_structures == sql_structures else '❌ FAIL'}")


# TEST 2: COMPLEX TYPE & DIFFICULTY (Rigid AA)
print("\n--- TEST 2: 'Rigid' Antibody-Antigen ('AA') Complexes ---")

# Calculate Expected from Raw CSV (RMSD <= 1.5 is Rigid)
expected_t2 = benchmark_df[(benchmark_df['complex_type'] == 'AA') & 
(benchmark_df['rmsd'] <= 1.5)][['complex_id', 'complex_type', 'rmsd', 'isa']].head(3)
print("🔍 EXPECTED (Calculated from Raw CSV):")
print(expected_t2)

# SQL Query
query2 = """
    SELECT complex_id, complex_type, rmsd, isa 
    FROM Complex 
    WHERE difficulty = 'rigid' AND complex_type = 'AA'
    LIMIT 3;
"""
print("\n ACTUAL (Queried from SQL Database):")
print(pd.read_sql_query(query2, conn))


# TEST 3: PROTEINS IN MULTIPLE COMPLEXES
print("\n--- TEST 3: Proteins appearing in >1 Complex ---")

# Calculate Expected from Raw CSV
p1 = benchmark_df[['pdb_1']].rename(columns={'pdb_1': 'pdb'})
p2 = benchmark_df[['pdb_2']].rename(columns={'pdb_2': 'pdb'})
all_p = pd.concat([p1, p2]).dropna(subset=['pdb'])
expected_freq = all_p['pdb'].value_counts()
expected_freq = expected_freq[expected_freq > 1].head(3)
print("🔍 EXPECTED (Counted from Raw CSV):")
print(expected_freq)

# SQL Query (Updated for new table 'Complex_Protein' and column 'pdb_protein')
query3 = """
    SELECT cp.pdb_protein as pdb, COUNT(cp.complex_id) as appearance_count
    FROM Complex_Protein cp
    GROUP BY cp.pdb_protein
    HAVING appearance_count > 1
    ORDER BY appearance_count DESC
    LIMIT 3;
"""
print("\n ACTUAL (Queried from SQL Database):")
print(pd.read_sql_query(query3, conn))


# ==========================================
# TEST 4: SEQUENCES FOR A SPECIFIC COMPLEX (1AHW)
# ==========================================
print("\n--- TEST 4: Join sequences for complex '1AHW' ---")

# Calculate Expected from Raw CSV
expected_t4 = seq_df[seq_df['filename'].str.startswith('1AHW')][['filename', 'chain_id', 'sequence']].head(3)
# Truncate sequence for display
expected_t4['sequence'] = expected_t4['sequence'].str[:30] + "..."
print("🔍 EXPECTED (Filtered directly from pdb_sequences.csv):")
print(expected_t4)

# SQL Query (Updated for the newly merged 'Structure' table)
# SQL Query (Updated for the correct full ID match)
query4 = """
    SELECT 
        c.complex_id,
        s.filename, 
        s.chain_id, 
        SUBSTR(s.sequence, 1, 30) || '...' as sequence
    FROM Complex c
    JOIN Structure s ON c.complex_id = s.complex_id
    WHERE c.complex_id = '1AHW_AB:C'
    LIMIT 3;
"""
print("\n ACTUAL (Queried through SQL Join):")
print(pd.read_sql_query(query4, conn))

conn.close()
