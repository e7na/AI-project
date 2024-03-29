from flet import *
import time
import numpy as np
from lib.puzzle_env import PLACEHOLDER, SLOT, FronierOptions
from search import read_file, parse_puzzle, search

puzzle = parse_puzzle(read_file("puzzle.txt"))
BOARD, (BOARD_HEIGHT, BOARD_WIDTH) = puzzle
# path = search(*puzzle)[1]
path = []
frames = lambda index: path[index].state
algo_key = list(FronierOptions.keys())[0]


def gui(page: Page):

    get_or = lambda fn, default: (
        result if not (page.web) and (result := fn()) else default
    )

    index = 0
    SOLVED = False
    TITLE = "A* Sliding Puzzle"
    INSTRUCTIONS = (
        f"Input your puzzle formatted as a grid of numbers separated by a '|' "
        f"symbol, with the empty slot represented by two underscores '__' and "
        f"each row on a separate line as shown below."
        f"\nEnsure that the input grid is rectangular, and the numbers are unique."
    )
    BUTTON_STYLE = ButtonStyle(shape=RoundedRectangleBorder(radius=10))
    page.title = TITLE
    page.dark_theme = page.theme = Theme(color_scheme_seed=colors.PURPLE_ACCENT_100)
    page.theme_mode = "dark"
    # page.update()
    APPBAR_HEIGHT = 70
    PADDING = 30
    EXTRA_PADDING = 35
    BUTTON_HEIGHT = 57
    MAX_WIDTH = 150
    FALLBACK_WIDTH = 87
    TOOLTIPS_WIDTH = 110
    tooltips_columns = lambda: FALLBACK_HEIGHT / content_height()
    # two_bottom_rows = lambda: BOARD_HEIGHT <= 6 and BOARD_WIDTH >= 3
    bottom_rows = lambda: 2 if BOARD_HEIGHT <= 6 and BOARD_WIDTH >= 3 else 1
    FALLBACK_HEIGHT = 7 * BUTTON_HEIGHT + APPBAR_HEIGHT + PADDING + EXTRA_PADDING
    block_width = lambda: get_or(
        lambda: (page.window_width - 2 * PADDING) * 0.65 / BOARD_WIDTH,
        FALLBACK_WIDTH,
    )
    content_height = lambda: (
        (BOARD_HEIGHT + bottom_rows()) * BUTTON_HEIGHT + APPBAR_HEIGHT
    )
    window_min_height = (
        lambda: content_height() + APPBAR_HEIGHT + PADDING + EXTRA_PADDING
    )
    window_width_from = lambda block_width=FALLBACK_WIDTH: (
        BOARD_WIDTH * block_width + TOOLTIPS_WIDTH + PADDING
    )
    page.window_min_height = window_min_height()
    page.window_min_width = window_width_from()
    page.window_width = window_width_from(110)
    page.window_height = window_min_height()
    page.fonts = {
        "Fira Code": "/fonts/FiraCode-Regular.ttf",
    }

    def resize_and_update():
        blocks_map(update_width)
        tooltips.height = get_or(
            lambda: page.window_height - APPBAR_HEIGHT - PADDING, content_height()
        )
        info_row[0].width = content_width()
        frame_switcher[0].width = content_width()
        action_con[0].width = heuristic_con[0].width = Steps[0].width = (
            content_width() / 3
        )
        update_content()

    page.on_resize = lambda e: resize_and_update()

    puzzle_input = Ref[TextField]()
    steps_summary = Ref[Text]()
    action = Ref[Text]()
    heuristic = Ref[Text]()
    move_count = Ref[Text]()
    board = Ref[Column]()
    algo_dd = Ref[Dropdown]()

    steps_string = (
        lambda: "Goal Reached!"
        if (index + 1) == len(path)
        else f"{index + 1} of {len(path)}"
        if SOLVED
        else "Press Solve"
    )

    block_width_or = lambda x, fn=block_width: dyn if ((dyn := fn()) and dyn < x) else x

    content_width = lambda: BOARD_WIDTH * block_width_or(MAX_WIDTH) + PADDING

    value = lambda block: block if block != PLACEHOLDER else "  "
    not_empty = lambda block: bool(block != PLACEHOLDER)

    def load_puzzle(e):
        global BOARD, BOARD_HEIGHT, BOARD_WIDTH, puzzle
        nonlocal SOLVED, index, blocks
        index = 0
        SOLVED = False
        update_clickability()
        puzzle = parse_puzzle(puzzle_input.current.value)
        BOARD, (BOARD_HEIGHT, BOARD_WIDTH) = puzzle
        page.window_min_height = window_min_height()
        page.window_min_width = window_width_from()
        page.window_width = window_width_from(110)
        page.window_height = window_min_height()
        generate_grid(BOARD)
        controls = [Row(row) for row in blocks]
        board.current.controls = controls
        # page.window_min_height = window_height()#((BOARD_HEIGHT + 3) * BUTTON_HEIGHT) + APPBAR_HEIGHT
        set_widgets()
        resize_and_update()
        action_con[0].expand = Steps[0].expand = possible_moves[0].expand = bool(
            BOARD_HEIGHT == 3
        )
        view_pop(e)

    def solve_puzzle(e):
        global path, puzzle, algo_key
        nonlocal SOLVED
        steps_summary.current.value = "Solving..."
        page.update()
        if result := search(*puzzle, algo_key):
            path, *_ = result
            SOLVED = True
            update_clickability()
        update_content()

    def change_algo(e):
        global algo_key, path
        nonlocal SOLVED, index
        algo_key = algo_dd.current.value
        path = []
        SOLVED = False
        update_clickability()
        index = 0
        update_content()

    def generate_grid(board):
        nonlocal blocks
        return (
            blocks := [
                [
                    TextField(
                        value=value(block),
                        text_align="center",
                        dense=True,
                        width=block_width_or(MAX_WIDTH),
                        disabled=not_empty(block),
                        read_only=True,
                        border_color=colors.PRIMARY,
                        border_radius=10,
                    )
                    for block in row
                ]
                for row in (board if isinstance(board, np.ndarray) else board(index))
            ]
        )

    blocks = generate_grid(BOARD)

    def update_clickability():
        if SOLVED:
            solve_button.disabled = True
            frame_switcher[0].disabled = False
        else:
            solve_button.disabled = False
            frame_switcher[0].disabled = True

    def blocks_map(fn):
        nonlocal blocks
        global BOARD
        for (x, y), block in np.ndenumerate(BOARD if not SOLVED else frames(index)):
            fn(x, y, block, blocks)
        page.update()

    def update_width(x, y, b, m):
        m[x][y].width = block_width_or(MAX_WIDTH)

    def update_value(x, y, b, m):
        m[x][y].value = str(value(b))
        m[x][y].disabled = not_empty(b)

    def update_content():
        blocks_map(update_value)
        steps_summary.current.value = steps_string()
        action.current.value = str(path[index].action if SOLVED else None).capitalize()
        heuristic.current.value = str(path[index].heuristic if SOLVED else None)
        move_count.current.value = (
            "Unknown" if not SOLVED else len(c) if (c := path[index].children) else 0
        )
        if index == len(path) - 1:
            steps_summary.current.color = "green"
        else:
            steps_summary.current.color = colors.PRIMARY
        page.update()

    def next_frame(e):
        nonlocal index
        if index < len(path) - 1:
            index += 1
            update_content()

    def prev_frame(e):
        nonlocal index
        if index > 0:
            index -= 1
            update_content()

    def auto_solve(e):
        for _ in path[index::]:
            next_frame(e)
            time.sleep(0.5)

    def change_theme(e):
        # Switch Between dark and light mode
        page.theme_mode = "light" if page.theme_mode == "dark" else "dark"
        theme_button.selected = not theme_button.selected
        page.update()

    # button to change theme_mode (from dark to light mode, or the reverse)
    theme_button = IconButton(
        icons.DARK_MODE,
        selected_icon=icons.LIGHT_MODE,
        icon_color=colors.PRIMARY,
        icon_size=30,
        on_click=change_theme,
        tooltip="change theme",
        style=ButtonStyle(color=colors.PRIMARY),
    )

    frame_switcher = (
        Row(
            disabled=True,
            controls=[
                Row(
                    expand=True,
                    controls=[
                        OutlinedButton(
                            icon=icons.ARROW_BACK,
                            on_click=prev_frame,
                            expand=1,
                            height=BUTTON_HEIGHT,
                            style=ButtonStyle(shape=RoundedRectangleBorder(radius=10)),
                        ),
                        OutlinedButton(
                            icon=icons.ARROW_FORWARD,
                            on_click=next_frame,
                            expand=1,
                            height=BUTTON_HEIGHT,
                            style=ButtonStyle(shape=RoundedRectangleBorder(radius=10)),
                        ),
                        ElevatedButton(
                            "Auto",
                            on_click=auto_solve,
                            expand=1,
                            height=BUTTON_HEIGHT,
                            style=BUTTON_STYLE,
                        ),
                    ],
                    width=content_width(),
                )
            ],
        ),
    )

    action_con = (
        Container(
            Column(
                [
                    Text("Action:", weight="bold"),
                    Text(ref=action, color=colors.PRIMARY, weight="w500"),
                ],
                spacing=3,
            ),
            height=BUTTON_HEIGHT,
            padding=padding.only(left=5),
        ),
    )

    heuristic_con = (
        Container(
            Column(
                [
                    Text("Heuristic:", weight="bold"),
                    Text(ref=heuristic, color=colors.PRIMARY, weight="w500"),
                ],
                spacing=3,
            ),
            height=BUTTON_HEIGHT,
            padding=padding.only(left=5),
        ),
    )

    Steps = (
        Container(
            Column(
                [
                    Text("Step:", weight="bold"),
                    Text(ref=steps_summary, color=colors.PRIMARY, weight="w500"),
                ],
                spacing=3,
            ),
            height=BUTTON_HEIGHT,
            padding=padding.only(left=5),
        ),
    )

    possible_moves = (
        Container(
            Column(
                [
                    Text("Possible Moves:", weight="bold"),
                    Text(ref=move_count, color=colors.PRIMARY, weight="w500"),
                ],
                spacing=3,
            ),
            height=BUTTON_HEIGHT,
            padding=padding.only(left=5),
        ),
    )

    solve_button = ElevatedButton(
        "Solve",
        height=BUTTON_HEIGHT,
        width=TOOLTIPS_WIDTH,
        style=BUTTON_STYLE,
        on_click=solve_puzzle,
    )

    info_row = Container()
    tooltips = Container()

    def set_widgets():
        nonlocal info_row, tooltips
        if bottom_rows() == 2:
            info_row = (
                Column(
                    [
                        Row(
                            controls=[
                                action_con[0],
                                Steps[0],
                                possible_moves[0],
                            ],
                        ),
                        frame_switcher[0],
                    ],
                    width=content_width(),
                ),
            )

            tooltips = Column(
                height=get_or(
                    lambda: page.window_height - APPBAR_HEIGHT - PADDING,
                    content_height(),
                ),
                wrap=True,
                alignment="center",
                spacing=9,
                controls=[
                    Dropdown(
                        width=TOOLTIPS_WIDTH,
                        height=BUTTON_HEIGHT,
                        color=colors.PRIMARY,
                        text_style=TextStyle(weight="Bold"),
                        border_radius=10,
                        border_width=0,
                        content_padding=16,
                        ref=algo_dd,
                        filled=True,
                        on_change=change_algo,
                        alignment=alignment.center,
                        value=algo_key,
                        options=[
                            dropdown.Option(algo) for algo in FronierOptions.keys()
                        ],
                    ),
                    ElevatedButton(
                        "Input",
                        height=BUTTON_HEIGHT,
                        width=TOOLTIPS_WIDTH,
                        style=BUTTON_STYLE,
                        on_click=lambda e: page.go("/input"),
                    ),
                    ElevatedButton(
                        "Randomize",
                        height=BUTTON_HEIGHT,
                        width=TOOLTIPS_WIDTH,
                        style=BUTTON_STYLE,
                        disabled=True,
                    ),
                    heuristic_con[0],
                    solve_button,
                ],
            )
        else:
            info_row = frame_switcher
            tooltips = Column(
                height=get_or(
                    lambda: page.window_height - APPBAR_HEIGHT - PADDING,
                    content_height(),
                ),
                wrap=True,
                alignment="center",
                spacing=9,
                controls=[
                    Dropdown(
                        width=TOOLTIPS_WIDTH,
                        height=BUTTON_HEIGHT,
                        color=colors.PRIMARY,
                        text_style=TextStyle(weight="Bold"),
                        border_radius=10,
                        border_width=0,
                        content_padding=16,
                        ref=algo_dd,
                        filled=True,
                        on_change=change_algo,
                        alignment=alignment.center,
                        value=algo_key,
                        options=[
                            dropdown.Option(algo) for algo in FronierOptions.keys()
                        ],
                    ),
                    ElevatedButton(
                        "Input",
                        height=BUTTON_HEIGHT,
                        width=TOOLTIPS_WIDTH,
                        style=BUTTON_STYLE,
                        on_click=lambda e: page.go("/input"),
                    ),
                    ElevatedButton(
                        "Randomize",
                        height=BUTTON_HEIGHT,
                        width=TOOLTIPS_WIDTH,
                        style=BUTTON_STYLE,
                        disabled=True,
                    ),
                    action_con[0],
                    heuristic_con[0],
                    Steps[0],
                    possible_moves[0],
                    solve_button,
                ],
            )

    def route_change(route):
        set_widgets()
        page.views.clear()
        page.views.append(
            View(
                "/",
                [
                    AppBar(
                        title=Text(TITLE, color=colors.PRIMARY, weight="bold"),
                        center_title=True,
                        bgcolor=colors.PRIMARY_CONTAINER,
                        toolbar_height=APPBAR_HEIGHT,
                        actions=[theme_button],
                    ),
                    Row(
                        alignment="center",
                        vertical_alignment="center",
                        expand=True,
                        controls=[
                            Column(
                                alignment="center",
                                horizontal_alignment="center",
                                controls=[
                                    # the TextField matrix that displays the board
                                    *[Row(row) for row in blocks],
                                    info_row[0],
                                ],
                                height=get_or(
                                    lambda: page.window_height
                                    - APPBAR_HEIGHT
                                    - PADDING,
                                    content_height(),
                                ),
                                ref=board,
                            ),
                            tooltips,
                        ],
                    ),
                ],
            )
        )

        if page.route == "/input":
            page.window_height = 550
            page.views.append(
                View(
                    "/input",
                    [
                        AppBar(
                            title=Text("Input", color=colors.PRIMARY, weight="bold"),
                            center_title=True,
                            bgcolor=colors.PRIMARY_CONTAINER,
                            leading=IconButton(
                                icons.ARROW_BACK,
                                on_click=view_pop,
                                icon_color=colors.PRIMARY,
                            ),
                        ),
                        Text(INSTRUCTIONS, size=16, weight="w500"),
                        Container(height=10),
                        TextField(
                            ref=puzzle_input,
                            label="Board",
                            multiline=True,
                            min_lines=3,
                            text_style=TextStyle(font_family="Fira Code"),
                            value=str(read_file("puzzle.txt")),
                        ),
                        Container(height=10),
                        ElevatedButton(
                            "DONE",
                            on_click=load_puzzle,
                            width=TOOLTIPS_WIDTH,
                            height=60,
                            style=BUTTON_STYLE,
                        ),
                    ],
                )
            )

        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        # page.window_height = (BOARD_HEIGHT * 90) + 70
        page.go(top_view.route)
        update_clickability()
        # resize_and_update()
        # update_content()

    page.on_route_change = route_change
    page.on_view_pop = lambda e: resize_and_update
    page.go(page.route)

    # update_content()
    resize_and_update()


if __name__ == "__main__":
    app(target=gui, port=8080, assets_dir="assets")
