#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ダウンロード済みタイルをMBTilesに変換するツール

前提:
  - gsi_aerial_photos/zoom_XX/tile_X_Y.jpg のフォルダ構成でタイルが保存されていること
  - Pythonパッケージ: mercantile, sqlite3, click をインストール済み
      pip install mercantile click
"""

import os
import sqlite3
import mercantile
import click

@click.command()
@click.option('--tiles-dir', default='gsi_aerial_photos',
              help='XYZタイルを格納したディレクトリ')
@click.option('--mbtiles', default='output.mbtiles',
              help='出力するMBTilesファイル名')
def create_mbtiles(tiles_dir, mbtiles):
    # MBTiles SQLite DB 作成
    conn = sqlite3.connect(mbtiles)
    cur = conn.cursor()

    # metadata テーブル
    cur.execute('''
        CREATE TABLE metadata (
            name TEXT,
            value TEXT
        );
    ''')

    # tiles テーブル
    cur.execute('''
        CREATE TABLE tiles (
            zoom_level INTEGER,
            tile_column INTEGER,
            tile_row INTEGER,
            tile_data BLOB
        );
    ''')

    # インデックス作成
    cur.execute('CREATE UNIQUE INDEX idx_tiles ON tiles (zoom_level, tile_column, tile_row);')

    # メタ情報挿入
    meta = {
        'name': 'GSI Aerial Photos',
        'format': 'jpg',
        'version': '1.0',
        'bounds': '-180.0,-85.0511,180.0,85.0511',
        'minzoom': '14',
        'maxzoom': '18',
        'type': 'overlay'
    }
    for k, v in meta.items():
        cur.execute('INSERT INTO metadata (name, value) VALUES (?, ?);', (k, v))
    conn.commit()

    # タイル読み込み
    for zoom_str in sorted(os.listdir(tiles_dir)):
        if not zoom_str.startswith('zoom_'):
            continue
        z = int(zoom_str.split('_')[1])
        zoom_path = os.path.join(tiles_dir, zoom_str)
        for filename in os.listdir(zoom_path):
            if not filename.endswith('.jpg'):
                continue
            # ファイル名 tile_X_Y.jpg から x, y を取得
            parts = filename.rstrip('.jpg').split('_')
            x, y = int(parts[1]), int(parts[2])
            # XYZ→TMS変換（MBTilesはTMS Y座標）
            tms_y = (2**z - 1 - y)  # ← ここだけでOK
            file_path = os.path.join(zoom_path, filename)
            with open(file_path, 'rb') as f:
                blob = f.read()
            cur.execute(
                'INSERT OR REPLACE INTO tiles (zoom_level, tile_column, tile_row, tile_data) VALUES (?, ?, ?, ?);',
                (z, x, tms_y, blob)
            )

    conn.commit()
    conn.close()
    print(f'MBTilesファイルを生成しました: {mbtiles}')

if __name__ == '__main__':
    create_mbtiles()
