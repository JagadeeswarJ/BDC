# Set 2 — MapReduce: Word Frequency Count

## What MapReduce Does

Three phases process data in parallel across a cluster:

```
Input file → MAP (emit word,1) → SHUFFLE/SORT (group by word) → REDUCE (sum) → Output
```

---

## The Problem

Count the frequency of each word (case-insensitive) in the given data:

```
Bus, Car, bus, car, train, car, bus, car, train, bus, TRAIN,BUS, buS, caR, CAR, car, BUS, TRAIN
```

Expected output (after lowercasing everything):
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
Paste exactly:
```
Bus, Car, bus, car, train, car, bus, car, train, bus, TRAIN,BUS, buS, caR, CAR, car, BUS, TRAIN
```
Save: `Ctrl+O`, Enter, `Ctrl+X`.

Upload to HDFS:
```bash
hadoop fs -mkdir -p /user/cloudera/wc/input
hadoop fs -put words.txt /user/cloudera/wc/input/
```

---

## Step 2 — Java Code: `WordCount.java`

```java
import java.io.IOException;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

public class WordCount {

  public static class TokenMapper extends Mapper<Object, Text, Text, IntWritable> {
    private final IntWritable one = new IntWritable(1);
    private Text word = new Text();

    public void map(Object key, Text value, Context ctx) throws IOException, InterruptedException {
      // split on commas and whitespace, lowercase everything
      String[] tokens = value.toString().toLowerCase().split("[,\\s]+");
      for (String token : tokens) {
        if (!token.isEmpty()) {
          word.set(token);
          ctx.write(word, one);
        }
      }
    }
  }

  public static class SumReducer extends Reducer<Text, IntWritable, Text, IntWritable> {
    public void reduce(Text key, Iterable<IntWritable> vals, Context ctx) throws IOException, InterruptedException {
      int sum = 0;
      for (IntWritable v : vals) sum += v.get();
      ctx.write(key, new IntWritable(sum));
    }
  }

  public static void main(String[] args) throws Exception {
    Job job = Job.getInstance(new Configuration(), "wordcount");
    job.setJarByClass(WordCount.class);
    job.setMapperClass(TokenMapper.class);
    job.setReducerClass(SumReducer.class);
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(IntWritable.class);
    FileInputFormat.addInputPath(job, new Path(args[0]));
    FileOutputFormat.setOutputPath(job, new Path(args[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
```

---

## Step 3 — Compile, Package, Run

```bash
# Compile
javac -classpath $(hadoop classpath) -d wc_classes WordCount.java

# Package into a JAR
jar -cvf wc.jar -C wc_classes/ .

# Run on HDFS
hadoop jar wc.jar WordCount /user/cloudera/wc/input /user/cloudera/wc/output

# View result
hadoop fs -cat /user/cloudera/wc/output/part-r-00000
```

**Expected output:**
```
bus     7
car     7
train   4
```

To re-run, delete old output first:
```bash
hadoop fs -rm -r /user/cloudera/wc/output
```

---

## How Each Part Works

**Mapper** — reads one line, lowercases it, splits on commas and spaces using regex `[,\\s]+`, emits `(word, 1)` for each token.

**Shuffle/Sort** — automatic. Framework groups all `1`s by key: `bus → [1,1,1,1,1,1,1]`, `car → [1,1,1,1,1,1,1]`, `train → [1,1,1,1]`.

**Reducer** — sums the list for each key and emits `(word, total)`.

---

## Things to Remember

- **Case-insensitive**: use `.toLowerCase()` in the mapper, otherwise Bus and bus are counted separately.
- **Comma handling**: the data has commas, so use `split("[,\\s]+")` not `StringTokenizer` (which only splits on whitespace).
- Output directory **must not exist** — Hadoop refuses to overwrite. Delete before re-running.
- `Text` = Hadoop's String, `IntWritable` = Hadoop's int. They are serializable for network transfer.
- Phases: **Map → Shuffle/Sort → Reduce** (Shuffle is automatic, you don't write it).
