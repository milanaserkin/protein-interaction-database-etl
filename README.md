# Protein-Protein Interaction Database

**Project Overview**
This repository contains the end to end workflow and scripts used to design a normalized database schema to store, query, and analyze structural and functional information about protein complexes. The biological objective was to perform ETL tasks to extract, clean, and load data from PDB files and benchmark metadata and then write queries to retrieve meaningful biological information.
Data was sourced from the Protein-Protein Docking Benchmark v5.5 (Weng Lab: https://zlab.wenglab.org/benchmark/).

### Technical Stack
* **Languages:** Python, SQL, Bash
* **Biological Data:** 3D PDB files, Benchmark v5.5 HTML table 
* **Tools & Suites:** Pandas, SQLite 
* **Infrastructure:** SLURM High-Performance Computing (HPC) Cluster

---

### Pipeline Workflow

<img width="707" height="503" alt="pipeline" src="https://github.com/user-attachments/assets/0ece1816-c322-4f01-9aaa-1ece4d6509e1" />

The automated pipeline executes the following sequential steps:
`Download Raw Data` ➔ `Verify HTML Table` ➔ `Extract PDB Sequences & Chains` ➔ `Transform & Clean Data` ➔ `Generate Relational Schema` ➔ `Load to SQLite Database` ➔ `Validate Outputs`

---

### Repository Structure
```text
├── database/
│   └──  Protein_Protein_Interactions.db    # Final database submission 
├── scripts/
│   ├── check_table_structures.py          # Verify HTML table contains all information 
│   ├── read_html.py                       # Parses HTML and extract table 
│   ├── check_read_html.py                 # Verify dataframes match original file 
│   ├── extract_pdb_sequences.py           # Unzip's PDBs, reads 3D structures and grab sequences and chains 
│   ├── check_extract_pdb_sequences.py     # Verify PDB extraction matches, original files 
│   ├── make_database.py                   # Connects to SQLite, makes relational schema, and uploads data 
│   └── check_make_database.py             # Verifies all data loaded to database accurately from original files 
├── figures/
│   ├── etl_pipeline_workflow.png          # Visual representation of the ETL pipeline
│   └── er_diagram.png                     # Conceptual schema of the database (ER diagram)
├── BINF_6211_PPI_Database.pdf             # Final project documentation and assignment details
└── README.md                              # Project documentation
