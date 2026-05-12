# 01 — Cloudera Setup & Verification

## Objective

Start the Cloudera QuickStart VM, log in, and verify all the tools you need (Hadoop, Hive, Pig, Sqoop, MySQL) are installed and working.

---

## Why This Step Matters

Cloudera QuickStart VM comes pre-loaded with a full Hadoop stack. You do NOT need to install anything. But services need to be running and you need to know how to open a terminal and use it.

If any tool fails the verification, fix it here — do NOT proceed, because later steps will silently fail.

---

## Step 1.1 — Boot the VM

1. Open VirtualBox / VMware
2. Start the `cloudera-quickstart` VM
3. Wait 2-3 minutes for all services to start (NameNode, DataNode, ResourceManager, HiveServer2, etc.)
4. The desktop will load with Firefox and a terminal icon visible

**Default credentials:**
- Username: `cloudera`
- Password: `cloudera`
- Root password: `cloudera`

---

## Step 1.2 — Open a Terminal

Click the black terminal icon on the top toolbar (or right-click desktop → "Open Terminal").

Your prompt should look like:
```
[cloudera@quickstart ~]$
```

You are now logged in as user `cloudera` in the home directory `/home/cloudera/`.

---

## Step 1.3 — Verify Hadoop

```bash
hadoop version
```

**Expected output (something like):**
```
Hadoop 2.6.0-cdh5.x.x
Subversion ...
Compiled by ...
```

Then verify HDFS is up:
```bash
hadoop fs -ls /
```

**Expected:** A list of directories like `/user`, `/tmp`, `/var` with no error.

If you get a connection error, HDFS NameNode is not running. Restart the VM.

---

## Step 1.4 — Verify Hive

```bash
hive --version
```

**Expected:**
```
Hive 1.1.0-cdh5.x.x
```

Quick smoke test — open Hive and exit:
```bash
hive
```
You will see the `hive>` prompt. Type:
```sql
SHOW DATABASES;
```
You should see at least `default`. Exit with:
```sql
exit;
```

---

## Step 1.5 — Verify Pig

```bash
pig -version
```

**Expected:**
```
Apache Pig version 0.12.0-cdh5.x.x
```

Smoke test:
```bash
pig
```
You will see the `grunt>` prompt. Exit with:
```
quit;
```

---

## Step 1.6 — Verify Sqoop

```bash
sqoop version
```

**Expected:**
```
Sqoop 1.4.6-cdh5.x.x
```

---

## Step 1.7 — Verify MySQL

Cloudera VM ships with MySQL running.

```bash
mysql -u root -p
```

When prompted, enter password: `cloudera`

**Expected:** You land at the `mysql>` prompt.
```sql
SHOW DATABASES;
```
You should see default databases like `information_schema`, `mysql`, `hive`, etc.

Exit:
```sql
exit;
```

---

## Step 1.8 — Verify Web UIs (Optional but Useful)

Open Firefox inside the VM:

| Service | URL | What you see |
|---------|-----|--------------|
| HDFS NameNode | http://localhost:50070 | Cluster overview, file browser |
| YARN ResourceManager | http://localhost:8088 | Running and finished jobs |
| Hue (web dashboard) | http://localhost:8888 | All tools in one UI (login: cloudera / cloudera) |

These are useful for screenshots in your report.

---

## Troubleshooting

### "Connection refused" errors
Services didn't start. Run:
```bash
sudo /home/cloudera/cloudera-manager --force --express
```
Or restart the VM.

### VM is slow / hangs
Increase RAM allocation in VM settings (close VM first). 8 GB is comfortable.

### `mysql: command not found`
Rare. Install: `sudo yum install mysql mysql-server -y`

---

## Checklist Before Moving On

- [ ] `hadoop version` works
- [ ] `hadoop fs -ls /` returns a directory listing
- [ ] `hive` shell opens and `SHOW DATABASES` works
- [ ] `pig` opens the grunt shell
- [ ] `sqoop version` works
- [ ] `mysql -u root -p` (password: cloudera) logs in

All checked? Good. Open `02-hdfs-basics.md`.
