from flet import *
from main import np, time, frames, PLACEHOLDER, SLOT, WIDTH as BOARD_WIDTH

def gui(page: Page):
    
    page.title = "Sliding Puzzle"
    page.vertical_alignment = "center"
    page.on_resize = lambda e: blocks_map(update_width)
    #Define a Starting Window Size
    page.window_width = 500
    page.window_height = 720
    page.window_min_width = 500
    page.window_min_height = 700
    #page.appbar = AppBar(title=Text("Sliding Puzzle", color=colors.BACKGROUND, weight="bold"), center_title=True, bgcolor="blue200",toolbar_height=70)
    index = 0
    buttons = Ref[Text]()
    steps_summary = Ref[Text]()
    steps_string = lambda: f"Step {index+1} of {len(frames)}"
    width_equation = lambda: page.window_width * 0.7/(BOARD_WIDTH)
    block_width_or = lambda x, fn=width_equation: dyn if (dyn:=fn()) < x else x
    value = lambda s: s if s!=PLACEHOLDER else SLOT
    empty = lambda s: True if s!=PLACEHOLDER else False
    FALLBACK_WIDTH = 150
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
        page.update()

    button_width = lambda: (BOARD_WIDTH+0.3)*block_width_or(FALLBACK_WIDTH)
    def update_width(x, y, b, m): 
        m[x][y].width = block_width_or(FALLBACK_WIDTH)
        buttons.current.width = button_width()

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
            steps_summary.current.color="green"
            steps_summary.current.value = "Goal Reached!"
            page.update()

    def prev_frame(e):
        nonlocal index
        if index > 0:
            index -= 1
            steps_summary.current.color="blue200"
            update_board()
    
    def auto_solve(e):
        for _ in frames[index::]:
            next_frame(e)
            time.sleep(0.4)
            
    page.add(*[Row([
                txt for txt in row
            ], alignment="center")
        for row in blocks])

    page.add(Container(height = 10), Row([Row(ref=buttons, controls=[
                OutlinedButton("Previous", on_click=prev_frame, expand=1),
                FilledButton("Next", on_click=next_frame, expand=1),
                ElevatedButton("Auto Solve", on_click=auto_solve, expand=2)
            ], alignment="center",
            width=button_width())],
        alignment="center"))

    page.add(Container(height = 5), Row([
            Text(ref=steps_summary, color="blue200", weight="bold")
        ], alignment="center"))

    steps_summary.current.value = steps_string()
    page.update()

if (frames): app(target=gui, port=8080)