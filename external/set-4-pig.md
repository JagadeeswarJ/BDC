# Set 4 — Pig: Simple Logs

## What Pig Is — and Why It Exists

Hive is **declarative** (SQL — "tell me what you want"). **Pig** is **procedural** — you describe a dataflow step by step using **Pig Latin**:

```
LOAD  →  FILTER  →  GROUP  →  FOREACH (aggregate)  →  STORE / DUMP
```

A Pig script compiles to one or more MapReduce jobs. It's lazy: nothing executes until a `DUMP` or `STORE` is reached.

Open the shell with `pig` (Grunt prompt). Run a script with `pig script.pig`.

---

## The Problem

Tab-delimited log files with these fields:

| # | Field | Example |
|---|-------|---------|
| 1 | `site`        | `google` |
| 2 | `hour_of_day` | `10`     |
| 3 | `page_views`  | `100`    |
| 4 | `data_date`   | `2026-04-25` |

The lab brief says to use **`PigStorage('')`** for tab-delimited loads. (`` is the SOH/Ctrl-A character — Hive's default delimiter. The brief is unusual, but we follow it as written; in practice you'd also see `PigStorage('\t')` for tab-delimited data.)

---

## Prepare Input

```bash
nano simple_logs.txt
```
Put inside (tab between fields):
```
google	10	100	2026-04-25
google	11	150	2026-04-25
yahoo	10	200	2026-04-25
google	10	120	2026-04-26
yahoo	11	180	2026-04-26
```

Save: `Ctrl+O`, Enter, `Ctrl+X`.

```bash
hdfs dfs -mkdir -p /data/pig/simple_logs
hdfs dfs -put simple_logs.txt /data/pig/simple_logs/
hdfs dfs -ls /data/pig/simple_logs/
```

Launch Pig: `pig`

---

## Load the Logs

```pig
logs = LOAD '/data/pig/simple_logs/simple_logs.txt'
       USING PigStorage('')
       AS (site:chararray, hour:int, page_views:int, data_date:chararray);

DUMP logs;
```

**Working:**
- `LOAD ... USING PigStorage(delim)` reads the file and splits each line by `delim`.
- The `AS (...)` part attaches a schema with column names and types.
- `chararray` = string, `int` = integer. Pig's type system is similar to Hive's.

---

## i. Total Views Per Hour Per Day

```pig
grp1 = GROUP logs BY (data_date, hour);
res1 = FOREACH grp1 GENERATE group.data_date, group.hour, SUM(logs.page_views);
DUMP res1;
```

**Working:**
- `GROUP BY (data_date, hour)` builds groups keyed by the composite (date, hour). Each group has a `group` field (the key) and a `logs` field (a bag of matching rows).
- `FOREACH ... GENERATE` projects each group: pull the date and hour out of the key, then sum the `page_views` from all rows in the bag.

**Expected:**
```
(2026-04-25,10,300)
(2026-04-25,11,150)
(2026-04-26,10,120)
(2026-04-26,11,180)
```

---

## ii. Total Views Per Day

```pig
grp2 = GROUP logs BY data_date;
res2 = FOREACH grp2 GENERATE group, SUM(logs.page_views);
DUMP res2;
```

**Working:** Single-key grouping. `group` here is just the date string. Sum all `page_views` in each group.

**Expected:**
```
(2026-04-25,450)
(2026-04-26,300)
```

---

## iii. Total Views Per Hour (Across All Days)

```pig
grp3 = GROUP logs BY hour;
res3 = FOREACH grp3 GENERATE group, SUM(logs.page_views);
DUMP res3;
```

**Working:** Same structure, now keyed on `hour` only, so views are accumulated across every date.

**Expected:**
```
(10,420)
(11,330)
```

---

## iv. Word Count in Pig

Prepare input:
```bash
nano input.txt
```
```
hello world hello pig
big data pig
```
```bash
hdfs dfs -mkdir -p /data/pig
hdfs dfs -put input.txt /data/pig/
```

Pig script:
```pig
A = LOAD '/data/pig/input.txt' USING PigStorage('\t') AS (line:chararray);
B = FOREACH A GENERATE FLATTEN(TOKENIZE(line)) AS word;
C = GROUP B BY word;
D = FOREACH C GENERATE group, COUNT(B);
DUMP D;
```

**Working line by line:**
- `LOAD ... AS (line:chararray)` — read each line of the file as one big string.
- `TOKENIZE(line)` returns a *bag* of words; `FLATTEN` un-nests that bag so each word becomes its own row.
- `GROUP B BY word` — gather all rows with the same word.
- `FOREACH ... GENERATE group, COUNT(B)` — emit (word, number_of_occurrences). `COUNT(B)` counts rows in the bag for that group.

**Expected:**
```
(big,1)
(data,1)
(hello,2)
(pig,2)
(world,1)
```

That's five lines of Pig for what was ~50 lines of Java in Set 2.

---

## Things to Remember

- Pig is **lazy** — nothing runs until `DUMP` or `STORE`.
- `GROUP` produces a special structure: a key (`group`) + a bag of rows (named after the input alias).
- `FLATTEN` is essential whenever you need to expand a bag/tuple into multiple rows.
- Pig data model: **atom, tuple, bag, map**.
- Hive ≈ SQL; Pig ≈ scripting; MapReduce ≈ raw Java. **All three compile to the same engine** underneath.
