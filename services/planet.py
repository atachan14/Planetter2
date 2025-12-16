# get_planet_tiles
def get_planet_tiles(cur, user_id):
    """
    惑星着陸時のスナップショットを返す
    {
      planet: {...},
      tiles: { "x,y": {...} },
      users: { user_id: {...} }
    }
    """
    # --------------------------------------------------
    # ① ユーザーのいる惑星を取得
    # --------------------------------------------------
    cur.execute("""
        SELECT planet_id
        FROM users
        WHERE id = %s
    """, (user_id,))
    row = cur.fetchone()
    if row is None:
        raise Exception("user not found")

    planet_id = row["planet_id"]

    # --------------------------------------------------
    # ② 惑星情報
    # --------------------------------------------------
    cur.execute("""
        SELECT id, name, width, height
        FROM planet
        WHERE id = %s
    """, (planet_id,))
    planet_row = cur.fetchone()

    planet = {
        "id": planet_row["id"],
        "name": planet_row["name"],
        "width": planet_row["width"],
        "height": planet_row["height"],
    }

    # --------------------------------------------------
    # ③ タイル上のオブジェクト
    # --------------------------------------------------
    cur.execute("""
        SELECT
            o.id            AS object_id,
            o.kind          AS kind,
            op.x            AS x,
            op.y            AS y,

            -- post summary
            p.value         AS post_value,
            p.good          AS post_good,
            p.bad           AS post_bad,

            -- book summary
            b.name          AS book_name

        FROM object_placements op
        JOIN objects o
            ON o.id = op.object_id

        LEFT JOIN post p
            ON p.object_id = o.id

        LEFT JOIN book b
            ON b.object_id = o.id

        WHERE op.planet_id = %s
    """, (planet_id,))

    tiles = {}

    for row in cur.fetchall():
        key = f"{row['x']},{row['y']}"

        # kindごとにsummaryを組み立てる
        if row["kind"] == "post":
            summary = {
                "value": row["post_value"],
                "good": row["post_good"],
                "bad": row["post_bad"],
            }
        elif row["kind"] == "page":
            summary = {
                "page_name": row["page_name"],
            }
        elif row["kind"] == "book":
            summary = {
                "book_name": row["book_name"],
            }
        elif row["kind"] == "shelf":
            summary = {
                "shelf_name": row["shelf_name"],
            }
        else:
            summary = {}

        tiles[key] = {
            "object": {
                "id": row["object_id"],
                "kind": row["kind"],
                "summary": summary,
            }
        }

    # --------------------------------------------------
    # ④ 同じ惑星にいるユーザー
    # --------------------------------------------------
    cur.execute("""
        SELECT
            id,
            username,
            pos_x,
            pos_y,
            dir
        FROM users
        WHERE planet_id = %s
    """, (planet_id,))

    users = {}

    for row in cur.fetchall():
        users[row["id"]] = {
            "username": row["username"],
            "x": row["pos_x"],
            "y": row["pos_y"],
            "dir": row["dir"],
        }

    return {
        "planet": planet,
        "tiles": tiles,
        "users": users,
    }



# walk
def walk_player(cur, user_id):
    cur.execute(
        """
        SELECT u.x, u.y, u.dir, u.planet_id, p.width, p.height
        FROM users u
        JOIN planets p ON u.planet_id = p.id
        WHERE u.id = %s
        """,
        (user_id,)
    )
    row = cur.fetchone()
    if row is None:
        return None

    x, y, dir, planet_id, width, height = row
    dx, dy = DIR_TO_DELTA[dir]

    new_x = (x + dx) % width
    new_y = (y + dy) % height

    cur.execute(
        "UPDATE players SET x = %s, y = %s WHERE user_id = %s",
        (new_x, new_y, user_id)
    )

    return {
        "planet_id": planet_id,
        "x": new_x,
        "y": new_y,
        "r": 1
    }
DIR_TO_DELTA = {
    0: (0, -1),
    1: (1, 0),
    2: (0, 1),
    3: (-1, 0),
}

# turn
def turn_player(cur, user_id, turn):
    cur.execute(
        "SELECT dir, planet_id FROM players WHERE user_id = %s",
        (user_id,)
    )
    dir, planet_id = cur.fetchone()

    new_dir = rotate(dir, turn)

    cur.execute(
        "UPDATE players SET dir = %s WHERE user_id = %s",
        (new_dir, user_id)
    )

    return {
        "planet_id": planet_id,
        "r": 1
    }
def rotate(dir, turn):
    return (dir + turn) % 4

# surroundings
def get_planet_tiles(cur, user_id):
    # ① 自分の位置と planet サイズ
    cur.execute(
        """
        SELECT u.planet_id, p.width, p.height
        FROM users u
        JOIN planets p ON u.planet_id = p.id
        WHERE u.id = %s
        """,
        (user_id,)
    )
    row = cur.fetchone()
    if row is None:
        return None

    cx, cy, planet_id, width, height = row

    # ② 周囲3x3の座標を計算（トーラス）
    coords = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            x = (cx + dx) % width
            y = (cy + dy) % height
            coords.append((x, y))

    # ③ あるオブジェクトだけ取得
    cur.execute(
        """
        SELECT x, y, object_id
        FROM object_placements
        WHERE planet_id = %s
          AND (x, y) IN %s
        """,
        (planet_id, tuple(coords))
    )
    rows = cur.fetchall()

    # ④ (x, y) → object_id の辞書に
    placed = {(x, y): object_id for x, y, object_id in rows}

    # ⑤ 3x3 を empty 補完して返す
    result = []
    for dy in (-1, 0, 1):
        row_cells = []
        for dx in (-1, 0, 1):
            x = (cx + dx) % width
            y = (cy + dy) % height
            obj = placed.get((x, y))
            row_cells.append({
                "x": x,
                "y": y,
                "object_id": obj,  # None なら empty
            })
        result.append(row_cells)

    return {
        "center": {"x": cx, "y": cy},
        "cells": result
    }
