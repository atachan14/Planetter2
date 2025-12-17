# ========================
# --------display-----------
# ====================

# get_planet_tiles
def fetch_planet_data(cur, user_id):
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
        FROM planets
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
            b.book_name          AS book_name

        FROM object_placements op
        JOIN objects o
            ON o.id = op.object_id

        LEFT JOIN posts p
            ON p.object_id = o.id

        LEFT JOIN books b
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
            direction
        FROM users
        WHERE planet_id = %s
    """, (planet_id,))

    users = {}

    for row in cur.fetchall():
        users[row["id"]] = {
            "username": row["username"],
            "x": row["pos_x"],
            "y": row["pos_y"],
            "direction": row["direction"],
        }

    return {
        "planet": planet,
        "tiles": tiles,
        "users": users,
    }

# surroundings
def fetch_surround_data():
    return {
        "dummy": True
    }

# just-pos
def fetch_just_pos_data(cur, object_id):
    return{
        "dummy": True
    }










# ========================
# --------action-----------
# ====================

# walk
DIRECTION_TO_DELTA = {
    0: (0, -1),
    1: (1, 0),
    2: (0, 1),
    3: (-1, 0),
}

def walk_user(cur, user_id):
    cur.execute(
        """
        SELECT u.pos_x, u.pos_y, u.direction, u.planet_id, p.width, p.height
        FROM users u
        JOIN planets p ON u.planet_id = p.id
        WHERE u.id = %s
        """,
        (user_id,)
    )

    row = cur.fetchone()
    if row is None:
        return None

    x = row["pos_x"]
    y = row["pos_y"]
    direction = row["direction"]
    planet_id = row["planet_id"]
    width = row["width"]
    height = row["height"]

    dx, dy = DIRECTION_TO_DELTA[direction]

    new_x = (x + dx) % width
    new_y = (y + dy) % height

    cur.execute(
        "UPDATE users SET pos_x = %s, pos_y = %s WHERE id = %s",
        (new_x, new_y, user_id)
    )

    return {
        "planet_id": planet_id,
        "x": new_x,
        "y": new_y,
    }


# turn
def turn_user(cur, user_id, turn):
    cur.execute(
        "SELECT direction, planet_id FROM users WHERE id = %s",
        (user_id,)
    )
    direction, planet_id = cur.fetchone()

    new_direction = rotate(direction, turn)

    cur.execute(
        "UPDATE users SET direction = %s WHERE id = %s",
        (new_direction, user_id)
    )

    return {
        "planet_id": planet_id,
        "r": 1
    }
def rotate(direction, turn):
    return (direction + turn) % 4
