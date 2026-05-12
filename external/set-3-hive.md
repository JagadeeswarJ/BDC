# Set 3 — Hive: Analyzing a `user_data` Table

## What Hive Is — and Why It Exists

Writing raw Java MapReduce for every query is painful. **Hive** lets you write SQL-like queries (**HiveQL**) and compiles them to MapReduce jobs.

Key idea: **schema-on-read**. The actual data sits as plain text files in HDFS; Hive's metastore just records "this folder's files have these columns". You can drop and recreate the schema without touching the data.

```
HiveQL  ──►  Hive compiler  ──►  MapReduce  ──►  reads HDFS files
```

---

## The Problem

A table `user_data` has three fields:

| Field | Type |
|-------|------|
| `data_date`  | string |
| `user_id`    | string |
| `properties` | string |

The `properties` field is semi-structured: `Age=21;state=CA;gender=M;`.

We need to:
1. Create the Hive table.
2. Load sample data.
3. Produce min, max, and unique count per property.
4. Generate count of records per state.

---

## i. Create the Table

```sql
CREATE TABLE user_data (
  data_date  STRING,
  user_id    STRING,
  properties STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE;
```

**Working:**
- `ROW FORMAT DELIMITED FIELDS TERMINATED BY ','` tells Hive the underlying file is CSV; each line splits into 3 columns at commas.
- `STORED AS TEXTFILE` = plain text (default). The data folder for this table will live under `/user/hive/warehouse/user_data/` by default.
- Because `properties` is a single STRING column holding `Age=21;state=CA;gender=M;`, we'll parse it at query time using built-in functions.

---

## ii. Fill the Table With Sample Data

Local file `user_data.csv`:
```
2026-04-01,u1,Age=21;state=CA;gender=M;
2026-04-02,u2,Age=25;state=NY;gender=F;
2026-04-03,u3,Age=30;state=CA;gender=M;
2026-04-04,u4,Age=40;state=TX;gender=M;
2026-04-05,u5,Age=21;state=NY;gender=F;
```

Push it to HDFS, then load it into Hive:
```bash
hadoop fs -put user_data.csv /tmp/
```
```sql
LOAD DATA INPATH '/tmp/user_data.csv' INTO TABLE user_data;
SELECT * FROM user_data;
```

**Working:**
- `LOAD DATA INPATH` *moves* the file from `/tmp/` into the table's warehouse directory.
- Use `LOAD DATA LOCAL INPATH` if the file is on the Linux filesystem instead.

---

## iii. Min, Max, and Unique Count of Each Property

**The parsing trick:** `str_to_map(properties, ';', '=')` converts `"Age=21;state=CA;gender=M;"` into a map `{Age:21, state:CA, gender:M}`. Then `LATERAL VIEW explode(...)` un-nests that map into one row per (key, value).

```sql
SELECT prop_key,
       MIN(prop_value)            AS min_value,
       MAX(prop_value)            AS max_value,
       COUNT(DISTINCT prop_value) AS unique_values
FROM user_data
LATERAL VIEW explode(str_to_map(properties, ';', '=')) p AS prop_key, prop_value
GROUP BY prop_key;
```

**Working step-by-step:**
1. `str_to_map(properties, ';', '=')` — splits the string by `;` first to get pairs, then by `=` inside each pair to form a map.
2. `LATERAL VIEW explode(...)` — turns each map entry into its own row, adding two new columns: `prop_key`, `prop_value`.
3. `GROUP BY prop_key` — collects all rows for `Age`, all rows for `state`, all rows for `gender`.
4. `MIN`, `MAX`, `COUNT(DISTINCT)` — aggregated per property.

**Expected:**
```
Age      21   40   4
gender   F    M    2
state    CA   TX   3
```

---

## iv. Count Records Per State

```sql
SELECT prop_value AS state, COUNT(*) AS cnt
FROM user_data
LATERAL VIEW explode(str_to_map(properties, ';', '=')) p AS prop_key, prop_value
WHERE prop_key = 'state'
GROUP BY prop_value;
```

**Working:**
- Same explode trick to get one row per (property_key, value).
- `WHERE prop_key = 'state'` filters down to only state rows.
- `GROUP BY prop_value` + `COUNT(*)` gives the count per state.

**Expected:**
```
CA   2
NY   2
TX   1
```

---

## Things to Remember

- Hive = **SQL over HDFS files**; metadata in a metastore, data as plain files.
- `LATERAL VIEW explode` is the canonical way to turn a collection column (array/map) into rows.
- `str_to_map(str, pairDelim, kvDelim)` parses a `k=v;k=v` string into a map.
- Difference from regular SQL: no row-level updates by default; Hive is built for batch analytics, not OLTP.
- Aggregations like `GROUP BY`, `MIN`, `MAX`, `COUNT(DISTINCT)` all translate into MapReduce jobs under the hood.
