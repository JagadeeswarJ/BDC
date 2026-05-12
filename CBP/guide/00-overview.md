# 00 — Overview: Client Intelligence Center

## What We Are Building

A complete data pipeline on the Hadoop ecosystem that:
1. Takes customer data from a MySQL database
2. Moves it into HDFS (distributed storage)
3. Processes it with MapReduce (parallel computation)
4. Queries it with Hive (SQL-style analysis)
5. Transforms it with Pig (scripting-style analysis)

The end result: **insights about customer behavior** (e.g., average purchase amount by gender).

---

## The Pipeline (Visual)

```
   +---------+    Sqoop     +--------+    Hive       +-----------+
   |  MySQL  |  ----------> |  HDFS  | -----------> |  Insights |
   |         |              |        |    Pig        |           |
   |customer_|   +--------+ |        |  MapReduce    |  Female:  |
   |  data   |   | Local  | |        | -----------> |   150.00  |
   +---------+   |  CSV   | |        |               |  Male:    |
                 +--------+ +--------+               |  250.625  |
                     |          ^                    +-----------+
                     +---put--->+
```

---

## Why Each Tool Exists (First Principles)

| Tool | Problem It Solves |
|------|-------------------|
| **HDFS** | A single hard drive cannot hold or read huge files fast. HDFS splits files across many machines. |
| **Sqoop** | You have data in SQL databases. Writing custom scripts to move it to HDFS is tedious. Sqoop is a one-command bridge. |
| **MapReduce** | Processing terabytes of data sequentially takes forever. Split work across many nodes and combine results. |
| **Hive** | Writing MapReduce Java code for every query is painful. Hive lets you write SQL which compiles to MapReduce. |
| **Pig** | SQL is declarative; sometimes you want step-by-step data transformations. Pig Latin is a procedural scripting language. |

---

## Dataset We Will Use

**File:** `customer_data.csv`

```
1,Alice,30,Female,150.00,2024-01-01
2,Bob,25,Male,200.50,2024-02-15
3,Charlie,35,Male,300.75,2024-03-20
```

**Columns:** `id, name, age, gender, purchase_amount, date`

This is the exact dataset shown in your project PDF's Test Cases.

---

## The Target Result

Running this Hive query:
```sql
SELECT gender, AVG(purchase_amount) AS avg_purchase
FROM customer_data_hive
GROUP BY gender;
```

Must output:
```
Female   150.00
Male     250.625
```

That's the "money shot" for your report.

---

## Guide Structure — Read in This Order

| File | Topic | Time |
|------|-------|------|
| `01-cloudera-setup.md` | Start VM, verify tools work | 10 min |
| `02-hdfs-basics.md` | Understand + use HDFS commands | 15 min |
| `03-sqoop-mysql-import.md` | MySQL → HDFS via Sqoop | 20 min |
| `04-hive-querying.md` | Hive table + GROUP BY query | 20 min |
| `05-pig-transformation.md` | Pig script for filtering/grouping | 20 min |
| `06-mapreduce-processing.md` | Run MapReduce on HDFS data | 20 min |
| `07-final-integration.md` | Run full pipeline end-to-end + collect screenshots | 30 min |
| `08-troubleshooting.md` | Common errors and fixes | as needed |

**Total active time: ~2 hours** if everything goes smoothly.

---

## Prerequisites

- Cloudera QuickStart VM (CDH 5.x) running in VirtualBox or VMware
- At least 8 GB RAM allocated to VM (4 GB minimum but slow)
- Terminal access as user `cloudera` (default password: `cloudera`)

---

## Mental Model to Hold Throughout

There are TWO filesystems in play at all times:

1. **Linux local filesystem** — `/home/cloudera/...` — your VM's disk
2. **HDFS** — `/user/cloudera/...` or `/user/hadoop/...` — Hadoop's distributed storage

When you see `hadoop fs -put local_file hdfs_path`, you're copying from (1) to (2).
When you see `hadoop fs -get hdfs_path local_file`, you're copying from (2) to (1).

Don't mix them up — it's the single most common source of confusion.

---

Next: open `01-cloudera-setup.md`.
