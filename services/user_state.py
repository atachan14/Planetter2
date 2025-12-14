def get_user_state(cur, user_id):
    cur.execute("""
        SELECT
            u.username,
            u.pos_x,
            u.pos_y,
            u.dir,
            p.id AS planet_id,
            p.name AS planet_name
        FROM users u
        JOIN planets p ON u.planet_id = p.id
        WHERE u.id = %s
    """, (user_id,))
    row = cur.fetchone()

    return {
        "user_name": row[0],
        "pos_x": row[1],
        "pos_y": row[2],
        "dir": row[3],
        "planet_id": row[4],
        "planet_name": row[5],
    }
