# 06 — MapReduce: Parallel Processing from Scratch

## Objective

Understand MapReduce from first principles, then run two MapReduce programs:
1. Classic WordCount (using Cloudera's pre-built example JAR)
2. A custom Java MapReduce program that counts customers per gender (matches the PDF's UserInteractionCount example)

---

## First Principles: What Is MapReduce?

**MapReduce is a two-phase programming model for parallel computation on large datasets.**

### The Core Idea

You have a terabyte of data, one machine can't process it fast, so you split the work:

1. **MAP phase**
   - Each machine reads its chunk of data
   - For each record, emits zero or more `(key, value)` pairs
   - Output is shuffled so all pairs with the same key end up on the same machine

2. **REDUCE phase**
   - For each unique key, a reducer receives all its values
   - It aggregates them (sum, count, list, etc.) and emits a final result

### WordCount Example

Input:
```
hello world
hello hadoop
```

**Map output** (each mapper emits one pair per word):
```
(hello, 1)
(world, 1)
(hello, 1)
(hadoop, 1)
```

**Shuffle** groups by key:
```
hello → [1, 1]
world → [1]
hadoop → [1]
```

**Reduce output** (sum values for each key):
```
(hello, 2)
(world, 1)
(hadoop, 1)
```

### Why Bother?

This pattern is **embarrassingly parallel** — each mapper works independently on its chunk. Double the machines, halve the time. Combined with HDFS (which stores data on the same machines), you get data-local computation: the code runs where the data already lives.

### Why Not Always Use MapReduce?

- Writing Java MapReduce is verbose — that's why we have Hive and Pig.
- But for learning and for custom algorithms that don't fit SQL/Pig, MapReduce is still used.

---

## Part A — WordCount Using the Pre-built Example JAR

Fastest way to see MapReduce in action. Cloudera ships example JARs.

### Step 6A.1 — Locate the Examples JAR

```bash
ls /usr/lib/hadoop-mapreduce/hadoop-mapreduce-examples*.jar
```

You should see something like:
```
/usr/lib/hadoop-mapreduce/hadoop-mapreduce-examples.jar
```

### Step 6A.2 — Prepare a Text File in HDFS

We'll use your customer CSV — but you can use any text file.

```bash
# If you need to re-upload
hadoop fs -mkdir -p /user/cloudera/cbp/input
hadoop fs -put -f /home/cloudera/cbp/customer_data.csv /user/cloudera/cbp/input/
```

Clear the output dir:
```bash
hadoop fs -rm -r /user/cloudera/cbp/output/mr_wordcount
```

### Step 6A.3 — Run WordCount

```bash
hadoop jar /usr/lib/hadoop-mapreduce/hadoop-mapreduce-examples.jar \
    wordcount \
    /user/cloudera/cbp/input/customer_data.csv \
    /user/cloudera/cbp/output/mr_wordcount
```

Watch for progress:
```
map 0% reduce 0%
map 100% reduce 0%
map 100% reduce 100%
Job ... completed successfully
```

### Step 6A.4 — View Results

```bash
hadoop fs -ls /user/cloudera/cbp/output/mr_wordcount
hadoop fs -cat /user/cloudera/cbp/output/mr_wordcount/part-r-00000
```

You'll see each word (with CSV tokens) and its count.

**Screenshot this output for the report.**

---

## Part B — Custom Java MapReduce (Customer Count by Gender)

This mirrors the `UserInteractionCount` class in your project PDF, but adapted for our customer data.

### Step 6B.1 — Create a Working Directory

```bash
mkdir -p /home/cloudera/cbp/mr_custom
cd /home/cloudera/cbp/mr_custom
```

### Step 6B.2 — Write the Java Files

Create `CustomerGenderCount.java`:
```bash
nano CustomerGenderCount.java
```

Paste:
```java
import java.io.IOException;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

public class CustomerGenderCount {

    public static class GenderMapper
            extends Mapper<LongWritable, Text, Text, IntWritable> {

        private final static IntWritable ONE = new IntWritable(1);
        private Text gender = new Text();

        @Override
        public void map(LongWritable key, Text value, Context context)
                throws IOException, InterruptedException {
            // value = one CSV line: "1,Alice,30,Female,150.00,2024-01-01"
            String line = value.toString();
            String[] fields = line.split(",");
            if (fields.length >= 4) {
                gender.set(fields[3].trim());
                context.write(gender, ONE);
            }
        }
    }

    public static class GenderReducer
            extends Reducer<Text, IntWritable, Text, IntWritable> {

        @Override
        public void reduce(Text key, Iterable<IntWritable> values, Context context)
                throws IOException, InterruptedException {
            int sum = 0;
            for (IntWritable v : values) {
                sum += v.get();
            }
            context.write(key, new IntWritable(sum));
        }
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 2) {
            System.err.println("Usage: CustomerGenderCount <input> <output>");
            System.exit(-1);
        }

        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "Customer Gender Count");
        job.setJarByClass(CustomerGenderCount.class);

        job.setMapperClass(GenderMapper.class);
        job.setCombinerClass(GenderReducer.class);  // optimization
        job.setReducerClass(GenderReducer.class);

        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(IntWritable.class);

        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));

        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }
}
```

### Step 6B.3 — Compile

```bash
# Compile to class files
hadoop com.sun.tools.javac.Main CustomerGenderCount.java

# Package into a JAR
jar cf customer_gender_count.jar *.class
```

Verify:
```bash
ls -la
```

You should see `.class` files and `customer_gender_count.jar`.

### Step 6B.4 — Run

Clean previous output:
```bash
hadoop fs -rm -r /user/cloudera/cbp/output/mr_gender_count
```

Run:
```bash
hadoop jar customer_gender_count.jar CustomerGenderCount \
    /user/cloudera/cbp/input/customer_data.csv \
    /user/cloudera/cbp/output/mr_gender_count
```

### Step 6B.5 — View Results

```bash
hadoop fs -cat /user/cloudera/cbp/output/mr_gender_count/part-r-00000
```

**Expected:**
```
Female   2
Male     3
```

**Screenshot this for the report** — this is your custom MapReduce output.

---

## Part C — Most Frequent Words (Syllabus Point 2B)

Syllabus asks you to take WordCount output and find the most frequent words. Quick way with Linux:
```bash
hadoop fs -cat /user/cloudera/cbp/output/mr_wordcount/part-r-00000 | sort -k2 -n -r | head -5
```
The `sort -k2 -n -r` sorts by column 2 numerically in reverse (descending).

If you want a pure MapReduce solution, you'd write a second job that takes the first job's output as input and emits `(count, word)` pairs so the shuffle phase sorts them. For the project, the bash post-processing above is fine and demonstrates the concept.

---

## Step 6.6 — Check Job History (For Screenshots)

Open the YARN ResourceManager UI in Firefox inside the VM:
```
http://localhost:8088
```

You'll see your submitted jobs with status, duration, counters (input records read, output records written). **Screenshot** a successful job page — it's great for the report.

---

## Troubleshooting

### `hadoop: command not found` when compiling
Use the full path: `/usr/bin/hadoop com.sun.tools.javac.Main ...` — or verify `$PATH` has `/usr/bin`.

### `ClassNotFoundException` during `hadoop jar`
- Make sure the class name in the command matches the class name in the file (case-sensitive).
- Make sure the JAR actually contains the class: `jar tf customer_gender_count.jar` — should list `CustomerGenderCount.class`.

### "Output directory already exists"
Delete it before running: `hadoop fs -rm -r <output_path>`.

### Job runs but output file is empty
Your mapper isn't emitting anything. Check the CSV parsing — are fields really comma-separated? Does `fields.length >= 4` hold? Add debug prints via `context.getCounter(...)` to diagnose.

### "NoClassDefFoundError: org/apache/hadoop/..."
You're running `java CustomerGenderCount` directly. Must run via `hadoop jar` so Hadoop libraries are on classpath.

---

## Checklist Before Moving On

- [ ] WordCount example JAR ran successfully
- [ ] You understand map → shuffle → reduce conceptually
- [ ] Custom Java MapReduce compiled and ran
- [ ] Output at `/user/cloudera/cbp/output/mr_gender_count/part-r-00000` shows gender counts
- [ ] Screenshot of YARN job history captured

Next: `07-final-integration.md`.
