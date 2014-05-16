# STEM
Shortest Path Problem Solver for large scale graphs and timetable with Dijkstra's algorithm

---

This library includes an implementation of Dijkstra's algorithm and large scale time-dependent network for timetable of train, wrote in Python.

## Usage

### Making cache file

```
$ cd stem
$ python
from stem import Stem
calc = Stem()
calc.add_folder("data/train_line/json")
```
You have to make a cache file with below before solving a problem. The code makes a file named `matrix_cache.mat` in current directory.

### Example

```
from stem import Stem
calc = Stem(cache='matrix_cache')
calc.add_folder("/works/csisv13/torotoki/data/train_line/json")

import datetime
start_time = datetime.time(12, 30)
A = self.calc.nearest_node(u"渋谷", start_time)
print self.calc.shortest_path(A, u"新宿")
```

### Input File Format
coming soon

## Known issue

* The part of code reading timetable is complex codes for now, because it is not separated departure and arrival node of train
