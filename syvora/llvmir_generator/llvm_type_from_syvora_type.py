from llvmlite import ir
from syvora.ast_creator import AccessibleTypeExpression
from .symbol_table import SymbolTable


def llvm_type_from_syvora_type(t: AccessibleTypeExpression, symbol_table: SymbolTable) -> ir.Type:
    if t.child == None:
        if t.name == "Int":
            return ir.IntType(64)
        elif t.name == "Float":
            return ir.DoubleType()
        elif t.name == "Bool":
            return ir.IntType(1)

    raise TypeError(f"Unknown type: {t}")
