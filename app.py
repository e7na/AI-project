from flet import *
import time
import numpy as np
from lib.puzzle_env import PLACEHOLDER, SLOT, FronierOptions
from search import read_file, parse_puzzle, search

puzzle = parse_puzzle(read_file("puzzle.txt"))
_, (BOARD_HEIGHT, BOARD_WIDTH) = puzzle
path = search(*puzzle)[1]
frames = lambda index: path[index].state


def gui(page: Page):
    index = 0

    TITLE = "A* Sliding Puzzle"
    INSTRUCTIONS = (
        f"Input your puzzle formatted as a grid of numbers separated by a '|' "
        f"symbol, with the empty slot represented by two underscores '__' and "
        f"each row on a separate line as shown below."
        f"\nEnsure that the input grid is rectangular, and the numbers are unique."
    )
    page.title = TITLE
    page.vertical_alignment = "center"
    page.theme_mode = "dark"
    page.update()
    page.window_min_width = 550
    page.window_min_height = (BOARD_HEIGHT + 1) * 50
    page.window_width = 550
    page.window_height = BOARD_HEIGHT * 90

    def resize_and_update():
        blocks_map(update_width)
        update_content()
    page.on_resize = lambda e: resize_and_update 

    puzzle_input = Ref[TextField]()
    frame_switcher = Ref[Text]()
    tooltips = Ref[Column]()
    steps_summary = Ref[Text]()
    action = Ref[Text]()
    heuristic = Ref[Text]()
    move_count = Ref[Text]()
    board = Ref[Column]()

    steps_string = lambda: f"{index+1} of {len(path)}"

    FALLBACK_WIDTH = 87
    width_equation = lambda: (page.window_width * 0.65 / (BOARD_WIDTH))
    block_width_or = (
        lambda x, fn=width_equation: dyn if ((dyn := fn()) and dyn < x) else x
    )

    frame_switcher_width = lambda: (BOARD_WIDTH + 0.3) * block_width_or(FALLBACK_WIDTH)
    TOOLTIPS_WIDTH = 110

    value = lambda block: block if block != PLACEHOLDER else "  "
    not_empty = lambda block: bool(block != PLACEHOLDER)

    # fmt: off
    blocks = [[TextField(
                value=value(block), text_align="center", dense=True,
                width=block_width_or(FALLBACK_WIDTH), disabled=not_empty(block),
                read_only=True, border_color="blue200",
            ) for block in row
        ] for row in frames(index)]

    def blocks_map(fn):
        nonlocal blocks
        for (x, y), block in np.ndenumerate(frames(index)):
            fn(x, y, block, blocks)
        page.update()

    def update_width(x, y, b, m): 
        m[x][y].width = block_width_or(FALLBACK_WIDTH)
        frame_switcher.current.width = frame_switcher_width()

    def update_value(x, y, b, m):
        m[x][y].value = str(value(b))
        m[x][y].disabled = not_empty(b)

    def update_content():
        blocks_map(update_value)
        steps_summary.current.value = steps_string()
        tooltips.current.height = page.window_height - 80
        action.current.value = str(path[index].action)
        heuristic.current.value = str(path[index].heuristic)
        move_count.current.value = len(c) if (c:=path[index].children) else 0
        page.update()

    def next_frame(e):
        nonlocal index
        if index < len(path) - 1:
            index += 1
            update_content()
        if index == len(path) - 1:
            steps_summary.current.color = "green"
            steps_summary.current.value = "Goal Reached!"
            page.update()

    def prev_frame(e):
        nonlocal index
        if index > 0:
            index -= 1
            steps_summary.current.color = "blue200"
            update_content()
    
    def auto_solve(e):
        for _ in path[index::]:
            next_frame(e)
            time.sleep(0.4)

    def change_theme(e):
        # Switch Between dark and light mode
        page.theme_mode = "light" if page.theme_mode == "dark" else "dark"
        theme_button.selected = not theme_button.selected
        page.update()

    # button to change theme_mode (from dark to light mode, or the reverse)
    theme_button = IconButton(
        icons.DARK_MODE, selected_icon=icons.LIGHT_MODE, icon_color=colors.BLACK,
        icon_size=30, tooltip="change theme", on_click=change_theme,
        style=ButtonStyle(color={"": colors.BACKGROUND, "selected": colors.WHITE}))

    def inputP(e):
        global path, BOARD_HEIGHT, BOARD_WIDTH, index
        nonlocal blocks
        index = 0
        puzzle = parse_puzzle(puzzle_input.current.value)
        _, (BOARD_HEIGHT, BOARD_WIDTH) = puzzle
        path = search(*puzzle)[1]
        blocks = [[TextField(
                value=value(block), text_align="center", dense=True,
                width=block_width_or(FALLBACK_WIDTH), disabled=not_empty(block),
                read_only=True, border_color="blue200",
            ) for block in row
        ] for row in frames(index)]
        controls = [Row(row, alignment="center") for row in blocks]
        board.current.controls = controls
        view_pop(e)
        resize_and_update()
        update_content()
        



    def route_change(route):
        page.views.clear()
        page.views.append(
            View(
                "/",
                [
                    AppBar(title=Text(TITLE, color=colors.BACKGROUND, weight="bold"),
                    center_title=True, bgcolor="blue200", toolbar_height=70,actions=[theme_button]),
                    Row([

            Column([
                # the TextField matrix that displays the board
                *[Row(row, alignment="center") for row in blocks],

                Container(height=10),

                Row([Row(ref=frame_switcher, controls=[
                        OutlinedButton("Previous", on_click=prev_frame, expand=1),
                        FilledButton("Next", on_click=next_frame, expand=1),
                        ElevatedButton("Auto Solve", on_click=auto_solve, expand=2)
                    ], alignment="center", width=frame_switcher_width())], alignment="center"),       

            ], ref=board, alignment="center", horizontal_alignment="center"),

            Column([
                Dropdown(
                    width=TOOLTIPS_WIDTH,
                    height=57, border_radius=10, border_width=0, filled=True,
                    value=list(FronierOptions.keys())[0], content_padding=16,
                    alignment=alignment.center, options=[
                        dropdown.Option(algo) for algo in FronierOptions.keys()
                    ]),
                
                ElevatedButton("Input", height=58, width=TOOLTIPS_WIDTH, on_click=lambda _: page.go("/input"),
                    style=ButtonStyle(shape=RoundedRectangleBorder(radius=10))),

                ElevatedButton("Randomize", disabled=True, height=59, width=TOOLTIPS_WIDTH,
                    style=ButtonStyle(shape=RoundedRectangleBorder(radius=10))),

                Container(Column([
                            Text("Action:", weight="bold"),
                            Text(ref=action)
                        ], spacing=3, alignment="center"),
                    height=58),

                Container(Column([
                            Text("Heuristic:", weight="bold"),
                            Text(ref=heuristic)
                        ], spacing=3, alignment="center"),
                    height=59),

                Container(Column([
                            Text("Step:", weight="bold"),
                            Text(ref=steps_summary, color="blue200", weight="bold"),
                        ], spacing=3, alignment="center"),
                    height=62),

                Container(Column([
                            Text("Possible moves:", weight="bold"),
                            Text(ref=move_count, color="blue200", weight="bold"),
                        ], spacing=3, alignment="center"),
                    height=62),

                ElevatedButton("Solve", disabled=True, height=59, width=TOOLTIPS_WIDTH,
                    style=ButtonStyle(shape=RoundedRectangleBorder(radius=10))),
            ], ref=tooltips, height=page.window_height, wrap=True, spacing=8)

        ],alignment="center", vertical_alignment="start")
                ],
            )
        )
        if page.route == "/input":
            page.views.append(
                View(
                    "/input",
                    [
                        AppBar(title=Text("Input", color=colors.BACKGROUND, weight="bold"), center_title=True,
                        bgcolor="blue200",leading=IconButton(icons.ARROW_BACK, on_click = view_pop, icon_color=colors.BACKGROUND,)),
                        Text(INSTRUCTIONS, size=16, weight="w500"),
                        Container(height=10),
                        TextField(ref=puzzle_input, label="Board", multiline=True, min_lines=3, value= str(read_file("puzzle.txt"))),
                        Container(height=10),
                        ElevatedButton("DONE", on_click=inputP, width=TOOLTIPS_WIDTH,
                        height=60, style=ButtonStyle(shape=RoundedRectangleBorder(radius=10))),
                    ],
                )
            )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

    update_content()


if path and __name__ == "__main__":
    app(target=gui, port=8080)
