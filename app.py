from flet import *
from main import *

def gui(page: Page):
    index = 0
    page.title = "Flet Sliding Puzzle"
    page.vertical_alignment = "center"

    value = lambda s: s if s!=PLACEHOLDER else SLOT
    block_width_or = lambda x: x if not (pw:=page.window_width) else 0.9*pw / width
    FALLBACK_WIDTH = 100

    steps_summary = Ref[Text]()
    steps_string = lambda: f"step {index+1} of {len(frames)}"

    page.on_resize = lambda e: blocks_map(update_width)

    blocks = [[ # the TextField matrix to display the puzzle
            TextField(value=value(block),
            text_align="center", width=block_width_or(FALLBACK_WIDTH), disabled=True)
            for block in row
        ] for row in frames[index]]

    def blocks_map(fn):
        nonlocal blocks
        for (x, y), block in np.ndenumerate(frames[index]):
            fn(x, y, block, blocks)
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
            steps_summary.current.value = "the goal!"
            page.update()

    def prev_frame(e):
        nonlocal index
        if index > 0:
            index -= 1
            update_board()

    page.add(*[Row([
                txt for txt in row
            ], alignment="center")
            for row in blocks])

    page.add(Row([
                ElevatedButton("Previous", on_click=prev_frame),
                ElevatedButton("Next", on_click=next_frame)
            ], alignment="center"))

    page.add(Row([Text(ref=steps_summary, color="green400")], alignment="center"))
    steps_summary.current.value = steps_string()
    page.update()

if (frames): app(target=gui, port=8550)