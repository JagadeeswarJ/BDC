# Final Implementation — Client Intelligence Center

Run these in order inside the Cloudera VM terminal.

---

## 1. HDFS — Store Data

```bash
mkdir -p /home/cloudera/cbp
cat > /home/cloudera/cbp/customer_data.csv <<EOF
1,Alice,30,Female,150.00,2024-01-01
2,Bob,25,Male,200.50,2024-02-15
3,Charlie,35,Male,300.75,2024-03-20
4,Diana,28,Female,180.00,2024-04-10
5,Ethan,40,Male,250.25,2024-05-05
EOF

hadoop fs -mkdir -p /user/cloudera/cbp/input
hadoop fs -put -f /home/cloudera/cbp/customer_data.csv /user/cloudera/cbp/input/
hadoop fs -cat /user/cloudera/cbp/input/customer_data.csv
```

---

## 2. Sqoop — MySQL → HDFS

```bash
# Create DB and table in MySQL
mysql -u root -pcloudera -e "
CREATE DATABASE IF NOT EXISTS customer_db;
USE customer_db;
CREATE TABLE IF NOT EXISTS customer_data (
    id INT PRIMARY KEY, name VARCHAR(50), age INT,
    gender VARCHAR(10), purchase_amount DECIMAL(10,2), purchase_date DATE
);
INSERT IGNORE INTO customer_data VALUES
(1,'Alice',30,'Female',150.00,'2024-01-01'),
(2,'Bob',25,'Male',200.50,'2024-02-15'),
(3,'Charlie',35,'Male',300.75,'2024-03-20'),
(4,'Diana',28,'Female',180.00,'2024-04-10'),
(5,'Ethan',40,'Male',250.25,'2024-05-05');
"

# Import to HDFS
hadoop fs -rm -r /user/cloudera/cbp/sqoop_import
sqoop import \
  --connect jdbc:mysql://localhost:3306/customer_db \
  --username root --password cloudera \
  --table customer_data \
  --target-dir /user/cloudera/cbp/sqoop_import \
  --m 1

# Verify
hadoop fs -cat /user/cloudera/cbp/sqoop_import/part-m-00000
```

---

## 3. Hive — Query

```bash
hive -e "
CREATE DATABASE IF NOT EXISTS cbp;
USE cbp;

CREATE TABLE IF NOT EXISTS customer_data_hive (
    id INT, name STRING, age INT, gender STRING,
    purchase_amount DOUBLE, purchase_date STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE;

LOAD DATA LOCAL INPATH '/home/cloudera/cbp/customer_data.csv'
OVERWRITE INTO TABLE customer_data_hive;

SELECT * FROM customer_data_hive;

SELECT gender, AVG(purchase_amount) AS avg_purchase
FROM customer_data_hive
GROUP BY gender;
"
```

---

## 4. Pig — Transform

```bash
cat > /home/cloudera/cbp/gender_stats.pig <<'EOF'
customers = LOAD '/user/cloudera/cbp/input/customer_data.csv'
    USING PigStorage(',')
    AS (id:int, name:chararray, age:int, gender:chararray,
        purchase_amount:double, purchase_date:chararray);

grouped = GROUP customers BY gender;

stats = FOREACH grouped GENERATE
    group AS gender,
    COUNT(customers) AS customer_count,
    AVG(customers.purchase_amount) AS avg_purchase,
    SUM(customers.purchase_amount) AS total_purchase;

STORE stats INTO '/user/cloudera/cbp/output/pig_gender_stats'
    USING PigStorage(',');
EOF

hadoop fs -rm -r /user/cloudera/cbp/output/pig_gender_stats
pig -x mapreduce /home/cloudera/cbp/gender_stats.pig
hadoop fs -cat /user/cloudera/cbp/output/pig_gender_stats/part-r-00000
```

---

## Expected Outputs

**Sqoop / HDFS cat:**
```
1,Alice,30,Female,150.00,2024-01-01
2,Bob,25,Male,200.50,2024-02-15
3,Charlie,35,Male,300.75,2024-03-20
4,Diana,28,Female,180.00,2024-04-10
5,Ethan,40,Male,250.25,2024-05-05
```

**Hive GROUP BY gender:**
```
Female   165.0
Male     250.5
```

**Pig output:**
```
Female,2,165.0,330.0
Male,3,250.5,751.5
```

---

## Screenshots to Take for Report

1. `hadoop fs -cat` of the uploaded CSV
2. Sqoop job running + `part-m-00000` contents
3. Hive `SELECT *` result
4. Hive `GROUP BY gender` result ← most important
5. Pig `part-r-00000` contents
