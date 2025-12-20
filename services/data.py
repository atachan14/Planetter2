# user
def fetch_self_data(cur, user_id):
    cur.execute("""
        SELECT
            id,
            username,
            planet_id,
            x,
            y,
            direction,
            stardust,
            created_at
        FROM users
        WHERE id = %s
    """, (user_id,))
    
    row = cur.fetchone()
    if row is None:
        return None

    return {
        "id": row["id"],
        "username": row["username"],
        "planet_id": row["planet_id"],
        "x": row["x"],
        "y": row["y"],
        "direction": row["direction"],
        "stardust": row["stardust"],
        "created_at": row["created_at"]
    }

# planet
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
        SELECT id, name, width, height,created_at,created_name
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
        "created_at": planet_row["created_at"],
        "created_name": planet_row["created_name"]
    }

    # --------------------------------------------------
    # ③ タイル上のオブジェクト
    # --------------------------------------------------
    cur.execute("""
        SELECT
          o.id,
          o.kind,
          o.content,
          ot.x,
          ot.y
        FROM object_tiles ot
        JOIN objects o ON o.id = ot.object_id
        WHERE ot.planet_id = %s
    """, (planet_id,))

    tiles = {}

    for row in cur.fetchall():
        key = f"{row['x']},{row['y']}"

        tiles[key] = {
            "id": row["id"],
            "kind": row["kind"],
            "content": row["content"] or "",
        }
        

    # --------------------------------------------------
    # ④ 同じ惑星にいるユーザー
    # --------------------------------------------------
    cur.execute("""
        SELECT
            id,
            username,
            x,
            y
        FROM users
        WHERE planet_id = %s
    """, (planet_id,))

    users = {}

    for row in cur.fetchall():
        users[row["id"]] = {
            "username": row["username"],
            "x": row["x"],
            "y": row["y"],
        }

    return {
        "planet": planet,
        "tiles": tiles,
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

