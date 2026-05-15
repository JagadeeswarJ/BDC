# Set 1 — HDFS (Storage)

## What HDFS Is

HDFS splits large files into 128 MB blocks, distributes them across machines (DataNodes), and replicates each block 3 times. A central NameNode tracks which block lives where.

**Two filesystems — never mix them up:**
```
Local Linux FS            HDFS
/home/cloudera/file.txt   /user/cloudera/file.txt
ls, cat, nano             hadoop fs -ls, -cat, -put, -get
```

---

## A. Hadoop Storage File System

### I. Create directory structure in HDFS

```bash
hadoop fs -mkdir -p /user/cloudera/lab/input
```

- `-mkdir` creates an HDFS directory.
- `-p` creates any missing parent directories silently (like Linux `mkdir -p`).

---

### II. Move a file from local Linux → HDFS

```bash
hadoop fs -put sample.txt /user/cloudera/lab/input/
```

- `-put` copies the local file into HDFS.
- HDFS splits the file into blocks and distributes them to DataNodes.
- To also delete the local file after copying, use `-moveFromLocal` instead.

---

## B. Viewing Data Contents, Files and Directory

### a) See the contents (listing) of an HDFS directory

```bash
hadoop fs -ls /user/cloudera/lab/input
```

Shows permissions, replication factor, owner, size, and modification time — like `ls -l` in Linux.

### b) See the contents of a file in HDFS

```bash
hadoop fs -cat /user/cloudera/lab/input/sample.txt
```

Streams the file bytes to the terminal. For large files, pipe through `head`:
```bash
hadoop fs -cat /user/cloudera/lab/input/sample.txt | head
```

---

## C. Getting Files Data from HDFS to Local Disk

### I. Copy file from HDFS to the local filesystem

```bash
hadoop fs -get /user/cloudera/lab/input/sample.txt /home/cloudera/sample.txt
```

- `-get` pulls blocks from all DataNodes and reassembles the file locally.
- Equivalent: `-copyToLocal`.

---

## Things to Remember

- `hadoop fs` and `hdfs dfs` are identical — either works.
- Default block size = **128 MB**, replication factor = **3**.
- NameNode holds **metadata only**; DataNodes hold actual data blocks.
- HDFS is **write-once, read-many** — no in-place edits.
- `-put` = local→HDFS | `-get` = HDFS→local. Don't mix up the direction.
