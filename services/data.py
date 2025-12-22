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
    self_data = fetch_self_data(cur, user_id)
    if self_data is None:
        raise Exception("user not found")

    planet_id = self_data["planet_id"]


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
def fetch_here_data(cur, user_id: int):
    # 1) ユーザーの現在地
    cur.execute("""
        SELECT planet_id, x, y
        FROM users
        WHERE id = %s
    """, (user_id,))
    user = cur.fetchone()
    if not user:
        return {"root_id": None, "nodes": {}, "edges": {}}

    # 2) タイル上の root object を取得
    cur.execute("""
        SELECT object_id
        FROM object_tiles
        WHERE planet_id = %s AND x = %s AND y = %s
        LIMIT 1
    """, (user["planet_id"], user["x"], user["y"]))
    row = cur.fetchone()
    if not row:
        return {"root_id": None, "nodes": {}, "edges": {}}

    root_id = row["object_id"]

    # 3) relation を再帰で全部拾う（root から辿れる child を全取得）
    cur.execute("""
        WITH RECURSIVE rel AS (
          SELECT parent_id, child_id
          FROM object_relations
          WHERE parent_id = %s

          UNION ALL

          SELECT r.parent_id, r.child_id
          FROM object_relations r
          JOIN rel ON r.parent_id = rel.child_id
        )
        SELECT parent_id, child_id
        FROM rel
    """, (root_id,))
    rel_rows = cur.fetchall()

    # 4) edges と ids を作る
    edges: dict[int, list[int]] = {}
    ids = {root_id}
    for r in rel_rows:
        p = r["parent_id"]
        c = r["child_id"]
        edges.setdefault(p, []).append(c)
        ids.add(p)
        ids.add(c)

    # 5) objects をまとめて取る
    cur.execute("""
        SELECT id, kind, content, good, bad, created_at, created_user
        FROM objects
        WHERE id = ANY(%s)
    """, (list(ids),))
    obj_rows = cur.fetchall()

    nodes = {str(o["id"]): dict(o) for o in obj_rows}

    return {
        "root_id": root_id,
        "nodes": nodes,
        "edges": edges
    }

