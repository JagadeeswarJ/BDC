# Set 2 — MapReduce: Word Frequency Count

## What MapReduce Does

Three phases process data in parallel:

```
Input → MAP (emit word,1) → SHUFFLE/SORT (group by word) → REDUCE (sum) → Output
```

We write the mapper and reducer in **Python**. Hadoop runs them using its built-in **Streaming** utility — no Java needed.

---

## The Problem

Count the frequency of each word (case-insensitive) in:

```
Bus, Car, bus, car, train, car, bus, car, train, bus, TRAIN,BUS, buS, caR, CAR, car, BUS, TRAIN
```

Expected output:
```
bus     7
car     7
train   4
```

---

## Step 1 — Create the Input File

```bash
nano words.txt
```
Paste this line:
```
Bus, Car, bus, car, train, car, bus, car, train, bus, TRAIN,BUS, buS, caR, CAR, car, BUS, TRAIN
```
Save: `Ctrl+O` → Enter → `Ctrl+X`

---

## Step 2 — Create mapper.py

```bash
nano mapper.py
```
Paste:
```python
import sys, re

for line in sys.stdin:
    for word in re.split(r'[,\s]+', line.lower().strip()):
        if word:
            print(word + "\t1")
```
Save: `Ctrl+O` → Enter → `Ctrl+X`

**What it does:** reads each line → lowercase → split on commas/spaces → print `word\t1` for each token.

---

## Step 3 — Create reducer.py

```bash
nano reducer.py
```
Paste:
```python
import sys
from collections import defaultdict

counts = defaultdict(int)
for line in sys.stdin:
    word, _ = line.strip().split('\t')
    counts[word] += 1

for word, cnt in counts.items():
    print(word + "\t" + str(cnt))
```
Save: `Ctrl+O` → Enter → `Ctrl+X`

**What it does:** reads `word\t1` lines → sums count per word → prints `word\ttotal`.

---

## Step 4 — Upload Input to HDFS

```bash
hadoop fs -mkdir -p /user/cloudera/wc/input
hadoop fs -put words.txt /user/cloudera/wc/input/
```

---

## Step 5 — Run the MapReduce Job

```bash
hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
  -input   /user/cloudera/wc/input \
  -output  /user/cloudera/wc/output \
  -mapper  mapper.py \
  -reducer reducer.py \
  -file    mapper.py \
  -file    reducer.py
```

> `hadoop-streaming.jar` is a **pre-installed Hadoop tool** — you don't write or compile it. It acts as a bridge that feeds HDFS data into your Python scripts via stdin/stdout, exactly like a shell pipe.
>
> `-file mapper.py` and `-file reducer.py` tell Hadoop to ship your local Python files to the cluster nodes before the job starts.

---

## Step 6 — View the Result

```bash
hadoop fs -cat /user/cloudera/wc/output/part-00000
```

**Expected:**
```
bus     7
car     7
train   4
```

If you need to re-run, delete the output folder first:
```bash
hadoop fs -rm -r /user/cloudera/wc/output
```

---

## How Each Part Works

**Mapper** — gets one line at a time from stdin. Lowercases it, splits on commas and spaces, emits `word\t1` for every token.

**Shuffle/Sort** — done automatically by Hadoop. Groups all the `1`s by key: `bus → [1,1,1,1,1,1,1]`.

**Reducer** — gets the grouped lines from stdin. Adds up the counts and prints the total.

---

## Things to Remember

- `line.lower()` — makes it case-insensitive (`Bus` and `bus` both become `bus`).
- `re.split(r'[,\s]+', ...)` — splits on commas **and** spaces (plain `split()` misses commas).
- `\t` is the key-value separator — mapper emits `word\t1`, reducer reads `word\t1`.
- Output dir must **not exist** before running — Hadoop refuses to overwrite.
- The `.jar` in the run command is Hadoop's own streaming tool, not your code.
- Phases: **Map → Shuffle/Sort → Reduce** — Shuffle is automatic, you never write it.
