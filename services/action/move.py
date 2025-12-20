import random

#helper
DIRECTION_TO_DELTA = {
    0: (0, -1),
    1: (1, 0),
    2: (0, 1),
    3: (-1, 0),
}
def rotate(direction, turn):
    return (direction + turn) % 4

#landing
def land_on_planet(cur, user_id, planet_id):
    cur.execute(
        "SELECT width, height FROM planets WHERE id = %s",
        (planet_id,)
    )
    row = cur.fetchone()
    width = int(row["width"])
    height = int(row["height"])

    x = random.randrange(width)
    y = random.randrange(height)
    direction = random.randrange(4)

    cur.execute(
        """
        UPDATE users
        SET planet_id = %s,
            x = %s,
            y = %s,
            direction = %s
        WHERE id = %s
        """,
        (planet_id, x, y, direction, user_id)
    )

# walk
def walk_user(cur, user_id):
    cur.execute(
        """
        SELECT u.x, u.y, u.direction, u.planet_id, p.width, p.height
        FROM users u
        JOIN planets p ON u.planet_id = p.id
        WHERE u.id = %s
        """,
        (user_id,)
    )

    row = cur.fetchone()
    if row is None:
        return None

    x = row["x"]
    y = row["y"]
    direction = row["direction"]
    planet_id = row["planet_id"]
    width = row["width"]
    height = row["height"]

    dx, dy = DIRECTION_TO_DELTA[direction]

    new_x = (x + dx) % width
    new_y = (y + dy) % height

    cur.execute(
        "UPDATE users SET x = %s, y = %s WHERE id = %s",
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
