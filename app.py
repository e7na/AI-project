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


def get_or(callable, default):
    try:
        return callable()
    except ValueError:
        return default


def gui(page: Page):
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
    page.update()
    page.window_min_width = 550
    BUTTON_HEIGHT = 58
    page.window_min_height = BOARD_HEIGHT * BUTTON_HEIGHT
    FALLBACK_HEIGHT = 7 * BUTTON_HEIGHT + 70
    page.window_width = 580
    window_height = lambda: (BOARD_HEIGHT * 90) + 140
    page.window_height = window_height()
    page.fonts = {
        "Fira Code": "/fonts/FiraCode-Regular.ttf",
    }

    def resize_and_update():
        blocks_map(update_width)
        update_content()

    page.on_resize = lambda e: resize_and_update()

    puzzle_input = Ref[TextField]()
    frame_switcher = Ref[Text]()
    tooltips = Ref[Column]()
    steps_summary = Ref[Text]()
    action = Ref[Text]()
    heuristic = Ref[Text]()
    move_count = Ref[Text]()
    board = Ref[Column]()
    algo_dd = Ref[Dropdown]()
    solve_button = Ref[ElevatedButton]()

    steps_string = lambda: "Goal Reached!"  if (index + 1) == len(path) else f"{index + 1} of {len(path)}" if SOLVED else "Press Solve"

    MAX_WIDTH = 150
    FALLBACK_WIDTH = 87

    width_equation = lambda: get_or(
        lambda: page.window_width * 0.65 / (BOARD_WIDTH), FALLBACK_WIDTH
    )
    block_width_or = (
        lambda x, fn=width_equation: dyn if ((dyn := fn()) and dyn < x) else x
    )

    frame_switcher_width = lambda: (BOARD_WIDTH + 0.3) * block_width_or(MAX_WIDTH)
    TOOLTIPS_WIDTH = 110

    value = lambda block: block if block != PLACEHOLDER else "  "
    not_empty = lambda block: bool(block != PLACEHOLDER)

    def load_puzzle(e):
        global BOARD, BOARD_HEIGHT, BOARD_WIDTH, puzzle
        nonlocal SOLVED, index, blocks
        index = 0
        SOLVED = False
        puzzle = parse_puzzle(puzzle_input.current.value)
        BOARD, (BOARD_HEIGHT, BOARD_WIDTH) = puzzle
        generate_grid(BOARD)
        controls = [Row(row) for row in blocks]
        board.current.controls = controls
        resize_and_update()
        view_pop(e)

    def solve_puzzle(e):
        global path, puzzle, algo_key
        nonlocal SOLVED
        steps_summary.current.value = "Solving..."
        page.update()
        if result := search(*puzzle, algo_key):
            path, *_ = result
            SOLVED = True
            frame_switcher.current.disabled = False
            solve_button.current.disabled = True
        update_content()

    def change_algo(e):
        global algo_key, path
        nonlocal SOLVED
        algo_key = algo_dd.current.value
        path = []
        SOLVED = False
        index = 0
        solve_button.current.disabled = False
        frame_switcher.current.disabled = True
        update_content()

    # fmt: off
    def generate_grid(board):
        nonlocal blocks
        return (blocks := [[TextField(
                value=value(block), text_align="center", dense=True,
                width=block_width_or(MAX_WIDTH), disabled=not_empty(block),
                read_only=True, border_color=colors.PRIMARY,
            ) for block in row
        ] for row in (board if isinstance(board, np.ndarray) else board(index))])
    # fmt: on
    blocks = generate_grid(BOARD)

    def blocks_map(fn):
        nonlocal blocks
        global BOARD
        for (x, y), block in np.ndenumerate(BOARD if not SOLVED else frames(index)):
            fn(x, y, block, blocks)
        page.update()

    def update_width(x, y, b, m):
        m[x][y].width = block_width_or(MAX_WIDTH)
        frame_switcher.current.width = frame_switcher_width()

    def update_value(x, y, b, m):
        m[x][y].value = str(value(b))
        m[x][y].disabled = not_empty(b)

    def update_content():
        blocks_map(update_value)
        steps_summary.current.value = steps_string()
        tooltips.current.height = get_or(lambda: page.window_width, FALLBACK_HEIGHT)
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

    # fmt: off
    def route_change(route):
        page.views.clear()
        page.views.append(
            View("/", [
                AppBar(
                    title=Text(TITLE, color=colors.PRIMARY, weight="bold"),
                    center_title=True,
                    bgcolor=colors.PRIMARY_CONTAINER,
                    toolbar_height=70,
                    actions=[theme_button]),

                Row(alignment="center",vertical_alignment="center", expand=True, controls=[
                    Column(alignment="center",horizontal_alignment="center",controls=[
                        # the TextField matrix that displays the board
                        *[Row(row) for row in blocks],

                        Row([Row(ref=frame_switcher, disabled=True, controls=[
                                    OutlinedButton(
                                        "Previous",
                                        on_click=prev_frame,
                                        expand=1,
                                        height=BUTTON_HEIGHT,
                                        style=ButtonStyle(shape=RoundedRectangleBorder(radius=10))),
                                    ElevatedButton(
                                        "Next",
                                        on_click=next_frame,
                                        expand=1,
                                        height=BUTTON_HEIGHT,
                                        style=ButtonStyle(shape=RoundedRectangleBorder(radius=10))),
                                    ElevatedButton(
                                        "Auto",
                                        on_click=auto_solve,
                                        expand=1,
                                        height=BUTTON_HEIGHT,
                                        style=BUTTON_STYLE)],
                                width=frame_switcher_width())],)], ref=board,),

                    Column(
                        ref=tooltips,
                        height=get_or(lambda: page.window_height - 70, FALLBACK_HEIGHT),
                        wrap=True,
                        alignment="center",
                        spacing=8,
                        controls=[
                            Dropdown(
                                width=TOOLTIPS_WIDTH,
                                height=57,
                                border_radius=10,
                                border_width=0,
                                content_padding=16,
                                ref=algo_dd,
                                filled=True,
                                on_change=change_algo,
                                alignment=alignment.center,
                                value=algo_key,
                                options=[
                                    dropdown.Option(algo) for algo in FronierOptions.keys()]),
                            
                            ElevatedButton(
                                "Input",
                                height=BUTTON_HEIGHT,
                                width=TOOLTIPS_WIDTH,
                                style=BUTTON_STYLE,
                                on_click=lambda e: page.go("/input")),

                            ElevatedButton(
                                "Randomize",
                                height=BUTTON_HEIGHT,
                                width=TOOLTIPS_WIDTH,
                                style=BUTTON_STYLE,
                                disabled=True),

                            Container(
                                Column([
                                        Text(
                                            "Action:",
                                            weight="bold"),
                                        Text(ref=action)],
                                    spacing=3,
                                    alignment="start"),
                                height=BUTTON_HEIGHT),

                            Container(
                                Column([
                                        Text(
                                            "Heuristic:",
                                            weight="bold"),
                                        Text(ref=heuristic)],
                                    spacing=3,
                                    alignment="start"),
                                height=BUTTON_HEIGHT),

                            Container(Column([
                                        Text(
                                            "Step:",
                                            weight="bold"),
                                        Text(ref=steps_summary,
                                        color=colors.PRIMARY,
                                        weight="bold")],
                                    spacing=3,
                                    alignment="start"),
                                height=BUTTON_HEIGHT),

                            Container(Column([
                                        Text(
                                            "Possible moves:",
                                            weight="bold"),
                                        Text(ref=move_count,
                                        color=colors.PRIMARY,
                                        weight="bold")],
                                    spacing=3,
                                    alignment="start"),
                                height=BUTTON_HEIGHT),

                            ElevatedButton(
                                "Solve",
                                height=BUTTON_HEIGHT,
                                width=TOOLTIPS_WIDTH,
                                ref=solve_button,
                                style=BUTTON_STYLE,
                                on_click=solve_puzzle)])
                    ])]))

        if page.route == "/input":
            page.window_height = 550
            page.views.append(
                View("/input", [
                    AppBar(title=Text("Input", color=colors.PRIMARY, weight="bold"), center_title=True,
                        bgcolor=colors.PRIMARY_CONTAINER, leading=IconButton(icons.ARROW_BACK, on_click=view_pop,
                        icon_color=colors.PRIMARY,)),
                    Text(INSTRUCTIONS, size=16, weight="w500"),
                    Container(height=10),
                    TextField(ref=puzzle_input, label="Board", multiline=True, min_lines=3,
                        text_style=TextStyle(font_family="Fira Code"), value=str(read_file("puzzle.txt"))),
                    Container(height=10),
                    ElevatedButton("DONE", on_click=load_puzzle, width=TOOLTIPS_WIDTH, height=60, style=BUTTON_STYLE)]))

        page.update()
    # fmt: on

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.window_height = (BOARD_HEIGHT * 90) + 70
        page.go(top_view.route)
        frame_switcher.current.disabled = False
        solve_button.current.disabled = True
        update_content()

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

    update_content()


if __name__ == "__main__":
    app(target=gui, port=8080, assets_dir="assets")
