import glfw
import OpenGL.GL as gl

def swap_right(state, slot_coords):
    slot_x, slot_y = slot_coords
    # swap the slot with the block on its left in the row
    state[slot_y, slot_x], state[slot_y, slot_x - 1] = (
        state[slot_y, slot_x - 1],
        state[slot_y, slot_x],
    )
    return state


def swap_left(state, slot_coords):
    slot_x, slot_y = slot_coords
    # swap the slot with the block on its right in the row
    state[slot_y, slot_x], state[slot_y, slot_x + 1] = (
        state[slot_y, slot_x + 1],
        state[slot_y, slot_x],
    )
    return state


def swap_up(state, slot_coords):
    slot_x, slot_y = slot_coords
    # swap the slot with the block below it in the same column
    state[slot_y, slot_x], state[slot_y + 1, slot_x] = (
        state[slot_y + 1, slot_x],
        state[slot_y, slot_x],
    )
    return state


def swap_down(state, slot_coords):
    slot_x, slot_y = slot_coords
    # swap the slot with the block above it in the same column
    state[slot_y, slot_x], state[slot_y - 1, slot_x] = (
        state[slot_y - 1, slot_x],
        state[slot_y, slot_x],
    )
    return state


def impl_glfw_init(size):
    width, height = 500, 500
    window_name = "minimal ImGui/GLFW3 example"

    if not glfw.init():
        print("Could not initialize OpenGL context")
        exit(1)

    # OS X supports only forward-compatible core profiles from 3.2
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(
        int(width), int(height), window_name, None, None
    )
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        exit(1)

    return window

