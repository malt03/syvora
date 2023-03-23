from typing import Optional, Any


class SymbolTable:
    def __init__(self):
        self.scopes = [{}]

    def insert(self, name: str, value: Any) -> None:
        self.scopes[-1][name] = value

    def lookup(self, name: str) -> Optional[Any]:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def enter_scope(self) -> None:
        self.scopes.append({})

    def exit_scope(self) -> None:
        self.scopes.pop
