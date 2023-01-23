import glfw

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