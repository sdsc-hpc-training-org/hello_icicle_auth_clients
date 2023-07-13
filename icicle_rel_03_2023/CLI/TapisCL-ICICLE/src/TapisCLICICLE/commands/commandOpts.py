class CHECK_EXPLICIT_ID:
    def __init__(self, arg_name: str):
        self.arg_name = arg_name
    
    def __call__(self, kwargs):
        if self.arg_name not in kwargs or not kwargs[self.arg_name]:
            kwargs[self.arg_name] = kwargs['connection'].system
        return kwargs


class CHECK_PWD:
    """
    support the invocation of relative paths for tapis systems
    """
    def __init__(self, dir_simplify_args: tuple):
        self.dir_simplify_args = dir_simplify_args

    def __go_back_checker(self, index: int, path_list: list):
        back_count = 0
        for element in path_list[index:]:
            if element != "..":
                break
            back_count += 1
        return back_count

    def __simplify_path(self, path: list):
        index = 0
        length = len(path)
        try:
            while index < length:
                if path[index] == ".":
                    path.pop(index)
                    continue
                elif path[index] == "..":
                    back_count = self.__go_back_checker(index, path)
                    desired_len = len(path) - (2 * back_count)
                    while len(path) != desired_len:
                        path.pop(index-back_count)
                    continue
                index += 1
        except IndexError:
            pass
        finally:
            path = "/".join(path)
            if not path:
                path = "/"
        return path
    
    def __relative_to_absolute(self, absolute_path: str, relative_path: str):
        if not relative_path:
            return absolute_path
        elif absolute_path[-1] == "/":
            return f"{absolute_path}{relative_path}"
        return f"{absolute_path}/{relative_path}"

    def __call__(self, kwargs):
        for file_argument_name in self.dir_simplify_args:
            if not kwargs[file_argument_name] or kwargs['connection'].pwd not in kwargs[file_argument_name]:
                file = self.__relative_to_absolute(kwargs['connection'].pwd, kwargs[file_argument_name])
                kwargs[file_argument_name] = self.__simplify_path(file.split("/"))
        return kwargs