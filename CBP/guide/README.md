# CBP Implementation Guide — Client Intelligence Center

Step-by-step guide to implement the Hadoop ecosystem project on Cloudera QuickStart VM.

## Read in Order

| # | File | Topic |
|---|------|-------|
| 0 | [00-overview.md](00-overview.md) | Big picture, pipeline diagram, first principles |
| 1 | [01-cloudera-setup.md](01-cloudera-setup.md) | Boot VM, verify all tools work |
| 2 | [02-hdfs-basics.md](02-hdfs-basics.md) | HDFS commands, upload customer data |
| 3 | [03-sqoop-mysql-import.md](03-sqoop-mysql-import.md) | MySQL → HDFS with Sqoop |
| 4 | [04-hive-querying.md](04-hive-querying.md) | Hive tables + the key GROUP BY query |
| 5 | [05-pig-transformation.md](05-pig-transformation.md) | Pig Latin scripts for transformations |
| 6 | [06-mapreduce-processing.md](06-mapreduce-processing.md) | Java MapReduce from scratch |
| 7 | [07-final-integration.md](07-final-integration.md) | End-to-end run + screenshots for report |
| 8 | [08-troubleshooting.md](08-troubleshooting.md) | Common errors and fixes |

## How to Use This Guide

1. Open each file in order.
2. Run the commands. Read the "First Principles" sections — they explain **why**, not just **how**.
3. At the end of each step there's a **checklist**. Don't move on until every box is checked.
4. If something breaks, jump to `08-troubleshooting.md`.
5. Stuck or confused? Ask, and I'll walk you through that specific step in more depth.

## Key Deliverable

The target query — this must work:
```sql
SELECT gender, AVG(purchase_amount) AS avg_purchase
FROM customer_data_hive
GROUP BY gender;
```
Output: `Female 165.0`, `Male 250.5` (or `Female 150.0`, `Male 250.625` if using only the 3 rows from the PDF).

## Time Budget

Active time ~2 hours if nothing breaks. Add buffer for first-time issues — probably 3–4 hours total.
