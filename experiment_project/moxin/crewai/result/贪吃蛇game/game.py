import turtle
import time
import random

delay = 0.1
score = 0
high_score = 0  # Stores the highest score

# Screen setup
screen = turtle.Screen()
screen.title("Snake Game")
screen.bgcolor("black")
screen.setup(width=600, height=600)

# Snake head
head = turtle.Turtle()
head.speed(0)
head.shape("square")
head.color("white")
head.penup()
head.goto(0, 0)
head.direction = "Stop"

# Snake food
food = turtle.Turtle()
colors = random.choice(['red', 'green', 'blue'])
shapes = random.choice(['square', 'triangle', 'circle'])
food.speed(0)
food.shape(shapes)
food.color(colors)
food.penup()
food.goto(0, 100)

pen = turtle.Turtle()
pen.speed(0)
pen.shape("square")
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0, 250)
pen.write("Score : 0  High Score : 0", align="center", font=("candara", 24, "bold"))

# Assign key directions
def go_up():
    if head.direction != "down":
        head.direction = "up"

def go_down():
    if head.direction != "up":
        head.direction = "down"

def go_left():
    if head.direction != "right":
        head.direction = "left"

def go_right():
    if head.direction != "left":
        head.direction = "right"

def move():
    if head.direction == "up":
        y = head.ycor()
        head.sety(y + 20)
    if head.direction == "down":
        y = head.ycor()
        head.sety(y - 20)
    if head.direction == "left":
        x = head.xcor()
        head.setx(x - 20)
    if head.direction == "right":
        x = head.xcor()
        head.setx(x + 20)

screen.listen()
screen.onkeypress(go_up, "w")
screen.onkeypress(go_down, "s")
screen.onkeypress(go_left, "a")
screen.onkeypress(go_right, "d")

segments = []

# Main game loop
while True:
    screen.update()
    if head.distance(food) < 20:
        x = random.randint(-270, 270)
        y = random.randint(-270, 270)
        food.goto(x, y)

        # Adding segment
        new_segment = turtle.Turtle()
        new_segment.speed(0)
        new_segment.shape("square")
        new_segment.color("orange")  # tail colour
        new_segment.penup()
        segments.append(new_segment)
        score += 10
        delay -= 0.001
        pen.clear()
        if score > high_score:  # Updating the high score
            high_score = score
        pen.write("Score : {} High Score : {}".format(score, high_score), align="center", font=("candara", 24, "bold"))
    # Check for head collisions with body segments
    for index in range(len(segments) - 1, 0, -1):
        x = segments[index-1].xcor()
        y = segments[index-1].ycor()
        segments[index].goto(x, y)
    if len(segments) > 0:
        x = head.xcor()
        y = head.ycor()
        segments[0].goto(x, y)
    move()

    # Check for head collision with the border
    if head.xcor()>290 or head.xcor()<-290 or head.ycor()>290 or head.ycor()<-290:
        time.sleep(1)
        head.goto(0,0)
        head.direction = "Stop"
        colors = random.choice(['red', 'blue', 'green'])
        shapes = random.choice(['square', 'circle'])
        for segment in segments:
            segment.goto(1000, 1000)
        segments.clear()
        score = 0
        delay = 0.1
        pen.clear()
        pen.write("Score : {} High Score : {} ".format(score, high_score), align="center", font=("candara", 24, "bold"))

    # Check for head collisions with the body segments
    for segment in segments:
        if segment.distance(head) < 20:
            time.sleep(1)
            head.goto(0, 0)
            head.direction = "Stop"
            colors = random.choice(['red', 'blue', 'green'])
            shapes = random.choice(['square', 'circle'])
            for segment in segments:
                segment.goto(1000, 1000)
            segments.clear()
            score = 0
            delay = 0.1
            pen.clear()
            pen.write("Score : {} High Score : {} ".format(score, high_score), align="center", font=("candara", 24, "bold"))
    time.sleep(delay)
#



#
#
# import random
# import curses
#
# # Initialize the screen
# s = curses.initscr()
# curses.curs_set(0)
# sh, sw = s.getmaxyx()
# w = curses.newwin(sh, sw, 0, 0)
# w.keypad(1)
# w.timeout(100)
#
# # Snake starting point
# snk_x = sw//4
# snk_y = sh//2
# snake = [
#     [snk_y, snk_x],
#     [snk_y, snk_x-1],
#     [snk_y, snk_x-2]
# ]
#
# # Food
# food = [sh//2, sw//2]
# w.addch(int(food[0]), int(food[1]), curses.ACS_PI)
#
# # Initial score
# score = 0
# w.addstr(0, 0, 'Score: ' + str(score))  # Display the initial score
#
# # Snake direction
# key = curses.KEY_RIGHT
#
# while True:
#     next_key = w.getch()
#     key = key if next_key == -1 else next_key
#
#     # Check if game over
#     if snake[0][0] in [0, sh] or \
#         snake[0][1] in [0, sw] or \
#         snake[0] in snake[1:]:
#         curses.endwin()
#         quit()
#
#     # Check if snake has eaten food
#     new_head = [snake[0][0], snake[0][1]]
#
#     if snake[0][0] == food[0] and snake[0][1] == food[1]:
#         score += 1
#         food = None
#         while food is None:
#             nf = [
#                 random.randint(1, sh-1),
#                 random.randint(1, sw-1)
#             ]
#             food = nf if nf not in snake else None
#         w.addch(food[0], food[1], curses.ACS_PI)
#     else:
#         tail = snake.pop()
#         w.addch(int(tail[0]), int(tail[1]), ' ')
#
#     if key == curses.KEY_DOWN:
#         new_head[0] += 1
#     if key == curses.KEY_UP:
#         new_head[0] -= 1
#     if key == curses.KEY_LEFT:
#         new_head[1] -= 1
#     if key == curses.KEY_RIGHT:
#         new_head[1] += 1
#
#     # Update the snake
#     snake.insert(0, new_head)
#     w.addch(snake[0][0], snake[0][1], curses.ACS_CKBOARD)
#
#     # Display score
#     w.addstr(0, 0, 'Score: ' + str(score))