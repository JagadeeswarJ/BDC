# Set 6 — Sqoop: SQL ⇄ Hadoop

## What Sqoop Is

Sqoop moves data between relational databases (MySQL) and Hadoop (HDFS/Hive).

```
MySQL ──sqoop import──► HDFS / Hive
MySQL ◄──sqoop export── HDFS / Hive
```

Under the hood Sqoop runs a map-only MapReduce job — multiple mappers each pull a slice of the MySQL table in parallel.

**Memory rule:** `import` = into Hadoop | `export` = out of Hadoop

---

## I. Create Table in Hive Using HiveQL

First, create the source data in MySQL:
```bash
mysql -u root -p
```
```sql
CREATE DATABASE testdb;
USE testdb;

CREATE TABLE employee (
  id     INT,
  name   VARCHAR(50),
  salary INT
);

INSERT INTO employee VALUES (1,'Alice',30000),(2,'Bob',40000),(3,'Charlie',50000);
exit;
```

Now create the target Hive table:
```bash
hive
```
```sql
CREATE TABLE emp_hive (
  id     INT,
  name   STRING,
  salary INT
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE;
```

---

## II. Import SQL Table Data into Hive Using Sqoop

```bash
sqoop import \
  --connect jdbc:mysql://localhost/testdb \
  --username root --password cloudera \
  --table employee \
  --hive-import \
  --hive-table emp_hive \
  --m 1
```

**Flag breakdown:**

| Flag | What it does |
|------|-------------|
| `--connect jdbc:mysql://localhost/testdb` | JDBC URL to the source MySQL database |
| `--username root --password cloudera` | MySQL credentials |
| `--table employee` | Source table in MySQL |
| `--hive-import` | Load data into Hive after pulling from MySQL |
| `--hive-table emp_hive` | Target Hive table name |
| `--m 1` | Use 1 mapper (needed when table has no primary key) |

Verify in Hive:
```bash
hive
```
```sql
SELECT * FROM emp_hive;
```

**Expected:**
```
1   Alice    30000
2   Bob      40000
3   Charlie  50000
```

---

## III. Export Hive Table Data — to Local Machine and to SQL

### A) Export to Local Machine

The Hive table data lives in HDFS. Use `hdfs dfs -get` to pull it locally:
```bash
hdfs dfs -get /user/hive/warehouse/emp_hive /home/cloudera/emp_local
ls /home/cloudera/emp_local
cat /home/cloudera/emp_local/part-m-00000
```

### B) Export Back to MySQL (Sqoop Export)

First create the destination table in MySQL — Sqoop does **not** auto-create on export:
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

Then run Sqoop export:
```bash
sqoop export \
  --connect jdbc:mysql://localhost/testdb \
  --username root --password cloudera \
  --table emp_export \
  --export-dir /user/hive/warehouse/emp_hive \
  --m 1
```

- `--export-dir` points to the HDFS directory holding the Hive table data.
- Sqoop reads each line and INSERTs it into MySQL.

Verify:
```bash
mysql -u root -p
```
```sql
USE testdb;
SELECT * FROM emp_export;
```

**Expected:** Alice, Bob, Charlie rows back in MySQL.

---

## Things to Remember

- `import` = MySQL → Hadoop. `export` = Hadoop → MySQL. **Never confuse direction.**
- Sqoop runs **map-only** MapReduce — no reducer.
- `--m 1` = single mapper. Required when table has no primary key (otherwise Sqoop errors asking for `--split-by`).
- For export, the MySQL target table **must already exist** with the correct schema.
- Hive warehouse path: `/user/hive/warehouse/<table_name>/` — that's where `--export-dir` should point.
- `--hive-import` + `--hive-table` lets Sqoop directly register data in Hive without a separate LOAD step.
