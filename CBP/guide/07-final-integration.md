# 07 — Final Integration: End-to-End Run and Report Preparation

## Objective

Run the full pipeline from scratch in one clean sequence, collect all the screenshots and outputs you need for your report, and verify each deliverable matches the project PDF.

---

## The End-to-End Pipeline

You will execute this sequence in one session:

```
MySQL (customer_db)
    |
    | sqoop import
    v
HDFS (/user/cloudera/cbp/sqoop_import)
    |
    +---> Hive table (customer_data_hive)
    |       |
    |       +--> SELECT gender, AVG(purchase_amount) ... [SCREENSHOT 1]
    |
    +---> Pig script (gender_stats.pig)
    |       |
    |       +--> HDFS output [SCREENSHOT 2]
    |
    +---> MapReduce (CustomerGenderCount)
            |
            +--> HDFS output [SCREENSHOT 3]
```

---

## Step 7.1 — Pre-Flight Cleanup

Start fresh. From terminal:

```bash
# Clean HDFS
hadoop fs -rm -r /user/cloudera/cbp 2>/dev/null

# Recreate base structure
hadoop fs -mkdir -p /user/cloudera/cbp/input
hadoop fs -mkdir -p /user/cloudera/cbp/output
```

Drop Hive tables if present:
```bash
hive -e "DROP DATABASE IF EXISTS cbp CASCADE;"
```

Reset MySQL table if needed:
```bash
mysql -u root -pcloudera -e "DROP DATABASE IF EXISTS customer_db;"
```

---

## Step 7.2 — Seed MySQL

```bash
mysql -u root -pcloudera <<'SQL'
CREATE DATABASE customer_db;
USE customer_db;

CREATE TABLE customer_data (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    age INT,
    gender VARCHAR(10),
    purchase_amount DECIMAL(10,2),
    purchase_date DATE
);

INSERT INTO customer_data VALUES
(1, 'Alice',   30, 'Female', 150.00, '2024-01-01'),
(2, 'Bob',     25, 'Male',   200.50, '2024-02-15'),
(3, 'Charlie', 35, 'Male',   300.75, '2024-03-20'),
(4, 'Diana',   28, 'Female', 180.00, '2024-04-10'),
(5, 'Ethan',   40, 'Male',   250.25, '2024-05-05');

SELECT * FROM customer_data;
SQL
```

**Expected:** 5 rows displayed. → **SCREENSHOT A: MySQL source data**

---

## Step 7.3 — Sqoop Import

```bash
sqoop import \
    --connect jdbc:mysql://localhost:3306/customer_db \
    --username root \
    --password cloudera \
    --table customer_data \
    --target-dir /user/cloudera/cbp/sqoop_import \
    --m 1
```

Verify:
```bash
hadoop fs -ls /user/cloudera/cbp/sqoop_import
hadoop fs -cat /user/cloudera/cbp/sqoop_import/part-m-00000
```

→ **SCREENSHOT B: Sqoop job logs + HDFS output**

Also copy the file to input folder for other steps:
```bash
hadoop fs -cp /user/cloudera/cbp/sqoop_import/part-m-00000 /user/cloudera/cbp/input/customer_data.csv
```

---

## Step 7.4 — Hive

```bash
hive <<'HQL'
CREATE DATABASE cbp;
USE cbp;

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
STORED AS TEXTFILE;

LOAD DATA INPATH '/user/cloudera/cbp/input/customer_data.csv' INTO TABLE customer_data_hive;

SELECT * FROM customer_data_hive;

SELECT gender, AVG(purchase_amount) AS avg_purchase
FROM customer_data_hive
GROUP BY gender;
HQL
```

→ **SCREENSHOT C: Hive GROUP BY gender result — THIS IS THE KEY RESULT**

> Note: `LOAD DATA INPATH` moves the file. Re-upload for Pig and MapReduce steps:
> ```bash
> hadoop fs -cp /user/cloudera/cbp/sqoop_import/part-m-00000 /user/cloudera/cbp/input/customer_data.csv
> ```

---

## Step 7.5 — Pig

```bash
hadoop fs -rm -r /user/cloudera/cbp/output/pig_gender_stats
pig -x mapreduce /home/cloudera/cbp/gender_stats.pig
hadoop fs -cat /user/cloudera/cbp/output/pig_gender_stats/part-r-00000
```

→ **SCREENSHOT D: Pig output with gender stats**

---

## Step 7.6 — MapReduce

