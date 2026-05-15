# Set 5 — Hive: user_data Table

## What Hive Is

Hive lets you write SQL-like queries (HiveQL) on data stored as plain files in HDFS. No Java MapReduce needed — Hive compiles your query to MapReduce automatically.

**Key idea:** schema-on-read. Data is a plain text file in HDFS; the Hive metastore just says "this folder has these columns."

---

## The Table Structure

Table `user_data` has three fields:

| Field | Type | Example |
|-------|------|---------|
| `data_date`  | string | `2026-04-01` |
| `user_id`    | string | `u1` |
| `properties` | string | `Age=25;state=Telangana;gender=M;` |

The `properties` field contains key=value pairs separated by `;`.

---

## i. Create the Table in Hive

```sql
CREATE TABLE user_data (
  data_date  STRING,
  user_id    STRING,
  properties STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE;
```

- `ROW FORMAT DELIMITED FIELDS TERMINATED BY ','` — tells Hive the file is CSV; each line is split into 3 columns at commas.
- `STORED AS TEXTFILE` — data lives as plain text in HDFS under `/user/hive/warehouse/user_data/`.

---

## ii. Fill the Table With Sample Data

Create a local file `user_data.csv`:
```
2026-04-01,u1,Age=25;state=Telangana;gender=M;
2026-04-02,u2,Age=30;state=AndhraPradesh;gender=F;
2026-04-03,u3,Age=22;state=Telangana;gender=M;
2026-04-04,u4,Age=35;state=Karnataka;gender=F;
2026-04-05,u5,Age=28;state=AndhraPradesh;gender=M;
2026-04-06,u6,Age=22;state=Telangana;gender=F;
```

Upload to HDFS and load into Hive:
```bash
hadoop fs -put user_data.csv /tmp/
```
```sql
LOAD DATA INPATH '/tmp/user_data.csv' INTO TABLE user_data;
SELECT * FROM user_data;
```

- `LOAD DATA INPATH` **moves** the file from `/tmp/` into the Hive warehouse directory.
- Use `LOAD DATA LOCAL INPATH` if the file is on the Linux filesystem directly.

---

## iii. Min, Max, and Unique Count Per Property

**The trick:** `str_to_map(properties, ';', '=')` converts `"Age=25;state=Telangana;gender=M;"` into a map `{Age:25, state:Telangana, gender:M}`. Then `LATERAL VIEW explode(...)` turns each map entry into its own row.

```sql
SELECT prop_key,
       MIN(prop_value)            AS min_value,
       MAX(prop_value)            AS max_value,
       COUNT(DISTINCT prop_value) AS unique_values
FROM user_data
LATERAL VIEW explode(str_to_map(properties, ';', '=')) p AS prop_key, prop_value
GROUP BY prop_key;
```

**How it works step by step:**
1. `str_to_map(properties, ';', '=')` — splits by `;` to get pairs, then by `=` inside each pair → a map.
2. `LATERAL VIEW explode(...)` — un-nests the map into rows; adds columns `prop_key` and `prop_value`.
3. `GROUP BY prop_key` — collects all rows for `Age`, `state`, `gender` separately.
4. `MIN`, `MAX`, `COUNT(DISTINCT)` — aggregates per property.

**Expected output:**
```
Age     22  35  4
gender  F   M   2
state   AndhraPradesh  Telangana  3
```

---

## iv. Count Per State

```sql
SELECT prop_value AS state, COUNT(*) AS cnt
FROM user_data
LATERAL VIEW explode(str_to_map(properties, ';', '=')) p AS prop_key, prop_value
WHERE prop_key = 'state'
GROUP BY prop_value;
```

- Same explode trick, but `WHERE prop_key = 'state'` filters to only state rows.
- `GROUP BY prop_value` + `COUNT(*)` gives count per state.

**Expected output:**
```
AndhraPradesh   2
Karnataka       1
Telangana       3
```

---

## Things to Remember

- Hive = **SQL over HDFS files**. Data is plain text; schema is in the metastore.
- `LATERAL VIEW explode` turns a map/array column into multiple rows — essential for semi-structured data.
- `str_to_map(str, pairDelim, kvDelim)` parses `k=v;k=v` strings into a Hive map.
- `LOAD DATA INPATH` **moves** the file (removes it from `/tmp/`). `LOCAL INPATH` copies from the Linux disk.
- Hive is for **batch analytics**, not row-level updates. No UPDATE/DELETE in basic Hive.
- Aggregations `MIN`, `MAX`, `COUNT(DISTINCT)`, `GROUP BY` all run as MapReduce jobs underneath.
