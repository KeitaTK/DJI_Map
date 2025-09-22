#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国土地理院航空写真ダウンロードツール

指定した緯度経度の範囲から国土地理院の航空写真タイルを倍率14～18でダウンロードします。
座標: (36.058625, 136.547351) - (36.078885, 136.600470)
"""

import requests
import math
import time
from pathlib import Path

def deg2num(lat_deg, lon_deg, zoom):
    """緯度経度からタイル番号を計算"""
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def download_gsi_aerial_photos(lat1, lon1, lat2, lon2, zoom_start=14, zoom_end=18, delay=0.1):
    """
    国土地理院の航空写真をダウンロードする

    Parameters:
      lat1, lon1: 開始座標
      lat2, lon2: 終了座標
      zoom_start: 開始倍率（デフォルト14）
      zoom_end: 終了倍率（デフォルト18）
      delay: リクエスト間の待機時間（秒）
    """
    # 座標の正規化
    min_lat, max_lat = sorted([lat1, lat2])
    min_lon, max_lon = sorted([lon1, lon2])

    base_dir = Path("gsi_aerial_photos")
    base_dir.mkdir(exist_ok=True)

    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})

    total_downloaded = 0

    for zoom in range(zoom_start, zoom_end + 1):
        print(f"\nズームレベル {zoom} をダウンロード中...")
        x1, y2 = deg2num(min_lat, min_lon, zoom)
        x2, y1 = deg2num(max_lat, max_lon, zoom)
        zoom_dir = base_dir / f"zoom_{zoom:02d}"
        zoom_dir.mkdir(exist_ok=True)

        downloaded_count = 0
        total_tiles = (x2 - x1 + 1) * (y2 - y1 + 1)
        print(f"  タイル範囲 X({x1}-{x2}) Y({y1}-{y2}) 総数: {total_tiles}")

        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                url = f"https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{zoom}/{x}/{y}.jpg"
                filepath = zoom_dir / f"tile_{x}_{y}.jpg"
                if filepath.exists():
                    downloaded_count += 1
                    continue
                try:
                    res = session.get(url, timeout=30)
                    if res.status_code == 200:
                        with open(filepath, 'wb') as f:
                            f.write(res.content)
                        downloaded_count += 1
                        total_downloaded += 1
                except Exception as e:
                    print(f"  エラー: {e}")
                time.sleep(delay)

        print(f"  完了: {downloaded_count}/{total_tiles} タイル")

    session.close()
    print(f"\n=== ダウンロード完了: {total_downloaded} ファイル ===")
    print(f"保存先: {base_dir.absolute()}")

if __name__ == '__main__':
    lat1, lon1 = 36.058625, 136.547351
    lat2, lon2 = 36.078885, 136.600470
    download_gsi_aerial_photos(lat1, lon1, lat2, lon2)
