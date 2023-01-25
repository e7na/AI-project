from flet import *
from main import np, time, PLACEHOLDER, SLOT, parse_puzzle, read_file, search

puzzle = parse_puzzle(read_file("puzzle.txt"))
_, (BOARD_HEIGHT, BOARD_WIDTH) = puzzle
frames = search(*puzzle)[-1]


def gui(page: Page):
    page.title = "Sliding Puzzle"
    page.vertical_alignment = "center"
    page.on_resize = lambda e: blocks_map(update_width)
    # Define a Starting Window Size
    page.window_width = 550
    # This is Not Right:
    page.window_height = (BOARD_HEIGHT * 90) + 120
    page.window_min_width = 550
    # page.window_min_height = 650
    page.theme_mode = "dark"
    index = 0
    frame_switcher = Ref[Text]()
    steps_summary = Ref[Text]()
    tooltips = Ref[Column]()
    steps_string = lambda: f"{index+1} of {len(frames)}"
    width_equation = lambda: page.window_width * 0.65 / (BOARD_WIDTH)
    block_width_or = lambda x, fn=width_equation: dyn if (dyn := fn()) < x else x
    value = lambda s: s if s != PLACEHOLDER else SLOT
    empty = lambda s: True if s != PLACEHOLDER else False
    FALLBACK_WIDTH = 87
    TT_WIDTH = 110
    frame_switcher_width = lambda: (BOARD_WIDTH + 0.3) * block_width_or(FALLBACK_WIDTH) #+ TT_WIDTH

    # fmt: off
    blocks = [[TextField(
                value=value(block), text_align="center", dense=True,
                width=block_width_or(FALLBACK_WIDTH), disabled=empty(block),
                read_only=True, border_color="blue200",
            ) for block in row
        ] for row in frames[index]]

    def blocks_map(fn):
        nonlocal blocks
        for (x, y), block in np.ndenumerate(frames[index]):
            fn(x, y, block, blocks)
        tooltips.current.height = page.window_height - 80
        page.update()

    def update_width(x, y, b, m): 
        m[x][y].width = block_width_or(FALLBACK_WIDTH)
        frame_switcher.current.width = frame_switcher_width()

    def update_value(x, y, b, m):
        m[x][y].value = str(value(b))
        m[x][y].disabled = empty(b)

    def update_board():
        steps_summary.current.value = steps_string()
        blocks_map(update_value)

    def next_frame(e):
        nonlocal index
        if index < len(frames) - 1:
            index += 1
            update_board()
        if index == len(frames) - 1:
            steps_summary.current.color = "green"
            steps_summary.current.value = "Goal Reached!"
            page.update()

    def prev_frame(e):
        nonlocal index
        if index > 0:
            index -= 1
            steps_summary.current.color = "blue200"
            update_board()
    
    def auto_solve(e):
        for _ in frames[index::]:
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

    page.appbar = AppBar(
        title=Text("Sliding Puzzle", color=colors.BACKGROUND, weight="bold"),
        center_title=True, bgcolor="blue200", toolbar_height=70,
        actions=[theme_button])
            
    page.add(Row([
        Column([
                # the TextField matrix that displays the board
                *[Row([txt for txt in row],alignment="center")for row in blocks],

                Container(height=10),

                Row([Row(ref=frame_switcher, controls=[
                        OutlinedButton("Previous", on_click=prev_frame, expand=1),
                
                        FilledButton("Next", on_click=next_frame, expand=1),
                
                        ElevatedButton("Auto Solve", on_click=auto_solve, expand=2)
                    ], alignment="center", width=frame_switcher_width())], alignment="center"),       

        ], alignment="center", horizontal_alignment="center"),

            Column([
                Dropdown(
                    width=TT_WIDTH,
                    height=57, border_radius=10, border_width=0, content_padding=16,
                    value="A*", filled = True, alignment=alignment.center,
                    options=[
                        dropdown.Option("A*"),
                        dropdown.Option("GBFS"),
                        dropdown.Option("DFS"),
                        dropdown.Option("BFS"),
                    ]),
                
                ElevatedButton("Import", disabled=True, height=58, width=TT_WIDTH,
                    style=ButtonStyle(shape=RoundedRectangleBorder(radius=10))),

                ElevatedButton("Randomize", disabled=True, height=59, width=TT_WIDTH,
                    style=ButtonStyle(shape=RoundedRectangleBorder(radius=10))),

                Container(Column([
                            Text("Action:", weight="bold"),
                            Text("Right")
                        ], spacing=3, alignment="center"),
                    height=58),

                Container(Column([
                            Text("Heuristic:", weight="bold"),
                            Text("6")
                        ], spacing=3, alignment="center"),
                    height=59),

                Container(Column([
                            Text("Step:", weight="bold"),
                            Text(ref=steps_summary, color="blue200",weight="bold"),
                        ], spacing=3, alignment="center"),
                    height=62),

                ElevatedButton("Solve", disabled=True, height=59, width=TT_WIDTH,
                    style=ButtonStyle(shape=RoundedRectangleBorder(radius=10))),
            ], ref=tooltips, height=page.window_height, wrap=True, spacing=8)

        ],alignment="center", vertical_alignment="start"))

    steps_summary.current.value = steps_string()
    page.update()

if frames: app(target=gui, port=8080)
