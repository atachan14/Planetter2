# ========================
# --------display-----------
# ====================

# get_planet_tiles
def fetch_planet_data(cur, user_id):
    """
    惑星着陸時のスナップショットを返す
    {
      planet: {...},
      objects: { "x,y": {...} },
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
        SELECT id, name, width, height,created_at
        FROM planets
        WHERE id = %s
    """, (planet_id,))
    planet_row = cur.fetchone()
    if planet_row is None:
        raise Exception("planet not found")


    planet = {
        "id": planet_row["id"],
        "name": planet_row["name"],
        "width": planet_row["width"],
        "height": planet_row["height"],
        "created_at": planet_row["created_at"]
    }

    # --------------------------------------------------
    # ③ タイル上のオブジェクト
    # --------------------------------------------------
    cur.execute("""
        SELECT
          o.id,
          o.kind,
          o.surround_text,
          op.x,
          op.y
        FROM object_placements op
        JOIN objects o ON o.id = op.object_id
        WHERE op.planet_id = %s
    """, (planet_id,))

    objects = {}

    for row in cur.fetchall():
        key = f"{row['x']},{row['y']}"

        objects[key] = {
            "id": row["id"],
            "kind": row["kind"],
            "surround_text": row["surround_text"] or "",
        }
        

    # --------------------------------------------------
    # ④ 同じ惑星にいるユーザー
    # --------------------------------------------------
    cur.execute("""
        SELECT
            id,
            username,
            pos_x,
            pos_y
        FROM users
        WHERE planet_id = %s
    """, (planet_id,))

    users = {}

    for row in cur.fetchall():
        users[row["id"]] = {
            "username": row["username"],
            "x": row["pos_x"],
            "y": row["pos_y"],
        }

    return {
        "planet": planet,
        "objects": objects,
        "users": users,
    }


# here
def fetch_here_data(cur, object_id):
    return{
        "dummy": True
    }


def get_current_user(cur,user_id):
    cur.execute("""
        SELECT id, planet_id, x, y,direction
        FROM users
        WHERE id = %s
    """, (user_id,))
    return cur.fetchone()






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

def post_user(cur, user_id: int, value: str):
    # 1. ユーザー存在確認 + 現在座標取得
    cur.execute(
        """
        SELECT id, planet_id, pos_x, pos_y
        FROM users
        WHERE id = %s
        """,
        (user_id,)
    )
    user = cur.fetchone()
    if user is None:
        return None

    # 2. objects 作成
    cur.execute(
        """
        INSERT INTO objects (kind,surround_text)
        VALUES ('post', %s)
        RETURNING id
        """,
        (value,)
    )
    object_id = cur.fetchone()["id"]

    # 3. object_placements に配置
    cur.execute(
        """
        INSERT INTO object_placements (object_id, planet_id, x, y)
        VALUES (%s, %s, %s, %s)
        """,
        (object_id, user["planet_id"], user["pos_x"], user["pos_y"])
    )

    # 4. posts に本文保存
    cur.execute(
        """
        INSERT INTO posts (object_id, value, created_user)
        VALUES (%s, %s, %s)
        """,
        (object_id, value, user["id"])
    )

    # 5. 返却用データ（HTTP / WS 共通）
    return {
        "object_id": object_id,
        "kind": "post",
        "surround_text": value,
        "planet_id": user["planet_id"],
        "x": user["pos_x"],
        "y": user["pos_y"],
    }
