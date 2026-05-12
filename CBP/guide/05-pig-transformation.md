# 05 — Pig: Data Transformation with Pig Latin

## Objective

Use Pig Latin scripts to load customer data from HDFS, filter and transform it, group it by gender, and write results back to HDFS.

---

## First Principles: What Is Pig?

**Pig is a scripting language for data transformation.**

Hive is SQL → good for *declarative* queries ("give me the answer").
Pig is Pig Latin → good for *procedural* data pipelines ("do step 1, then step 2, then step 3").

### The Pig Mental Model

Everything in Pig is a **relation** (think: a table in memory). You:
1. **LOAD** a relation from HDFS
2. **FILTER / GROUP / FOREACH / JOIN / ORDER** — transform relations
3. **STORE** the final relation back to HDFS (or **DUMP** to screen)

Pig is **lazy**: nothing actually runs until you `STORE` or `DUMP`. Before that, Pig just builds up an execution plan. When you trigger output, it compiles the plan into MapReduce jobs and runs them.

### The Five Verbs You Need

| Verb | What it does | SQL analog |
|------|--------------|------------|
| `LOAD` | Read data into a relation | `FROM` |
| `FILTER` | Keep rows matching a condition | `WHERE` |
| `GROUP` | Group rows by a key | `GROUP BY` |
| `FOREACH ... GENERATE` | Transform each row/group | `SELECT` |
| `STORE` | Write relation to HDFS | (output) |

---

## Step 5.1 — Ensure Data Is in HDFS

Pig reads from HDFS. Make sure your file is there:
```bash
hadoop fs -ls /user/cloudera/cbp/input/
```

If you followed `04-hive-querying.md` Option A (LOAD DATA INPATH), Hive moved the file into the warehouse. Re-upload:
```bash
hadoop fs -mkdir -p /user/cloudera/cbp/input
hadoop fs -put -f /home/cloudera/cbp/customer_data.csv /user/cloudera/cbp/input/
hadoop fs -cat /user/cloudera/cbp/input/customer_data.csv
```
(The `-f` flag overwrites if it exists.)

---

## Step 5.2 — Clean the Output Directory

Pig fails if output directory exists:
```bash
hadoop fs -rm -r /user/cloudera/cbp/output/pig_gender_stats
```
("No such file" = fine.)

---

## Step 5.3 — Write Your First Pig Script

```bash
nano /home/cloudera/cbp/gender_stats.pig
```

Paste this:
```pig
-- gender_stats.pig
-- Compute per-gender stats from customer data

-- Step 1: Load CSV from HDFS
customers = LOAD '/user/cloudera/cbp/input/customer_data.csv'
    USING PigStorage(',')
    AS (id:int, name:chararray, age:int, gender:chararray,
        purchase_amount:double, purchase_date:chararray);

-- Step 2: Group rows by gender
grouped_by_gender = GROUP customers BY gender;

-- Step 3: For each group, compute count and average purchase
gender_stats = FOREACH grouped_by_gender GENERATE
    group AS gender,
    COUNT(customers) AS customer_count,
    AVG(customers.purchase_amount) AS avg_purchase,
    SUM(customers.purchase_amount) AS total_purchase;

-- Step 4: Store result back to HDFS
STORE gender_stats INTO '/user/cloudera/cbp/output/pig_gender_stats'
    USING PigStorage(',');
```

Save: `Ctrl+O`, `Enter`, `Ctrl+X`.

**Syntax notes:**
- `chararray` = Pig's string type
- `--` starts a single-line comment
- `PigStorage(',')` = CSV (default delimiter is tab)
- `group` is an auto-generated field holding the group key (here, gender value)
- Inside `FOREACH`, `customers` refers to all rows in that group — you can aggregate over them

---

## Step 5.4 — Run the Script

```bash
pig -x mapreduce /home/cloudera/cbp/gender_stats.pig
```

The `-x mapreduce` flag tells Pig to run as a real distributed job (as opposed to `-x local`, which runs on your Linux FS without HDFS).

You'll see MapReduce progress:
```
... Success!
Input: 1 file(s) processed ... 5 records
Output: 1 file(s) ... 2 records
```

---

## Step 5.5 — View the Result

```bash
hadoop fs -ls /user/cloudera/cbp/output/pig_gender_stats
hadoop fs -cat /user/cloudera/cbp/output/pig_gender_stats/part-r-00000
```

**Expected:**
```
Female,2,165.0,330.0
Male,3,250.5,751.5
```

(Format: gender, count, average, total)

**Screenshot this for the report.**

---

## Step 5.6 — Interactive Mode (Grunt Shell)

For debugging, use interactive mode. It shows you what each step looks like.

```bash
pig
```

You see:
```
grunt>
```

