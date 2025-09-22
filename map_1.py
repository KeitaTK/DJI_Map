#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MBTilesファイルをローカルサーバで配信し、
地図上でクリックした地点の緯度経度をPythonのコンソールに出力する例。

必要パッケージ:
    pip install flask folium
"""

from flask import Flask, send_file, abort, request, render_template_string
import sqlite3
import io
import logging
import functools

# Flaskアプリ初期化
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# 配信するMBTilesファイル名
# MBTILES_PATH = "地理院衛星写真オフライン.mbtiles"
MBTILES_PATH = "output.mbtiles"
# MBTILES_PATH = "地理院地図オフライン.mbtiles"

# タイル取得関数をキャッシュ
@functools.lru_cache(maxsize=1024)
def get_tile_from_db(z, x, y_mb):
    conn = sqlite3.connect(MBTILES_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT tile_data FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?",
        (z, x, y_mb)
    )
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

# タイルをSQLiteから読み出して返すエンドポイント
@app.route("/tiles/<int:z>/<int:x>/<int:y>.png")
def serve_tile(z, x, y):
    # MBTilesではY座標を反転する必要あり
    y_mb = (2 ** z - 1) - y
    tile_data = get_tile_from_db(z, x, y_mb)
    if not tile_data:
        abort(404)
    return send_file(io.BytesIO(tile_data), mimetype="image/png")

# 地図とクリック処理用HTMLを返すエンドポイント
@app.route("/")
def index():
    html = """
    <!DOCTYPE html>
    <html lang="ja">
      <head>
        <meta charset="utf-8" />
        <title>MBTilesクリック例</title>
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css"
        />
        <script src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js"></script>
      </head>
      <body>
        <div id="map" style="width:100%; height:100vh;"></div>
        <script>
          var map = L.map('map').setView([36.07, 136.55], 14);

          L.tileLayer('http://localhost:5000/tiles/{z}/{x}/{y}.png', {
            maxZoom: 18,
            attribution: 'Local MBTiles'
          }).addTo(map);

          // --- 使い方説明コントロール追加 ---
          var infoControl = L.control({position: 'topleft'});
          infoControl.onAdd = function(map) {
            var div = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
            div.style.background = 'white';
            div.style.padding = '6px 10px';
            div.style.marginTop = '40px';
            div.style.fontSize = '13px';
            div.innerHTML = '右クリックでポイント削除<br>ドラッグで移動';
            return div;
          };
          infoControl.addTo(map);
          // --- ここまで ---

          // ポイント管理用配列
          var markers = [];
          var pathCoords = [];
          var polyline = L.polyline(pathCoords, {color: 'red'}).addTo(map);

          // 番号を振り直す関数
          function updateMarkerNumbers() {
            pathCoords.length = 0;
            markers.forEach(function(marker, idx) {
              var latlng = marker.getLatLng();
              marker.setPopupContent(`<b>${idx+1}</b><br/>緯度: ${latlng.lat.toFixed(6)}<br/>経度: ${latlng.lng.toFixed(6)}`);
              pathCoords.push([latlng.lat, latlng.lng]);
            });
            polyline.setLatLngs(pathCoords);
          }

          // マーカー追加関数
          function addMarker(lat, lon) {
            var marker = L.marker([lat, lon], {draggable: true}).addTo(map);
            markers.push(marker);
            marker.bindPopup(""); // 番号は後でセット
            marker.openPopup();

            // ドラッグ後のイベント
            marker.on('dragend', function(e) {
              updateMarkerNumbers();
              sendLog(e.target.getLatLng().lat, e.target.getLatLng().lng);
            });

            // 右クリックで削除
            marker.on('contextmenu', function(e) {
              map.removeLayer(marker);
              markers = markers.filter(m => m !== marker);
              updateMarkerNumbers();
            });

            updateMarkerNumbers();
            sendLog(lat, lon);
          }

          // Python側に緯度経度を送信
          function sendLog(lat, lon) {
            fetch(`/log?lat=${lat.toFixed(6)}&lon=${lon.toFixed(6)}`)
              .catch(err => console.error('Fetch error:', err));
          }

          // クリックイベント
          map.on('click', function(e) {
            addMarker(e.latlng.lat, e.latlng.lng);
          });
        </script>
      </body>
    </html>
    """
    return render_template_string(html)

# クリック座標を受け取りコンソールに出力
@app.route("/log")
def log_coords():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    app.logger.info(f"クリック座標 → 緯度: {lat}, 経度: {lon}")
    return ("", 204)

if __name__ == "__main__":
    # Flaskサーバ起動
    app.run(port=5000, debug=False)
