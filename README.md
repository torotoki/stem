# STEM
STEM is a python library of Shortest Path Problem Solver for large scale graphs of timetable, includes an implementation of Dijkstra's algorithm for large scale time-dependent network.

## Usage

### Making cache file

```
$ cd stem
$ python
from stem import Stem
calc = Stem()
calc.add_folder("data/train_line/json")
```
You have to make a cache file with below before solving a problem. The code makes a file named `matrix_cache.mat` in the current directory.

### Example

```
from stem import Stem
calc = Stem(cache='matrix_cache')
calc.add_folder("data/train_line/json")

import datetime
start_time = datetime.time(12, 30)
A = self.calc.nearest_node(u"渋谷", start_time)
print self.calc.shortest_path(A, u"新宿")
```

### Input File Format
coming soon


## Known issue
* The part of code reading timetable is complex for the moment because departure node and arrival node of a train is not separated.


## License

STEM is licensed under the [GNU General Public
License](http://www.gnu.org/licenses/gpl-2.0.html) (v2 or later).
Note that this is the /full/ GPL, which allows many free uses, but not
its use in distributed [proprietary
software](http://www.gnu.org/licenses/gpl-faq.html#GPLInProprietarySystem).
