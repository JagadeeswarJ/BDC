# 02 — HDFS: Storing Data in the Distributed Filesystem

## Objective

Create your customer dataset locally, then move it into HDFS so downstream tools (Hive, Pig, MapReduce) can read it.

---

## First Principles: What Is HDFS?

**HDFS = Hadoop Distributed File System**

Imagine your laptop's 1 TB SSD. Now imagine you need to store 1 PB (1000 TB). No single disk can hold that. HDFS solves this by:

1. **Splitting** a large file into fixed-size blocks (default: **128 MB**)
2. **Distributing** those blocks across many machines (DataNodes)
3. **Replicating** each block 3 times (default) so if a machine dies, the data is safe
4. **Tracking** which block is where via a central index (the NameNode)

You interact with HDFS through a Unix-like command interface: `hadoop fs -ls`, `-mkdir`, `-put`, `-cat`, etc. Same commands as Linux, different prefix.

On your single-machine Cloudera VM, HDFS is still there — it just runs all components on one machine for learning.

---

## The Two Filesystems (Again)

Keep this diagram in your head:

```
Your VM has TWO filesystems:

Linux filesystem              HDFS
/home/cloudera/               /user/cloudera/
  customer_data.csv             customer_data/
                                  customer_data.csv
  
You reach it with:           You reach it with:
  ls, cat, nano                 hadoop fs -ls, -cat, etc.
```

---

## Step 2.1 — Create Working Directory Locally

```bash
mkdir -p /home/cloudera/cbp
cd /home/cloudera/cbp
pwd
```

**Expected:** `/home/cloudera/cbp`

This is where we keep local files before uploading to HDFS.

---

## Step 2.2 — Create the Customer Data CSV

```bash
nano customer_data.csv
```

Paste this content:
```
1,Alice,30,Female,150.00,2024-01-01
2,Bob,25,Male,200.50,2024-02-15
3,Charlie,35,Male,300.75,2024-03-20
4,Diana,28,Female,180.00,2024-04-10
5,Ethan,40,Male,250.25,2024-05-05
```

Save and exit: `Ctrl+O`, `Enter`, `Ctrl+X`.

Verify:
```bash
cat customer_data.csv
wc -l customer_data.csv
```

**Expected:** 5 lines.

> Note: I added 2 extra rows (Diana, Ethan) beyond what the PDF shows so your GROUP BY gender result has a proper average calculation (Male average = (200.50+300.75+250.25)/3 = 250.50, Female average = (150+180)/2 = 165).
> If you want to exactly match the PDF's expected output (Female 150.00, Male 250.625), use ONLY the first three rows. Your call — either works.

---

## Step 2.3 — HDFS Command Basics

Before uploading, learn these 6 commands. You will use them constantly:

| Command | Purpose | Linux equivalent |
|---------|---------|------------------|
| `hadoop fs -ls <path>` | List files in HDFS directory | `ls` |
| `hadoop fs -mkdir -p <path>` | Create HDFS directory (with parents) | `mkdir -p` |
| `hadoop fs -put <local> <hdfs>` | Upload local file to HDFS | (upload) |
| `hadoop fs -get <hdfs> <local>` | Download HDFS file to local | (download) |
| `hadoop fs -cat <hdfs_path>` | Print file contents | `cat` |
| `hadoop fs -rm -r <path>` | Delete file/dir from HDFS | `rm -r` |

**Important:** `hadoop fs` and `hdfs dfs` do the same thing. Use either.

---

## Step 2.4 — Explore HDFS

See what's already there:
```bash
hadoop fs -ls /
hadoop fs -ls /user
hadoop fs -ls /user/cloudera
```

If `/user/cloudera` doesn't exist, create it:
```bash
hadoop fs -mkdir -p /user/cloudera
```

---

## Step 2.5 — Create the Project Directory Structure in HDFS

```bash
hadoop fs -mkdir -p /user/cloudera/cbp/input
hadoop fs -mkdir -p /user/cloudera/cbp/output
```

Verify:
```bash
hadoop fs -ls /user/cloudera/cbp
```

**Expected:**
```
Found 2 items
drwxr-xr-x   - cloudera cloudera          0 ... /user/cloudera/cbp/input
drwxr-xr-x   - cloudera cloudera          0 ... /user/cloudera/cbp/output
```

---

## Step 2.6 — Upload the CSV to HDFS

```bash
hadoop fs -put /home/cloudera/cbp/customer_data.csv /user/cloudera/cbp/input/
```

Verify upload:
```bash
hadoop fs -ls /user/cloudera/cbp/input/
hadoop fs -cat /user/cloudera/cbp/input/customer_data.csv
```

**Expected:** The CSV contents you created in Step 2.2.

---

## Step 2.7 — Inspect File Properties (Bonus)

```bash
hadoop fs -du -h /user/cloudera/cbp/input/
hadoop fs -stat "%b bytes, replication=%r, block=%o" /user/cloudera/cbp/input/customer_data.csv
```

This gives you file size, replication factor, and block size. Useful for the report.

---

## Step 2.8 — Download from HDFS Back to Local (Just to Practice)

```bash
hadoop fs -get /user/cloudera/cbp/input/customer_data.csv /home/cloudera/cbp/downloaded_copy.csv
diff /home/cloudera/cbp/customer_data.csv /home/cloudera/cbp/downloaded_copy.csv
```

**Expected:** No output from `diff` → files are identical (round-trip worked).

Delete the test download:
```bash
rm /home/cloudera/cbp/downloaded_copy.csv
```

---

## Step 2.9 — View via Web UI (For Screenshots)

Open Firefox inside VM:
```
http://localhost:50070
```

Click **"Utilities" → "Browse the file system"** → navigate to `/user/cloudera/cbp/input/`.

You can see your file, its blocks, replication, and size. **Take a screenshot** — it's good for the report.

---

## Checklist Before Moving On

- [ ] Local file exists: `/home/cloudera/cbp/customer_data.csv`
- [ ] HDFS directories exist: `/user/cloudera/cbp/input` and `/user/cloudera/cbp/output`
- [ ] File uploaded: `hadoop fs -cat /user/cloudera/cbp/input/customer_data.csv` shows data
- [ ] You understand the difference between local and HDFS paths

Next: `03-sqoop-mysql-import.md`.
