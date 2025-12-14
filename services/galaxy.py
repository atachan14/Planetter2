import random
from db import get_db

def land_on_planet(cur, user_id, planet_id):
    cur.execute(
        "SELECT width, height FROM planets WHERE id = %s",
        (planet_id,)
    )
    width, height = cur.fetchone()

    x = random.randrange(width)
    y = random.randrange(height)
    dir = random.randrange(4)

    cur.execute(
        """
        UPDATE users
        SET planet_id = %s,
            pos_x = %s,
            pos_y = %s,
            dir = %s
        WHERE id = %s
        """,
        (planet_id, x, y, dir, user_id)
    )
