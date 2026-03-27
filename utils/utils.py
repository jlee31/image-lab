def push_undo(undo_stack, redo_stack, current_image, max_stack_size=20):
    undo_stack.append(current_image.copy())
    if len(undo_stack) > max_stack_size:
        undo_stack.pop(0)
    redo_stack.clear()

def undo(undo_stack, redo_stack, current_image):
    if undo_stack:
        redo_stack.append(current_image.copy())
        return undo_stack.pop()
    return current_image  

def redo(undo_stack, redo_stack, current_image):
    if redo_stack:
        undo_stack.append(current_image.copy())
        return redo_stack.pop()
    return current_image  