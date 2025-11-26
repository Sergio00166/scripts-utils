# Python CPU Bench & Stress Test

A lightweight Python tool for **quick CPU benchmarking** and **CPU stress testing**.  
It uses multiprocessing and rendering-like workloads to keep all CPU cores busy.  

---

## ✨ Features
- **Benchmark mode** (`bench`)
  - Runs a simple single-core and multi-core test.
  - Prints results as "performance scores".
- **Stress test mode** (`stress`)
  - Loads all CPU cores indefinitely.
  - Useful for burn-in or testing system cooling.
- **How it burns the CPU**  
  - Repeatedly performs **rasterization-like computations**.  
  - Uses **multiprocessing** to fully saturate all available CPU cores.  
  - Workload involves lots of **integer math, copying, and array manipulation** to keep the CPU under constant pressure.

---

## 🖥️ Usage

### Stress Test (default)
Run without arguments to start a CPU stress test:

```bash
python cpu_bench.py
```

or explicitly:

```bash
python cpu_bench.py stress
```

Stop anytime with **CTRL+C** or by pressing any key when prompted.

---

### Benchmark
Run a single-core and multi-core CPU performance test:

```bash
python cpu_bench.py bench
```

## ⚠️ Notes
- **Not a precise benchmark** – Python’s execution speed varies between versions and implementations.  
- Stress mode will keep your CPU **at 100% usage** until stopped – ensure you have proper cooling.  
- The workload is designed to be **intentionally inefficient** so it can fully load CPUs regardless of architecture.

