# Set 1 — HDFS (Hadoop Distributed File System)

## What HDFS Is — and Why It Exists

A single hard drive can't hold or read terabytes fast. **HDFS** solves this by:

1. **Splitting** large files into fixed-size blocks (default 128 MB).
2. **Distributing** blocks across many machines (DataNodes).
3. **Replicating** each block 3 times for fault tolerance.
4. **Tracking** what's where via a master index (NameNode).

You interact with HDFS using Linux-like commands prefixed with `hadoop fs` (or `hdfs dfs` — both are equivalent).

### Two Filesystems, Always

```
LOCAL Linux FS                HDFS
/home/cloudera/file.txt       /user/cloudera/file.txt
ls, cat, nano                 hadoop fs -ls, -cat, -put, -get
```

Mixing the two is the #1 source of "file not found" errors. Local paths talk to your VM's disk; HDFS paths talk to Hadoop's distributed storage.

---

## A. Hadoop Storage File System

### I. Create directory structure in HDFS

```bash
hadoop fs -mkdir -p /user/cloudera/lab/input
```

**Working:**
- `-mkdir` makes a new HDFS directory.
- `-p` ("parents") creates intermediate folders silently if they don't exist — exactly like Linux `mkdir -p`. Without `-p`, missing parents cause an error.

### II. Move a file from local Linux → HDFS

```bash
hadoop fs -put sample.txt /user/cloudera/lab/input/
```

**Working:**
- `-put` copies the local `sample.txt` into the HDFS path.
- Behind the scenes, HDFS splits the file into blocks, sends blocks to DataNodes, and tells the NameNode where each block lives.
- Equivalent: `-copyFromLocal`. If you want to *move* (delete local after copying), use `-moveFromLocal`.

---

## B. Viewing Data Contents, Files and Directories

### a) See the contents (listing) of an HDFS directory

```bash
hadoop fs -ls /user/cloudera/lab/input
```

**Working:** Lists files inside the directory along with permissions, replication factor, owner, size, and modification time — analogous to `ls -l` in Linux.

### b) See the contents of a file present in HDFS

```bash
hadoop fs -cat /user/cloudera/lab/input/sample.txt
```

**Working:**
- `-cat` streams the file's bytes back to your terminal.
- For huge files use `-tail` (last 1 KB) or pipe: `hadoop fs -cat <file> | head`.

---

## C. Getting File Data From HDFS to Local Disk

### I. Copy file from HDFS to the local filesystem

```bash
hadoop fs -get /user/cloudera/lab/input/sample.txt /home/cloudera/sample.txt
```

**Working:**
- `-get` pulls the file out of HDFS and writes a regular Linux file at the local path.
- Internally, HDFS reads all the file's blocks from various DataNodes and stitches them back together for you.
- Equivalent: `-copyToLocal`.

---

## Minimum Cheat Sheet (Exam-Ready)

| Command | Purpose |
|---------|---------|
| `hadoop fs -mkdir -p <path>` | create HDFS dir |
| `hadoop fs -put <local> <hdfs>` | upload |
| `hadoop fs -ls <path>` | list |
| `hadoop fs -cat <file>` | view contents |
| `hadoop fs -get <hdfs> <local>` | download |

---

## Things to Remember

- `hadoop fs` and `hdfs dfs` are identical — either works.
- Default block size = **128 MB**, replication = **3**.
- The NameNode stores **metadata only** (file→block map). DataNodes hold the actual blocks.
- HDFS is **write-once, read-many** — you can append but not edit in the middle.
