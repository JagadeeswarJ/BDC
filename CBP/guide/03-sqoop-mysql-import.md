# 03 — Sqoop: Importing from MySQL to HDFS

## Objective

Create the same customer data in a MySQL database, then use Sqoop to import it into HDFS automatically. This is the "real-world" path: your data starts in a relational database, and you bring it into Hadoop for analysis.

---

## First Principles: What Is Sqoop?

**Sqoop = SQL-to-Hadoop.**

Relational databases (MySQL, Oracle, PostgreSQL) store data in tables with rows and columns. They scale vertically (one powerful machine).

Hadoop scales horizontally (many machines). Its tools expect data in files (CSV, Parquet, Avro) on HDFS.

Sqoop is a **translator**:
- Reads from a SQL database using JDBC (standard Java DB connector)
- Launches **MapReduce jobs** that read table chunks in parallel
- Writes each chunk as a text file into an HDFS directory

One Sqoop command replaces hundreds of lines of ETL code.

**Direction:**
- `sqoop import` = MySQL → HDFS
- `sqoop export` = HDFS → MySQL

---

## Step 3.1 — Open MySQL

```bash
mysql -u root -p
```
Password: `cloudera`

You should see `mysql>` prompt.

---

## Step 3.2 — Create the Database and Table

```sql
CREATE DATABASE IF NOT EXISTS customer_db;
USE customer_db;

CREATE TABLE customer_data (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    age INT,
    gender VARCHAR(10),
    purchase_amount DECIMAL(10,2),
    purchase_date DATE
);
```

> Note: I used `purchase_date` instead of `date` because `date` is a reserved word in some SQL flavors. Avoids headaches.

Insert data:
```sql
INSERT INTO customer_data VALUES
(1, 'Alice',   30, 'Female', 150.00, '2024-01-01'),
(2, 'Bob',     25, 'Male',   200.50, '2024-02-15'),
(3, 'Charlie', 35, 'Male',   300.75, '2024-03-20'),
(4, 'Diana',   28, 'Female', 180.00, '2024-04-10'),
(5, 'Ethan',   40, 'Male',   250.25, '2024-05-05');
```

Verify:
```sql
SELECT * FROM customer_data;
```

**Expected:** 5 rows displayed.

Exit MySQL:
```sql
exit;
```

---

## Step 3.3 — Pre-Check: Clear the HDFS Target Directory

Sqoop fails if the target directory already exists. Make sure it doesn't:
```bash
hadoop fs -rm -r /user/cloudera/cbp/sqoop_import
```
(If it says "No such file", that's fine — we just wanted to be sure.)

---

## Step 3.4 — Run the Sqoop Import

```bash
sqoop import \
  --connect jdbc:mysql://localhost:3306/customer_db \
  --username root \
  --password cloudera \
  --table customer_data \
  --target-dir /user/cloudera/cbp/sqoop_import \
  --m 1
```

**Breakdown:**

| Flag | Meaning |
|------|---------|
| `--connect` | JDBC URL: `jdbc:mysql://host:port/database` |
| `--username` / `--password` | MySQL credentials |
| `--table` | Source table in MySQL |
| `--target-dir` | Destination directory in HDFS |
| `--m 1` | Use 1 mapper (for small data). Larger data: use `--m 4` or higher for parallelism. |

**What happens internally:**
- Sqoop reads the table schema from MySQL
- Generates a Java class representing the row
- Submits a MapReduce job (you will see "map 0% reduce 0%" progress)
- Each mapper reads a slice of rows and writes CSV files to HDFS

---

## Step 3.5 — Verify the Import

```bash
hadoop fs -ls /user/cloudera/cbp/sqoop_import
```

**Expected:**
```
-rw-r--r--   1 cloudera cloudera          0 ... /user/cloudera/cbp/sqoop_import/_SUCCESS
-rw-r--r--   1 cloudera cloudera       ~150 ... /user/cloudera/cbp/sqoop_import/part-m-00000
```

- `_SUCCESS` is an empty marker file — Sqoop writes it when the job finishes cleanly.
- `part-m-00000` contains the actual data (`part-m` = output from a mapper).

View the data:
```bash
hadoop fs -cat /user/cloudera/cbp/sqoop_import/part-m-00000
```

**Expected:**
```
1,Alice,30,Female,150.00,2024-01-01
2,Bob,25,Male,200.50,2024-02-15
3,Charlie,35,Male,300.75,2024-03-20
4,Diana,28,Female,180.00,2024-04-10
5,Ethan,40,Male,250.25,2024-05-05
```

**This matches your `customer_data.csv` from Step 02.** Sqoop just did the same upload, but from MySQL instead of a local file.

---

## Step 3.6 — Common Variations (For Your Report)

### Import only specific columns:
```bash
sqoop import \
  --connect jdbc:mysql://localhost:3306/customer_db \
  --username root --password cloudera \
  --table customer_data \
  --columns "id,name,gender" \
  --target-dir /user/cloudera/cbp/sqoop_subset \
  --m 1
```

### Import with a WHERE filter:
```bash
sqoop import \
  --connect jdbc:mysql://localhost:3306/customer_db \
  --username root --password cloudera \
  --table customer_data \
  --where "gender='Female'" \
  --target-dir /user/cloudera/cbp/sqoop_female \
  --m 1
```

### List all tables in a database (sanity check):
```bash
sqoop list-tables \
  --connect jdbc:mysql://localhost:3306/customer_db \
  --username root --password cloudera
```

---

## Step 3.7 — Export HDFS Data Back to MySQL (Reverse Direction)

This satisfies the syllabus point "Export hive table data into local machine and into SQL."

First create an empty target table in MySQL:
```bash
mysql -u root -p
```
```sql
USE customer_db;
CREATE TABLE customer_data_export (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    age INT,
    gender VARCHAR(10),
    purchase_amount DECIMAL(10,2),
    purchase_date DATE
);
exit;
```

Then export:
```bash
sqoop export \
  --connect jdbc:mysql://localhost:3306/customer_db \
  --username root --password cloudera \
  --table customer_data_export \
  --export-dir /user/cloudera/cbp/sqoop_import \
  --input-fields-terminated-by ',' \
  --m 1
```

Verify in MySQL:
```bash
mysql -u root -p -e "SELECT * FROM customer_db.customer_data_export;"
```

**Expected:** Same 5 rows.

---

## Troubleshooting

### `Access denied for user 'root'@'localhost'`
Password wrong. Cloudera default is `cloudera`. If changed, use the correct one.

### `Communications link failure`
MySQL is not running. Start it:
```bash
sudo service mysqld start
```

### `Output directory already exists`
Delete it first:
```bash
hadoop fs -rm -r /user/cloudera/cbp/sqoop_import
```

### `Could not load db driver class: com.mysql.jdbc.Driver`
MySQL JDBC jar is missing from Sqoop's lib folder. Cloudera VM has it pre-installed. If you hit this, copy it:
```bash
sudo cp /usr/share/java/mysql-connector-java.jar /var/lib/sqoop/
```

---

## Checklist Before Moving On

- [ ] MySQL `customer_db.customer_data` table exists with 5 rows
- [ ] Sqoop import ran without errors
- [ ] `/user/cloudera/cbp/sqoop_import/part-m-00000` contains the data
- [ ] (Optional) Sqoop export back to MySQL works
- [ ] You took a screenshot of the successful Sqoop job output for the report

Next: `04-hive-querying.md`.
