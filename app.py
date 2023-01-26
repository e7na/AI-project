from flet import *
import time
import numpy as np
from lib.puzzle_env import PLACEHOLDER, SLOT, FronierOptions
from search import read_file, parse_puzzle, search

puzzle = parse_puzzle(read_file("puzzle.txt"))
BOARD, (BOARD_HEIGHT, BOARD_WIDTH) = puzzle
path = search(*puzzle)[1]
frames = lambda index: path[index].state


def gui(page: Page):
    index = 0
    SOLVED = True
    TITLE = "A* Sliding Puzzle"
    INSTRUCTIONS = (
        f"Input your puzzle formatted as a grid of numbers separated by a '|' "
        f"symbol, with the empty slot represented by two underscores '__' and "
        f"each row on a separate line as shown below."
        f"\nEnsure that the input grid is rectangular, and the numbers are unique."
    )
    BUTTON_STYLE= ButtonStyle(shape=RoundedRectangleBorder(radius=10))
    page.title = TITLE
    page.vertical_alignment = "center"
    page.theme_mode = "dark"
    page.update()
    page.window_min_width = 550
    page.window_min_height = (BOARD_HEIGHT + 1) * 50
    page.window_width = 580
    page.window_height = (BOARD_HEIGHT * 90) + 70
    page.fonts = {
        "Fira Code": "/fonts/FiraCode-Regular.ttf",
    }

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

    def steps_string():
        if SOLVED:
            return f"{index+1} of {len(path)}"
        else:
            return "Press Solve"

    FALLBACK_WIDTH = 87
    width_equation = lambda: (page.window_width * 0.65 / (BOARD_WIDTH))
    block_width_or = (
        lambda x, fn=width_equation: dyn if ((dyn := fn()) and dyn < x) else x
    )
    ac_aligment = lambda: "center" if page.window_height < 400 else "start"

    frame_switcher_width = lambda: (BOARD_WIDTH + 0.3) * block_width_or(FALLBACK_WIDTH)
    TOOLTIPS_WIDTH = 110
    
    value = lambda block: block if block != PLACEHOLDER else "  "
    not_empty = lambda block: bool(block != PLACEHOLDER)

    # fmt: off

    def load_puzzle(e):
        global BOARD, BOARD_HEIGHT, BOARD_WIDTH
        nonlocal SOLVED, index, blocks
        index = 0
        SOLVED = False
        puzzle = parse_puzzle(puzzle_input.current.value)
        BOARD, (BOARD_HEIGHT, BOARD_WIDTH) = puzzle
        generate_grid(BOARD)
        controls = [Row(row, alignment="center") for row in blocks]
        board.current.controls = controls
        page.window_height = (BOARD_HEIGHT * 90) + 70
        view_pop(e)
        resize_and_update()
        update_content()

    def generate_grid(board):
        nonlocal blocks
        return (blocks := [[TextField(
                value=value(block), text_align="center", dense=True,
                width=block_width_or(FALLBACK_WIDTH), disabled=not_empty(block),
                read_only=True, border_color="blue200",
            ) for block in row
        ] for row in (board if isinstance(board, np.ndarray) else board(index))])
    blocks = generate_grid(BOARD)

    def blocks_map(fn):
        nonlocal blocks
        global BOARD
        for (x, y), block in np.ndenumerate(BOARD if not SOLVED else frames(index)):
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
        tooltips.current.height = page.window_height - 70
        action.current.value = str(path[index].action if SOLVED else None).capitalize()
        heuristic.current.value = str(path[index].heuristic if SOLVED else None)
        move_count.current.value = (
            "Unknown" if not SOLVED
                 else len(c) if (c:=path[index].children)
                    else 0
        )
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
            time.sleep(0.6)

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


    def route_change(route):
        page.views.clear()
        page.views.append(
            View(
                "/",
                [
                    AppBar(title=Text(TITLE, color=colors.BACKGROUND, weight="bold"),
                    center_title=True, bgcolor="blue200", toolbar_height=70, actions=[theme_button]),
                    Row([

            Column([
                # the TextField matrix that displays the board
                *[Row(row, alignment="center") for row in blocks],

                Container(),

                Row([Row(ref=frame_switcher, controls=[
                        OutlinedButton("Previous", on_click=prev_frame, expand=1, height=58, style=ButtonStyle(shape=RoundedRectangleBorder(radius=10))),
                        FilledButton("Next", on_click=next_frame, expand=1, height=58, style=ButtonStyle(shape=RoundedRectangleBorder(radius=10))),
                        ElevatedButton("Auto", on_click=auto_solve, expand=1, height=58, style=BUTTON_STYLE)
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
                
                ElevatedButton("Input", height=58, width=TOOLTIPS_WIDTH, on_click=goToInput,
                    style=BUTTON_STYLE),

                ElevatedButton("Randomize", disabled=True, height=58, width=TOOLTIPS_WIDTH,
                    style=BUTTON_STYLE),

                Container(Column([
                            Text("Action:", weight="bold"),
                            Text(ref=action,)
                        ], spacing=3, alignment=ac_aligment()),
                    height=58),

                Container(Column([
                            Text("Heuristic:", weight="bold"),
                            Text(ref=heuristic)
                        ], spacing=3, alignment="start"),
                    height=58),

                Container(Column([
                            Text("Step:", weight="bold"),
                            Text(ref=steps_summary, color="blue200", weight="bold"),
                        ], spacing=3, alignment="start"),
                    height=58),

                Container(Column([
                            Text("Possible moves:", weight="bold"),
                            Text(ref=move_count, color="blue200", weight="bold"),
                        ], spacing=3, alignment="start"),
                    height=69),

                ElevatedButton("Solve", disabled=True, height=58, width=TOOLTIPS_WIDTH,
                    style=BUTTON_STYLE),
            ], ref=tooltips, height=page.window_height - 70, wrap=True, spacing=8)

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
                        TextField(ref=puzzle_input, label="Board", multiline=True, min_lines=3, value= str(read_file("puzzle.txt")),
                        text_style=TextStyle(font_family="Fira Code"),),
                        Container(height=10),
                        ElevatedButton("DONE", on_click=load_puzzle, width=TOOLTIPS_WIDTH,
                        height=60, style=BUTTON_STYLE),
                    ],
                )
            )
        page.update()

    def goToInput(e):
        page.window_height = 550
        page.go("/input")

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.window_height = (BOARD_HEIGHT * 90) + 70
        page.go(top_view.route)
        update_content()

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

    update_content()


if path and __name__ == "__main__":
    app(target=gui, port=8080, assets_dir="assets")
