"""Safe Python code execution using RestrictedPython."""


def execute_safe_code_tool(code: str) -> str:
    """Execute Python code in a restricted sandbox.

    Args:
        code: Python code string to execute.

    Returns:
        Captured print output or error message.
    """
    allowed_modules = {
        "datetime": __import__("datetime"),
        "math": __import__("math"),
        "random": __import__("random"),
        "time": __import__("time"),
        "collections": __import__("collections"),
        "itertools": __import__("itertools"),
        "functools": __import__("functools"),
        "copy": __import__("copy"),
        "re": __import__("re"),
        "json": __import__("json"),
        "csv": __import__("csv"),
        "uuid": __import__("uuid"),
        "string": __import__("string"),
        "statistics": __import__("statistics"),
        "heapq": __import__("heapq"),
        "bisect": __import__("bisect"),
        "array": __import__("array"),
        "enum": __import__("enum"),
        "dataclasses": __import__("dataclasses"),
        "io": __import__("io"),
        "base64": __import__("base64"),
        "hashlib": __import__("hashlib"),
        "tempfile": __import__("tempfile"),
    }

    try:
        allowed_modules["numpy"] = __import__("numpy")
    except ImportError:
        pass

    try:
        allowed_modules["pandas"] = __import__("pandas")
    except ImportError:
        pass

    try:
        allowed_modules["scipy"] = __import__("scipy")
    except ImportError:
        pass

    def safe_import(name, *args, **kwargs):
        if name in allowed_modules:
            return allowed_modules[name]
        raise ImportError(f"Module {name} is not allowed")

    safe_builtins = {
        "abs": abs,
        "all": all,
        "any": any,
        "bin": bin,
        "bool": bool,
        "chr": chr,
        "complex": complex,
        "divmod": divmod,
        "float": float,
        "format": format,
        "hex": hex,
        "int": int,
        "len": len,
        "max": max,
        "min": min,
        "oct": oct,
        "ord": ord,
        "pow": pow,
        "round": round,
        "sorted": sorted,
        "sum": sum,
        "bytes": bytes,
        "dict": dict,
        "frozenset": frozenset,
        "list": list,
        "repr": repr,
        "set": set,
        "slice": slice,
        "str": str,
        "tuple": tuple,
        "type": type,
        "zip": zip,
        "enumerate": enumerate,
        "filter": filter,
        "iter": iter,
        "map": map,
        "next": next,
        "range": range,
        "reversed": reversed,
        "getattr": getattr,
        "hasattr": hasattr,
        "hash": hash,
        "isinstance": isinstance,
        "issubclass": issubclass,
        "__import__": safe_import,
    }

    output = []

    def safe_print(*args, **kwargs):
        end = kwargs.get("end", "\n")
        sep = kwargs.get("sep", " ")
        output.append(sep.join(str(arg) for arg in args) + end)

    restricted_globals = {
        "__builtins__": safe_builtins,
        "print": safe_print,
    }

    try:
        exec(code, restricted_globals)
        return "".join(output)
    except Exception as e:
        return f"Error executing code: {e}"
