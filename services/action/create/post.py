#post
def to_tile(cur, user_id: int, content: str):
    # 1. ユーザー存在確認 + 現在座標取得 
    cur.execute(
        """ 
        SELECT id, planet_id, x, y,username 
        FROM users WHERE id = %s 
        """,
        (user_id,) 
        ) 
    user = cur.fetchone() 
    if user is None: 
        return None
    # 2. objects 作成
    cur.execute( 
        """ 
        INSERT INTO objects (kind,content,created_name) 
        VALUES ('post', %s, %s) RETURNING id 
        """, 
        (content,user["username"]) 
        ) 
    object_id = cur.fetchone()["id"] 
    # 3. object_placements に配置 
    cur.execute( 
        """ 
        INSERT INTO object_tiles (object_id, planet_id, x, y) 
        VALUES (%s, %s, %s, %s) 
        """, 
        (object_id, user["planet_id"], user["x"], user["y"]) 
        ) 
    # 4. posts に本文保存が要らなくなった 
    # 5. 返却用データ（HTTP / WS 共通） 
    return { 
        "object_id": object_id, 
        "kind": "post", 
        "content": content, 
        "planet_id": user["planet_id"], 
        "x": user["x"], 
        "y": user["y"], 
        }
