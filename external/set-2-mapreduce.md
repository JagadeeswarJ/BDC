# Set 2 — MapReduce: Word Count

## What MapReduce Is — and Why It Works

Counting words in a 10 GB text file on one machine takes hours. **MapReduce** spreads that work across many machines using three phases:

```
Input file in HDFS
       │
       ▼
  ┌──────────┐
  │   MAP    │   each mapper reads its block,
  │          │   emits (word, 1) for every word
  └────┬─────┘
       │  (hello,1) (world,1) (hello,1) (data,1) ...
       ▼
  ┌──────────┐
  │ SHUFFLE  │   framework groups values by key
  │  + SORT  │
  └────┬─────┘
       │  hello → [1,1]   world → [1]   data → [1]
       ▼
  ┌──────────┐
  │  REDUCE  │   each reducer sums its key's values
  │          │
  └────┬─────┘
       │
       ▼
  Output in HDFS: hello 2, world 1, data 1
```

The genius is that **Map runs in parallel on each block where it lives** (data locality), and the Shuffle phase moves only the small intermediate keys, not the raw input.

---

## Develop a MapReduce Program to Count Word Occurrences

### Minimal Java Code — `WordCount.java`

```java
import java.io.IOException;
import java.util.StringTokenizer;
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
      StringTokenizer it = new StringTokenizer(value.toString());
      while (it.hasMoreTokens()) {
        word.set(it.nextToken());
        ctx.write(word, one);
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

### Compile, Package, Run

```bash
# Compile
javac -classpath $(hadoop classpath) -d wc_classes WordCount.java
jar -cvf wc.jar -C wc_classes/ .

# Prepare input
echo "hello world hello hadoop big data hadoop" > input.txt
hadoop fs -mkdir -p /user/cloudera/wc/input
hadoop fs -put input.txt /user/cloudera/wc/input/

# Run
hadoop jar wc.jar WordCount /user/cloudera/wc/input /user/cloudera/wc/output

# View result
hadoop fs -cat /user/cloudera/wc/output/part-r-00000
```

**Expected output:**
```
big     1
data    1
hadoop  2
hello   2
world   1
```

---

## How Each Piece Works

### The Mapper
- Hadoop's `TextInputFormat` (default) hands each line of the input to `map()` as a `Text` value (the key is the byte offset, which we ignore).
- `StringTokenizer` splits the line on whitespace.
- For each token we emit `(word, 1)`. This is the heart of the "Map" step: emit a key for every observation, with a value of 1.

### The Shuffle (free, automatic)
- The framework gathers all `(word, 1)` pairs across all mappers, sorts them by key, and groups them.
- All `1`s for `"hello"` end up at the same reducer.

### The Reducer
- For each unique key, `reduce()` is called once with an iterable of all its values.
- We loop through and sum — that gives the count.
- We emit `(word, total_count)`.

### The `main` Driver
- Builds a `Job`, points it at the Mapper/Reducer classes and the input/output paths, and submits it to YARN.
- **Output path must NOT exist beforehand** — Hadoop creates it and refuses to overwrite (a safety feature). Delete with `hadoop fs -rm -r /user/cloudera/wc/output` to re-run.

---

## Things to Remember

- Three phases: **Map → Shuffle/Sort → Reduce**.
- Mapper output types and Reducer input types **must match**.
- The Reducer is also a good **Combiner** for sum — set `job.setCombinerClass(SumReducer.class)` to add a mini-reduce on each mapper, cutting network traffic.
- `Text` and `IntWritable` are Hadoop's serializable replacements for `String` and `int`.
- Output filename is always `part-r-00000` (one file per reducer).
