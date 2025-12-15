DIR_TO_DELTA = {
    0: (0, -1),
    1: (1, 0),
    2: (0, 1),
    3: (-1, 0),
}


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