```bash
cd /home/cloudera/cbp/mr_custom

hadoop fs -rm -r /user/cloudera/cbp/output/mr_gender_count

hadoop jar customer_gender_count.jar CustomerGenderCount \
    /user/cloudera/cbp/input/customer_data.csv \
    /user/cloudera/cbp/output/mr_gender_count

hadoop fs -cat /user/cloudera/cbp/output/mr_gender_count/part-r-00000
```

→ **SCREENSHOT E: MapReduce output showing gender counts**

Also capture YARN page:
- Open http://localhost:8088 in Firefox
- Find your recent "Customer Gender Count" job
- → **SCREENSHOT F: YARN successful job page**

---

## Step 7.7 — Screenshot Checklist for the Report

Map each screenshot to a section of your project PDF:

| Screenshot | Goes in PDF Section |
|------------|---------------------|
| A — MySQL source data | Methodology § Data Integration |
| B — Sqoop job + HDFS output | Methodology § Data Integration / Results |
| C — Hive GROUP BY result (Female/Male avg) | Results (matches PDF's Test Case 4) |
| D — Pig output | Methodology § Data Transformation |
| E — MapReduce output | Methodology § Data Processing |
| F — YARN job history | Results (proof of distributed execution) |

Additional nice-to-haves:
- NameNode web UI (http://localhost:50070) showing your HDFS files
- Hue file browser (http://localhost:8888)
- Terminal showing `hadoop fs -ls /user/cloudera/cbp -R` (whole tree)

---

## Step 7.8 — Generate a Final "Tree View" for Documentation

```bash
echo "=========== HDFS Structure ==========="
hadoop fs -ls -R /user/cloudera/cbp

echo ""
echo "=========== MySQL customer_db ==========="
mysql -u root -pcloudera -e "USE customer_db; SHOW TABLES; SELECT * FROM customer_data;"

echo ""
echo "=========== Hive Tables ==========="
hive -e "USE cbp; SHOW TABLES; SELECT * FROM customer_data_hive; SELECT gender, AVG(purchase_amount) FROM customer_data_hive GROUP BY gender;"
```

Pipe all output to a file for the report:
```bash
./run_all_output.sh > /home/cloudera/cbp/full_output.txt 2>&1
```

Paste relevant sections into the report.

---

## Step 7.9 — Fill in the Report Template

Your PDF has these sections. Map outputs:

| Report Section | What to Put There |
|----------------|-------------------|
| Abstract | (Already written — leave as is) |
| Introduction | (Already written) |
| Methodology § Overview | Pipeline diagram from `00-overview.md` |
| Methodology § HDFS | Screenshot B + explanation |
| Methodology § Sqoop | Sqoop command + Screenshot B + explanation |
| Methodology § MapReduce | Java code + Screenshot E + explanation |
| Methodology § Hive | SQL query + Screenshot C + explanation |
| Methodology § Pig | Pig script + Screenshot D + explanation |
| Test Cases | Screenshots A–E |
| Results | Screenshot C (the GROUP BY answer) |
| Discussion | (Already written — keep the tool-by-tool analysis) |
| Conclusion | (Already written) |
| References | (Already listed) |

---

## Step 7.10 — Project Demo Script (What to Show the Examiner)

If you need to demonstrate live, follow this 5-minute path:

1. "First, here's our source data in MySQL" — run `SELECT * FROM customer_data;`
2. "We import it to HDFS using Sqoop" — run the sqoop command
3. "Verify HDFS has it" — `hadoop fs -cat .../part-m-00000`
4. "Now we query it with Hive" — open hive, run the GROUP BY
5. "Same analysis with Pig" — run the pig script
6. "And a custom Java MapReduce" — run the JAR
7. "All three give consistent answers" — show the outputs side-by-side

---

## Checklist Before Submission

- [ ] MySQL has `customer_db.customer_data` with 5 rows
- [ ] Sqoop imported to `/user/cloudera/cbp/sqoop_import/`
- [ ] Hive `cbp.customer_data_hive` returns correct GROUP BY result
- [ ] Pig script produces `/user/cloudera/cbp/output/pig_gender_stats/`
- [ ] Custom MapReduce JAR produces `/user/cloudera/cbp/output/mr_gender_count/`
- [ ] All 6 screenshots (A–F) captured
- [ ] YARN shows successful jobs in http://localhost:8088
- [ ] Report PDF sections filled in with commands + screenshots + explanations

Next (if needed): `08-troubleshooting.md`.
