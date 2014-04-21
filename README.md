最短経路問題を解くプログラムとその Web インタフェース
使用言語は Python
データ: /works/csisv13/torotoki/data/train_line/json

## 使い方

### キャッシュファイルの作成

```
$ cd stem
$ python
from stem import Stem
calc = Stem()
calc.add_folder("/works/csisv13/torotoki/data/train_line/json")
```
上記を実行すると `matrix_cache.mat` というファイルがカレントディレクトリにできる

### 動作確認

```
from stem import Stem
calc = Stem(cache='matrix_cache')
calc.add_folder("/works/csisv13/torotoki/data/train_line/json")

import datetime
start_time = datetime.time(12, 30)
A = self.calc.nearest_node(u"渋谷", start_time)
print self.calc.shortest_path(A, u"新宿")
```

## 既知の問題点
* 電車の出発ノードと着ノードを分けていないため、コードが若干煩雑になっている
* 休日のダイア変更、特殊なダイア変更
