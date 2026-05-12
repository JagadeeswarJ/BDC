# 04 — Hive: SQL-Style Querying on HDFS Data

## Objective

Create a Hive table on top of your HDFS data, then run the queries from the project PDF — especially `SELECT gender, AVG(purchase_amount) GROUP BY gender`.

---

## First Principles: What Is Hive?

**Hive makes HDFS look like a SQL database.**

- You write: `SELECT * FROM customer_data WHERE gender='Female'`
- Hive translates to: a MapReduce (or Tez/Spark) job that scans HDFS files

Key insight: **Hive does not store your data.** Hive stores a *schema* (metastore) that says "files at this HDFS location have these columns in this format." The actual data stays in HDFS.

This is called **schema-on-read**: the schema is applied when you query, not when you write.

### Two Table Types

| Type | Behavior | When to use |
|------|----------|-------------|
| **Managed** | Hive owns the data. Drop table = delete files. | You want Hive to manage lifecycle. |
| **External** | Hive only references the data. Drop table = schema gone, files remain. | Shared data, raw source data. |

We'll use **Managed** for simplicity, but I'll show you External too.

---

## Step 4.1 — Open Hive

```bash
hive
```

You land at:
```
hive>
```

List databases:
```sql
SHOW DATABASES;
```

---

## Step 4.2 — Create a Database for This Project

```sql
CREATE DATABASE IF NOT EXISTS cbp;
USE cbp;
```

Verify:
```sql
SHOW DATABASES;
```

---

## Step 4.3 — Create the Hive Table

```sql
CREATE TABLE customer_data_hive (
    id INT,
    name STRING,
    age INT,
    gender STRING,
    purchase_amount DOUBLE,
    purchase_date STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
STORED AS TEXTFILE;
```

**What this does:**
- Creates a schema in Hive's metastore
- Reserves an HDFS directory for this table (typically `/user/hive/warehouse/cbp.db/customer_data_hive`)
- Tells Hive that any files placed in that directory have 6 comma-separated fields

Check the table was created:
```sql
SHOW TABLES;
DESCRIBE customer_data_hive;
```

---

## Step 4.4 — Load Data into the Hive Table

Two options. Pick one.

### Option A — Load from HDFS

```sql
LOAD DATA INPATH '/user/cloudera/cbp/input/customer_data.csv'
INTO TABLE customer_data_hive;
```

> Important: `LOAD DATA INPATH` **MOVES** the file from its HDFS location into Hive's warehouse. After this, the file at `/user/cloudera/cbp/input/` is gone.

### Option B — Load from Local filesystem

```sql
LOAD DATA LOCAL INPATH '/home/cloudera/cbp/customer_data.csv'
INTO TABLE customer_data_hive;
```

The `LOCAL` keyword means "from Linux filesystem, not HDFS." The file is **copied** (not moved) into Hive's warehouse.

**Recommendation:** Use Option B so your original HDFS file stays intact for later steps (Pig, MapReduce).

---

## Step 4.5 — Verify the Load

```sql
SELECT * FROM customer_data_hive;
```

**Expected:**
```
1   Alice    30  Female  150.0   2024-01-01
2   Bob      25  Male    200.5   2024-02-15
3   Charlie  35  Male    300.75  2024-03-20
4   Diana    28  Female  180.0   2024-04-10
5   Ethan    40  Male    250.25  2024-05-05
```

Count check:
```sql
SELECT COUNT(*) FROM customer_data_hive;
```
Should be `5`.

---

## Step 4.6 — THE KEY QUERY (From Your Project PDF)

```sql
SELECT gender, AVG(purchase_amount) AS avg_purchase
FROM customer_data_hive
GROUP BY gender;
```

**Expected output:**
```
Female   165.0
Male     250.5
```

If you used only the first 3 rows (from the PDF exactly): Female 150.0, Male 250.625.

**This is your project's "money shot" — take a screenshot.**

---

## Step 4.7 — More Useful Queries (Bonus for the Report)

### Total revenue by gender
```sql
SELECT gender, SUM(purchase_amount) AS total_revenue
FROM customer_data_hive
GROUP BY gender;
```

### Count of customers by gender
```sql
SELECT gender, COUNT(*) AS customer_count
FROM customer_data_hive
GROUP BY gender;
```

### Highest and lowest purchase
```sql
SELECT MAX(purchase_amount) AS highest,
       MIN(purchase_amount) AS lowest
FROM customer_data_hive;
```

### Top-spending customers
```sql
SELECT name, purchase_amount
FROM customer_data_hive
ORDER BY purchase_amount DESC
LIMIT 3;
```

### Age-based segmentation
```sql
SELECT
    CASE
        WHEN age < 30 THEN 'Young'
        WHEN age < 40 THEN 'Middle'
        ELSE 'Senior'
    END AS age_group,
    COUNT(*) AS count,
    AVG(purchase_amount) AS avg_spend
FROM customer_data_hive
GROUP BY
    CASE
        WHEN age < 30 THEN 'Young'
        WHEN age < 40 THEN 'Middle'
        ELSE 'Senior'
    END;
```

---

## Step 4.8 — (Optional) Demonstrate the Syllabus Example

The syllabus mentions a `user_data` table with properties like `Age=21;state=CA;gender=M;`. Here's a quick version:

```sql
CREATE TABLE user_data (
    data_date STRING,
    user_id STRING,
    properties STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t';

INSERT INTO user_data VALUES
  ('2024-01-01', 'u1', 'Age=21;state=CA;gender=M'),
  ('2024-01-01', 'u2', 'Age=30;state=NY;gender=F'),
  ('2024-01-02', 'u3', 'Age=25;state=CA;gender=M');

-- Count records per state (naive regex extraction)
SELECT
    regexp_extract(properties, 'state=([A-Z]+)', 1) AS state,
    COUNT(*) AS count
FROM user_data
GROUP BY regexp_extract(properties, 'state=([A-Z]+)', 1);
```

---

## Step 4.9 — External Table Alternative (For Understanding)

Instead of moving data into Hive's warehouse, you can point Hive at data that already lives in HDFS:

```sql
CREATE EXTERNAL TABLE customer_data_external (
    id INT,
    name STRING,
    age INT,
    gender STRING,
    purchase_amount DOUBLE,
    purchase_date STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
LOCATION '/user/cloudera/cbp/sqoop_import';
```

Now:
```sql
SELECT * FROM customer_data_external;
```

Works directly on the Sqoop output with no LOAD step. This is how production pipelines often work.

---

## Step 4.10 — Exit Hive

```sql
exit;
```

---

## Troubleshooting

### Query returns NULL values in some columns
Your CSV has spaces around commas, e.g. `1, Alice, 30`. Remove the spaces or use:
```sql
FIELDS TERMINATED BY ', '
```
Better: regenerate the CSV without spaces.

### `SemanticException ... Table not found`
You're in the wrong database. Run `USE cbp;` first or prefix tables: `SELECT * FROM cbp.customer_data_hive;`.

### `FAILED: Execution Error ...` on GROUP BY
Sometimes Hive complains about the MapReduce engine. Try:
```sql
SET hive.execution.engine=mr;
```
Then rerun the query.

### Table already exists
Drop it and recreate:
```sql
DROP TABLE customer_data_hive;
```

---

## Checklist Before Moving On

- [ ] Database `cbp` exists in Hive
- [ ] Table `customer_data_hive` contains your 5 rows
- [ ] `SELECT gender, AVG(purchase_amount) GROUP BY gender` returns sensible results
- [ ] Screenshot of this query + output saved for report

Next: `05-pig-transformation.md`.
