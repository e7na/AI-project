import glfw
import OpenGL.GL as gl
from imgui.integrations.glfw import GlfwRenderer
import imgui

def impl_glfw_init(title, size):
    width, height = size
    # title = "minimal ImGui/GLFW3 example"

    if not glfw.init():
        print("Could not initialize OpenGL context")
        exit(1)

    glfw.window_hint(glfw.FOCUSED, glfw.FALSE)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    # glfw.window_hint(glfw.RESIZABLE, 1)
    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, 1)
    glfw.window_hint(glfw.SCALE_TO_MONITOR, 1)
    glfw.window_hint(glfw.DECORATED, 0)
    # glfw.window_hint(glfw.VISIBLE, 0)
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(int(width), int(height), title, None, None)
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        exit(1)

    return window


def display_sol(frames, initial=0):
    idx = initial
    size = 500, 500

    gl.glClearColor(1, 1, 1, 1)
    imgui.create_context()
    window = impl_glfw_init("Sliding puzzle", size)
    impl = GlfwRenderer(window)

    while not glfw.window_should_close(window):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        glfw.poll_events()
        impl.process_inputs()
        # io = imgui.get_io()
        frame = frames[idx]
        imgui.new_frame()
        _, keep_window_open = imgui.begin(
            "Board",
            closable=True,
        )
        imgui.columns(width)
        for row in frame:
            imgui.separator()
            for block in row:
                imgui.text(str(block) if block != PLACEHOLDER else SLOT)
                imgui.next_column()
        imgui.columns(1)
        imgui.separator()

        imgui.spacing() ; imgui.spacing()
        match [idx, imgui.button("Back"), imgui.same_line(), imgui.button("Next")]:
            case [index, _, _, True] if index < len(frames) - 1:
                idx += 1
            case [index, True, _, _] if index > 0:
                idx -= 1
        imgui.end()
        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)
        if not keep_window_open:
            glfw.set_window_should_close(window, True)
    impl.shutdown()
    glfw.terminate()