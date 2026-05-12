# 08 — Troubleshooting Reference

General rules when something breaks:
1. **Read the error message** — it usually tells you exactly what's wrong.
2. **Check the logs** — `yarn logs -applicationId <id>` or the web UI at port 8088.
3. **Confirm HDFS paths** — most errors are "wrong path" or "path already exists."

---

## HDFS Issues

### `Connection refused` when running `hadoop fs`
NameNode is down. Restart HDFS:
```bash
sudo service hadoop-hdfs-namenode restart
sudo service hadoop-hdfs-datanode restart
```
Or just restart the VM.

### `Output directory already exists`
Every Hadoop job (Sqoop, Pig, MapReduce) refuses to overwrite. Delete first:
```bash
hadoop fs -rm -r /user/cloudera/cbp/output/<whatever>
```

### `No such file or directory`
- Check the path: `hadoop fs -ls /user/cloudera/cbp`
- Make sure you're pointing at the HDFS path, not a local path
- Re-upload if the file was moved by a Hive `LOAD DATA INPATH`

### Permission denied
```bash
hadoop fs -chmod -R 777 /user/cloudera/cbp
```
(For production, you'd set proper permissions — for lab, full-open is fine.)

---

## Sqoop Issues

### `Access denied for user 'root'@'localhost'`
Wrong MySQL password. Default on Cloudera is `cloudera`. Try:
```bash
mysql -u root -p
```
and use the password you actually set.

### `com.mysql.jdbc.Driver not found`
```bash
ls /var/lib/sqoop/
```
If no MySQL connector jar, copy it:
```bash
sudo cp /usr/share/java/mysql-connector-java.jar /var/lib/sqoop/
sudo chmod 644 /var/lib/sqoop/mysql-connector-java.jar
```

### `Could not establish connection` to MySQL
```bash
sudo service mysqld status
sudo service mysqld start
```

### Import succeeds but output has weird fields (e.g., nulls)
MySQL DATE columns sometimes serialize oddly. Add:
```bash
--map-column-java purchase_date=String
```
to the sqoop command.

### `Zero-date cannot be represented as java.sql.Date`
Add to JDBC URL:
```
?zeroDateTimeBehavior=convertToNull
```
Full example:
```
--connect "jdbc:mysql://localhost:3306/customer_db?zeroDateTimeBehavior=convertToNull"
```

---

## Hive Issues

### `SemanticException ... Table not found`
Wrong database. Run `USE cbp;` or qualify the table: `cbp.customer_data_hive`.

### `FAILED: Execution Error ...` on GROUP BY / aggregation
Switch execution engine:
```sql
SET hive.execution.engine=mr;
```
Then rerun the query.

### Query returns NULLs for all rows
- Your CSV delimiter doesn't match `FIELDS TERMINATED BY`.
- Your CSV has spaces like `1, Alice, 30` — either strip spaces or use `STRING` for all columns and cast later.

### `Table already exists`
```sql
DROP TABLE IF EXISTS customer_data_hive;
```

### Hive starts slowly or hangs
HiveServer2 may be in a weird state. Restart:
```bash
sudo service hive-server2 restart
sudo service hive-metastore restart
```

### Can't connect to metastore
```bash
sudo service hive-metastore restart
```
Wait 30 seconds, then retry.

---

## Pig Issues

### `ERROR 2999: Unexpected internal error`
Usually a schema mismatch. Check:
- Field count in `LOAD ... AS (...)` matches your CSV columns
- Data types are correct (`int` for numbers, `chararray` for strings, `double` for decimals)

### `Output Location Validation Failed`
Delete output dir:
```bash
hadoop fs -rm -r /user/cloudera/cbp/output/pig_gender_stats
```

### Pig runs but produces no output file
You didn't call `STORE`. Pig is lazy — relations only materialize on `STORE` or `DUMP`.

### `DUMP` prints weird tuples like `(Female,2,165.0)`
That's normal — Pig outputs relations as tuples. When you `STORE` with `PigStorage(',')` it becomes clean CSV.

### Pig can't find input file
Make sure the file is in HDFS, not local:
```bash
hadoop fs -ls /user/cloudera/cbp/input/
```

---

## MapReduce Issues

### `ClassNotFoundException` when running the JAR
- Check the class name in your command EXACTLY matches the file.
- Verify the JAR contains the class:
  ```bash
  jar tf customer_gender_count.jar
  ```
  Expected: `CustomerGenderCount.class`, `CustomerGenderCount$GenderMapper.class`, etc.

### Compilation error: `package org.apache.hadoop... does not exist`
Your classpath is wrong. Use the Hadoop-provided compiler:
```bash
hadoop com.sun.tools.javac.Main CustomerGenderCount.java
```
This automatically puts Hadoop libraries on the classpath.

### Job finishes but output is empty
Your Mapper isn't emitting anything. Common causes:
- `fields.length` check too strict
- CSV delimiter mismatch
- Unexpected characters in input (BOM, Windows line endings)

Try:
```bash
file /home/cloudera/cbp/customer_data.csv
```
If it says "CRLF line terminators", convert:
```bash
dos2unix /home/cloudera/cbp/customer_data.csv
```

### `java.lang.NumberFormatException` in Mapper
Your code tries to parse text as int and fails. Add a try-catch or validate before parsing.

### Job hangs at "map 100% reduce 0%"
Usually a memory/YARN issue on a low-RAM VM. Restart YARN:
```bash
sudo service hadoop-yarn-resourcemanager restart
sudo service hadoop-yarn-nodemanager restart
```

---

## MySQL Issues

### `mysqld.sock` errors / won't start
```bash
sudo rm -f /var/lib/mysql/mysql.sock
sudo service mysqld restart
```

### Forgot MySQL root password
```bash
sudo service mysqld stop
sudo mysqld_safe --skip-grant-tables &
mysql -u root
```
Then:
```sql
USE mysql;
UPDATE user SET password=PASSWORD('cloudera') WHERE user='root';
FLUSH PRIVILEGES;
```

---

## VM / General Issues

### VM runs out of memory
- Close Firefox, Hue, and other heavy GUI apps
- Allocate more RAM to the VM (8 GB is comfortable)
- Or shut down unused services:
  ```bash
  sudo service flume-ng-agent stop
  sudo service oozie stop
  sudo service impala-catalog stop
  sudo service impala-server stop
  sudo service impala-state-store stop
  ```

### VM is extremely slow
Run this once to see what's hogging:
```bash
top
```
Press `M` to sort by memory.

### Services won't start after reboot
```bash
sudo /home/cloudera/cloudera-manager --force --express
```

### Clock is skewed (Kerberos-style errors on some services)
```bash
sudo ntpdate pool.ntp.org
```

---

## The Universal Debugging Checklist

When something fails, walk through this:

1. **What command did you run?** Copy-paste it.
2. **What was the exact error message?** Read all of it, not just the first line.
3. **Does the input path exist?**
   ```bash
   hadoop fs -ls <input_path>
   ```
4. **Does the output path ALREADY exist (bad)?**
   ```bash
   hadoop fs -ls <output_path>
   ```
5. **Are the relevant services running?**
   ```bash
   sudo service --status-all | grep running
   ```
6. **What do the logs say?**
   - YARN: `yarn logs -applicationId application_XXX`
   - HDFS: `/var/log/hadoop-hdfs/`
   - Hive: `/tmp/cloudera/hive.log`

If stuck after this checklist, bring me:
- Exact command you ran
- Exact error message (full stack trace)
- Output of the relevant `hadoop fs -ls`
