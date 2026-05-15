# Set 4 — Pig: Student Dataset

## What Pig Is

Pig is a **procedural dataflow language** for Hadoop. You describe transformations step-by-step in Pig Latin; Pig compiles them to MapReduce jobs.

```
LOAD → FILTER/GROUP/FOREACH → STORE / DUMP
```

Pig is **lazy** — nothing executes until `DUMP` or `STORE` is reached.

Open Pig shell: `pig` (gives `grunt>` prompt)

---

## The Dataset

File `students.csv`:
```
001,Jagruthi,21,Hyderabad,9.1
002,Praneeth,22,Chennai,8.6
003,Sujith,22,Mumbai,7.8
004,Sreeja,21,Bengaluru,9.2
005,Mahesh,24,Hyderabad,8.8
006,Rohit,22,Chennai,7.8
```

Fields: `StudentID, FirstName, Age, City, CGPA`

---

## Prepare Input

```bash
nano students.csv
```
Paste the data above. Save: `Ctrl+O`, Enter, `Ctrl+X`.

```bash
hadoop fs -mkdir -p /user/cloudera/pig/students
hadoop fs -put students.csv /user/cloudera/pig/students/
```

---

## LOAD — Load the Dataset

```pig
students = LOAD '/user/cloudera/pig/students/students.csv'
           USING PigStorage(',')
           AS (StudentID:chararray, FirstName:chararray, Age:int, City:chararray, CGPA:float);
```

- `LOAD ... USING PigStorage(',')` reads the CSV and splits each line at commas.
- `AS (...)` attaches column names and types.
- `chararray` = string, `int` = integer, `float` = decimal number.

---

## DUMP — Display the Data

```pig
DUMP students;
```

**Expected output:**
```
(001,Jagruthi,21,Hyderabad,9.1)
(002,Praneeth,22,Chennai,8.6)
(003,Sujith,22,Mumbai,7.8)
(004,Sreeja,21,Bengaluru,9.2)
(005,Mahesh,24,Hyderabad,8.8)
(006,Rohit,22,Chennai,7.8)
```

- `DUMP` triggers execution and prints all rows to the console.
- Use it to verify data at any step.

---

## DESCRIBE — Show the Schema

```pig
DESCRIBE students;
```

**Expected output:**
```
students: {StudentID: chararray, FirstName: chararray, Age: int, City: chararray, CGPA: float}
```

- `DESCRIBE` shows the relation's schema (column names + types) without running the data pipeline.
- Useful to confirm types were loaded correctly.

---

## STORE — Save the Output to HDFS

```pig
STORE students INTO '/user/cloudera/pig/students_output'
      USING PigStorage(',');
```

- `STORE` triggers execution and writes the result to HDFS in the given directory.
- `PigStorage(',')` writes CSV format (comma-separated).
- Output directory must not exist beforehand.

Verify the stored file:
```bash
hadoop fs -cat /user/cloudera/pig/students_output/part-m-00000
```

---

## Full Script (All 4 Operations Together)

```pig
-- LOAD
students = LOAD '/user/cloudera/pig/students/students.csv'
           USING PigStorage(',')
           AS (StudentID:chararray, FirstName:chararray, Age:int, City:chararray, CGPA:float);

-- DESCRIBE (schema check)
DESCRIBE students;

-- DUMP (display data)
DUMP students;

-- STORE (save to HDFS)
STORE students INTO '/user/cloudera/pig/students_output'
      USING PigStorage(',');
```

Run the script file:
```bash
pig students.pig
```

---

## Things to Remember

| Operation | Purpose | Triggers Execution? |
|-----------|---------|-------------------|
| `LOAD` | Read data from HDFS | No (lazy) |
| `DESCRIBE` | Show schema | No |
| `DUMP` | Print data to console | **Yes** |
| `STORE` | Write data to HDFS | **Yes** |

- `PigStorage(',')` for CSV; `PigStorage('\t')` for tab-delimited.
- `chararray` = String, `int` = integer, `float` = decimal.
- Pig runs on HDFS paths — always use HDFS paths in `LOAD`/`STORE`, not local Linux paths.
- `DESCRIBE` just shows the schema — it does **not** print data.
- `DUMP` is for debugging; `STORE` is for saving final results.
