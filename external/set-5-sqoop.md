# Set 5 — Sqoop: SQL ⇄ Hadoop

## What Sqoop Is — and Why It Exists

Most business data lives in relational databases (MySQL, Oracle, etc.). Hadoop processes data sitting in **HDFS**. Writing a custom JDBC-to-HDFS script for every table is tedious.

**Sqoop = SQL-to-Hadoop.** One command imports an entire RDBMS table into HDFS or directly into a Hive table. The reverse direction is **export**.

```
  MySQL                          Hadoop
  ┌──────┐    sqoop import     ┌─────────────┐
  │ tbl  │  ───────────────►   │ HDFS / Hive │
  │      │  ◄───────────────   │             │
  └──────┘    sqoop export     └─────────────┘
```

Under the hood Sqoop launches a **map-only MapReduce job**: multiple mappers each pull a slice of the table by primary-key ranges, in parallel.

---

## I. Create a Table in Hive Using HiveQL

We'll create a target table in Hive. (You could also let Sqoop auto-create it via `--create-hive-table`; we show both.)

Prepare MySQL source data first:
```bash
mysql -u root -p   # password: cloudera
```
```sql
CREATE DATABASE testdb;
USE testdb;

CREATE TABLE employee (
  id     INT,
  name   VARCHAR(50),
  salary INT
);

INSERT INTO employee VALUES (1,'Alice',30000),
                            (2,'Bob',40000),
                            (3,'Charlie',50000);
exit;
```

---

## II. Import the SQL Table Data Into Hive Using Sqoop

```bash
sqoop import \
  --connect jdbc:mysql://localhost/testdb \
  --username root --password root \
  --table employee \
  --hive-import --create-hive-table --hive-table emp_data \
  --m 1
```

**Working flag by flag:**

| Flag | What it does |
|------|--------------|
| `--connect jdbc:mysql://localhost/testdb` | JDBC URL pointing to the source DB |
| `--username / --password` | DB credentials |
| `--table employee` | Source table in MySQL |
| `--hive-import` | After loading into HDFS, automatically register the data as a Hive table |
| `--create-hive-table` | Auto-create the Hive table schema based on the MySQL schema |
| `--hive-table emp_data` | Name to use for the Hive table |
| `--m 1` | Use one mapper. Needed because the MySQL table has no PK (and our data is tiny); otherwise Sqoop would error asking for `--split-by` |

Verify in Hive:
```bash
hive
```
```sql
SELECT * FROM emp_data;
```

**Expected:**
```
1   Alice    30000
2   Bob      40000
3   Charlie  50000
```

---

## III. Export Hive Table Data — to Local Machine and to SQL

### A) To the local Linux filesystem

The Hive table's data lives in HDFS at `/user/hive/warehouse/emp_data`. Pull it down:
```bash
hdfs dfs -get /user/hive/warehouse/emp_data ~/emp_data
ls ~/emp_data
cat ~/emp_data/part-m-00000
```

**Working:** `hdfs dfs -get <hdfs_path> <local_path>` copies HDFS files back to Linux. Sqoop writes mapper output as `part-m-00000`, `part-m-00001`, etc.

### B) Back to MySQL

First create the destination table — Sqoop does **not** auto-create on export:
```bash
mysql -u root -p
```
```sql
USE testdb;
CREATE TABLE emp_export (
  id     INT,
  name   VARCHAR(50),
  salary INT
);
exit;
```

Then run the export:
```bash
sqoop export \
  --connect jdbc:mysql://localhost/testdb \
  --username root --password root \
  --table emp_export \
  --export-dir /user/hive/warehouse/emp_data \
  --m 1
```

**Working:**
- `--export-dir` points at the HDFS directory holding the rows to push out.
- Sqoop reads each line, splits it by the default delimiter, and runs an `INSERT` per row into MySQL.
- `--m 1` keeps it to a single mapper (use more for bigger tables).

Verify:
```bash
mysql -u root -p
```
```sql
USE testdb;
SELECT * FROM emp_export;
```

**Expected:** the three Alice/Bob/Charlie rows back in MySQL.

---

## Direction Cheat Sheet

| You want to... | Command |
|----------------|---------|
| Pull a MySQL table into HDFS | `sqoop import --target-dir <hdfs>` |
| Pull a MySQL table straight into Hive | `sqoop import --hive-import --hive-table <name>` |
| Push an HDFS dir back to MySQL | `sqoop export --export-dir <hdfs> --table <mysql_tbl>` |

---

## Things to Remember

- Direction: **`import` = into Hadoop**, **`export` = out of Hadoop**. Always.
- Sqoop runs **map-only** jobs — no reducer, because data is partitioned by PK ranges.
- `--m 1` = single mapper, single output file. Higher values need either a primary key or `--split-by <col>`.
- Export requires the **target table to exist already** in MySQL with the right schema.
- The Hive warehouse path defaults to `/user/hive/warehouse/<table_name>` — that's where the files actually live.
