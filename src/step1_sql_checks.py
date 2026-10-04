"""Step 1: load Cookie Cats into a SQL database, run metric queries, SRM check.
Usage: python src/step1_sql_checks.py [path_to_csv]
Uses DuckDB if installed, otherwise falls back to SQLite (same SQL).
"""
import sys, re
import pandas as pd
from scipy.stats import chisquare

CSV = sys.argv[1] if len(sys.argv) > 1 else "data/cookie_cats.csv"

df = pd.read_csv(CSV)
for c in ["retention_1", "retention_7"]:
    df[c] = df[c].astype(str).str.lower().map({"true": 1, "false": 0, "1": 1, "0": 0})

try:
    import duckdb
    con = duckdb.connect()
    con.register("ab_df", df)
    con.execute("CREATE TABLE ab AS SELECT * FROM ab_df")
    run = lambda q: con.execute(q).df()
    engine = "DuckDB"
except ImportError:
    import sqlite3
    con = sqlite3.connect(":memory:")
    df.to_sql("ab", con, index=False)
    run = lambda q: pd.read_sql_query(q, con)
    engine = "SQLite"
print(f"Engine: {engine} | rows loaded: {len(df):,}\n")

sql_text = open("sql/01_load_and_check.sql").read()
queries = [q.strip() for q in sql_text.split(";") if "SELECT" in q]
titles = re.findall(r"-- (Q\d\..*)", sql_text)
pd.set_option("display.width", 140)
for t, q in zip(titles, queries):
    print(t)
    print(run(q).to_string(index=False), "\n")

# SRM: are the groups close to the intended 50/50 split?
counts = run("SELECT version, COUNT(*) n FROM ab GROUP BY version ORDER BY version")["n"].tolist()
stat, p = chisquare(counts)
print(f"SRM chi-square test vs 50/50: chi2={stat:.3f}, p={p:.4f}")
if p < 0.001:
    print("-> Strong SRM: investigate before trusting results.")
elif p < 0.05:
    print("-> Mild imbalance (0.001 <= p < 0.05): report it and justify proceeding.")
else:
    print("-> No evidence of SRM.")
