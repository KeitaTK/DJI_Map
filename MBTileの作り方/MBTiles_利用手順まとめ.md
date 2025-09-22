# 国土地理院航空写真タイルのダウンロードとMBTiles利用手順

## 1. 航空写真タイルのダウンロード

`download_Map.py` を使って、指定範囲の航空写真タイルをダウンロードします。

```sh
python download_Map.py
```

- デフォルトで `gsi_aerial_photos/zoom_XX/tile_X_Y.jpg` 形式で保存されます。
- ダウンロード範囲やズームレベルは `download_Map.py` 内のパラメータで調整可能です。

---

## 2. MBTilesファイルの作成

ダウンロードしたタイル画像をMBTiles形式に変換します。

```sh
python make_Mbtiles.py --tiles-dir gsi_aerial_photos --mbtiles output.mbtiles
```

- `gsi_aerial_photos` ディレクトリ内のタイルを `output.mbtiles` にまとめます。
- 必要パッケージ: `mercantile`, `click`, `sqlite3`

---

## 3. MBTilesファイルのローカル配信

`map_1.py` を使ってMBTilesファイルをローカルサーバで配信し、地図表示やクリック座標取得ができます。

```sh
python map_1.py
```

- ブラウザで [http://localhost:5000/](http://localhost:5000/) にアクセス
- 地図上をクリックすると、クリックした緯度経度がPythonコンソールに出力されます
- MBTilesファイル名は `map_1.py` の `MBTILES_PATH` で切り替え可能

---

## 4. ファイル構成例

```
gsi_aerial_photos/
  zoom_14/
    tile_14406_6429.jpg
    ...
output.mbtiles
download_Map.py
make_Mbtiles.py
map_1.py
```

---

## 5. 注意点

- MBTiles作成時、Y座標の反転（XYZ→TMS変換）が必要です（スクリプト内で自動処理）。
- サーバ起動後、タイル取得は `/tiles/{z}/{x}/{y}.png` でアクセスされます。
- 必要なPythonパッケージは事前にインストールしてください。

---

## 参考

- [`download_Map.py`](download_Map.py)
- [`make_Mbtiles.py`](make_Mbtiles.py)
- [`map_1.py`](map_1.py)