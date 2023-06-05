def go_back_checker(index, path_list):
    back_count = 0
    for element in path_list[index:]:
        if element != "..":
            break
        back_count += 1
    return back_count

def simplify_path(path):
    index = 0
    length = len(path)
    try:
        while index < length:
            if path[index] == ".":
                path.pop(index)
                continue
            elif path[index] == "..":
                back_count = go_back_checker(index, path)
                desired_len = len(path) - (2 * back_count)
                while len(path) != desired_len:
                    path.pop(index-back_count)
                continue
            index += 1
    except:
        path = "/".join(path)
    return path