Run each line and inspect:
```pig
customers = LOAD '/user/cloudera/cbp/input/customer_data.csv'
    USING PigStorage(',')
    AS (id:int, name:chararray, age:int, gender:chararray,
        purchase_amount:double, purchase_date:chararray);

DUMP customers;
```

`DUMP` prints the relation to your terminal — useful for debugging. But never use it in a production script on big data (it prints everything).

```pig
DESCRIBE customers;
```
Shows the schema (column names + types).

Filter example:
```pig
female_only = FILTER customers BY gender == 'Female';
DUMP female_only;
```

Exit grunt:
```pig
quit;
```

---

## Step 5.7 — More Transformations (Bonus for Report)

### Filter + project (SELECT + WHERE in SQL terms)
```pig
big_spenders = FILTER customers BY purchase_amount > 200.0;
names_and_amounts = FOREACH big_spenders GENERATE name, purchase_amount;
DUMP names_and_amounts;
```

### Order by
```pig
ordered = ORDER customers BY purchase_amount DESC;
top_3 = LIMIT ordered 3;
DUMP top_3;
```

### Word count (classic Pig example — satisfies syllabus "word count script")

Create `/home/cloudera/cbp/wordcount.pig`:
```pig
-- Load a text file (could be any text — let's use our CSV as a "text")
input_data = LOAD '/user/cloudera/cbp/input/customer_data.csv' AS (line:chararray);

-- Break each line into words
words = FOREACH input_data GENERATE FLATTEN(TOKENIZE(line, ',')) AS word;

-- Group by word and count
word_groups = GROUP words BY word;
word_count = FOREACH word_groups GENERATE group AS word, COUNT(words) AS count;

-- Order by count desc
ordered_counts = ORDER word_count BY count DESC;

-- Store
STORE ordered_counts INTO '/user/cloudera/cbp/output/pig_wordcount' USING PigStorage(',');
```

Run and view:
```bash
hadoop fs -rm -r /user/cloudera/cbp/output/pig_wordcount
pig -x mapreduce /home/cloudera/cbp/wordcount.pig
hadoop fs -cat /user/cloudera/cbp/output/pig_wordcount/part-r-00000
```

---

## Step 5.8 — (Optional) The Log Analysis Example from Syllabus

The syllabus mentions tab-delimited logs with columns `(site, hour_of_day, page_views, data_date)`. Here's a ready-made script.

Create sample logs:
```bash
cat > /home/cloudera/cbp/simple_logs.tsv <<EOF
site1	9	100	2024-01-01
site1	10	150	2024-01-01
site1	9	120	2024-01-02
site2	9	80	2024-01-01
site2	10	90	2024-01-02
EOF

hadoop fs -mkdir -p /user/cloudera/cbp/simple_logs
hadoop fs -put -f /home/cloudera/cbp/simple_logs.tsv /user/cloudera/cbp/simple_logs/
```

Script `/home/cloudera/cbp/simple_logs.pig`:
```pig
logs = LOAD '/user/cloudera/cbp/simple_logs/simple_logs.tsv'
    USING PigStorage('\t')
    AS (site:chararray, hour_of_day:int, page_views:int, data_date:chararray);

-- Views per hour per day
by_hour_day = GROUP logs BY (hour_of_day, data_date);
views_per_hour_day = FOREACH by_hour_day GENERATE
    group.hour_of_day AS hour,
    group.data_date AS date,
    SUM(logs.page_views) AS total_views;

-- Views per day
by_day = GROUP logs BY data_date;
views_per_day = FOREACH by_day GENERATE
    group AS date,
    SUM(logs.page_views) AS total_views;

DUMP views_per_hour_day;
DUMP views_per_day;
```

Run:
```bash
pig -x mapreduce /home/cloudera/cbp/simple_logs.pig
```

---

## Troubleshooting

### `ERROR 2999: Unexpected internal error. null`
Usually a typo in field names or mismatch in schema. Recheck field count in your CSV vs. the `AS` clause.

### Output has strange characters like `()`
Your data has empty strings in a field. Filter them out:
```pig
customers = FILTER customers BY name IS NOT NULL;
```

### Script runs but output is empty
You probably forgot to `STORE`. Just defining relations doesn't run anything — Pig is lazy.

### `Output Location Validation Failed: Output directory already exists`
Delete it: `hadoop fs -rm -r <path>`.

---

## Checklist Before Moving On

- [ ] Pig script `gender_stats.pig` ran successfully
- [ ] Output file in HDFS: `/user/cloudera/cbp/output/pig_gender_stats/part-r-00000`
- [ ] Output contains gender-grouped stats
- [ ] (Optional) Word count and log analysis scripts tried
- [ ] Screenshots saved for the report

Next: `06-mapreduce-processing.md`.
