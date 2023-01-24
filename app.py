from flet import *
from main import np, time, frames, PLACEHOLDER, SLOT, WIDTH as BOARD_WIDTH

def gui(page: Page):
    index = 0
    page.title = "Sliding Puzzle"
    page.vertical_alignment = "center"
    buttons = Ref[Text]()

    width_equation = lambda: page.window_width * 0.7/(BOARD_WIDTH+0.7)
    block_width_or = lambda x, fn=width_equation: dyn if (dyn:=fn()) < x else x
    value = lambda s: s if s!=PLACEHOLDER else SLOT
    FALLBACK_WIDTH = 100
    blocks = [[ # the TextField matrix to display the puzzle
            TextField(
                value=value(block), text_align="center", dense=True,
                width=block_width_or(FALLBACK_WIDTH), disabled=True
            )
            for block in row
        ] for row in frames[index]]

    page.on_resize = lambda e: blocks_map(update_width)

    steps_summary = Ref[Text]()
    steps_string = lambda: f"Step {index+1} of {len(frames)}"

    def blocks_map(fn):
        nonlocal blocks
        for (x, y), block in np.ndenumerate(frames[index]):
            fn(x, y, block, blocks)
        buttons.current.width = 1.1*width_equation()
        page.update()

    def update_width(x, y, b, m): 
        m[x][y].width = block_width_or(FALLBACK_WIDTH)

    def update_value(x, y, b, m):
        m[x][y].value = str(value(b))

    def update_board():
        steps_summary.current.value = steps_string()
        blocks_map(update_value)

    def next_frame(e):
        nonlocal index
        if index < len(frames) - 1:
            index += 1
            update_board()
        if index == len(frames) - 1:
            steps_summary.current.color="green400"
            steps_summary.current.value = "Goal Reached!"
            page.update()

    def prev_frame(e):
        nonlocal index
        if index > 0:
            index -= 1
            steps_summary.current.color="white"
            update_board()
    
    def auto_solve(e):
        for _ in frames[index::]:
            next_frame(e)
            time.sleep(0.4)
            
    page.add(*[Row([
                txt for txt in row
            ], alignment="center")
            for row in blocks])

    page.add(Row([
                Row(ref=buttons, controls=[ElevatedButton("Previous", on_click=prev_frame, expand=1),
                ElevatedButton("Next", on_click=next_frame, expand=1),
                ElevatedButton("Auto Solve", on_click=auto_solve, expand=1)], alignment="center", width=page.window_width * 0.73)
            ], alignment="center"))

    page.add(Row([Text(ref=steps_summary, color="white")], alignment="center"))
    steps_summary.current.value = steps_string()
    page.update()

if (frames): app(target=gui, port=8550)