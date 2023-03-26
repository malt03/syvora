import llvmlite.ir as ir
import ctypes
from syvora.ast_creator import *
from .llvm_type_from_syvora_type import llvm_type_from_syvora_type
from .symbol_table import SymbolTable


class LLVMIRGenerator:

    def __init__(self):
        self.module = ir.Module(name="syvora_module")
        self.symbol_table = SymbolTable()

    def add_print_function(self):
        printf_type = ir.FunctionType(ir.IntType(
            32), [ir.PointerType(ir.IntType(8))], var_arg=True)
        printf = ir.Function(self.module, printf_type, name="printf")

        print_function_type = ir.FunctionType(ir.VoidType(), [ir.IntType(64)])
        print_function = ir.Function(
            self.module, print_function_type, 'pring_arg')

        block = print_function.append_basic_block('entry')
        builder = ir.IRBuilder(block)

        format_string = ir.Constant(ir.ArrayType(
            ir.IntType(8), 4), bytearray("%d\n\00", "utf8"))
        format_string_ptr = ir.GlobalVariable(
            self.module, format_string.type, ".str")
        format_string_ptr.linkage = 'private'
        format_string_ptr.global_constant = True
        format_string_ptr.initializer = format_string

        integer_value = print_function.args[0]
        builder.call(printf, [builder.bitcast(
            format_string_ptr, ir.PointerType(ir.IntType(8))), integer_value])

        builder.ret_void()

        dummy = FunctionDeclaration(
            "pring_arg", [Argument(Identifier("arg"), AccessibleTypeExpression("Int", None))], None, Block([], None))
        self.symbol_table.insert("print_arg", (dummy, print_function))

    def visit(self, node):
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"No visit_{node.__class__.__name__} method")

    def visit_Module(self, node: Module):
        self.add_print_function()

        for function in node.functions:
            self.visit(function)

    def visit_FunctionCallExpression(self, node: FunctionCallExpression):
        func_name = node.low_level_func_name()
        function_tuple: tuple[FunctionDeclaration,
                              ir.Function] = self.symbol_table.lookup(func_name)

        if function_tuple is None:
            raise ValueError(f"Function '{node.function_name}' is not defined")

        function_node, function = function_tuple

        arg_values = []
        for i, (arg_name, arg_expr) in enumerate(node.arguments):
            if function_node.arguments[i].identifier.name != arg_name:
                raise ValueError(
                    f"Argument '{arg_name}' does not match '{function_node.arguments[i].identifier.name}'")
            arg_value = self.visit(arg_expr)
            arg_values.append(arg_value)

        if node.children is not None:
            for child_expr in node.children:
                self.visit(child_expr)

        result = self.builder.call(function, arg_values)
        return result

    def visit_FunctionDeclaration(self, node: FunctionDeclaration):
        func_name = node.low_level_func_name()

        ret_type = llvm_type_from_syvora_type(
            node.return_type, self.symbol_table)
        arg_types = [llvm_type_from_syvora_type(
            arg.type, self.symbol_table) for arg in node.arguments]
        func_type = ir.FunctionType(ret_type, arg_types)
        llvm_function = ir.Function(self.module, func_type, func_name)

        entry_block = llvm_function.append_basic_block('entry')
        self.builder = ir.IRBuilder(entry_block)

        self.symbol_table.enter_scope()
        for i, arg in enumerate(llvm_function.args):
            arg.name = node.arguments[i].identifier
            alloca = self.builder.alloca(arg.type, name=arg.name)
            self.builder.store(arg, alloca)
            self.symbol_table.insert(arg.name, alloca)

        self.visit(node.body)

        if (node.return_type == None) != (node.body.return_expression == None):
            raise RuntimeError(
                f"Function '{func_name}' must have a return statement.")

        if node.body.return_expression != None:
            self.builder.ret(self.visit(node.body.return_expression))

        self.symbol_table.exit_scope()

        self.symbol_table.insert(func_name, (node, llvm_function))

        return llvm_function

    def visit_Block(self, node: Block) -> None:

        self.symbol_table.enter_scope()

        for statement in node.statements:
            self.visit(statement)

        self.symbol_table.exit_scope()

    def visit_BinaryExpression(self, node: BinaryExpression):
        left = self.visit(node.left)
        right = self.visit(node.right)

        if node.operator == "+":
            return self.builder.add(left, right)
        elif node.operator == "-":
            return self.builder.sub(left, right)
        elif node.operator == "*":
            return self.builder.mul(left, right)
        elif node.operator == "/":
            return self.builder.sdiv(left, right)

    def visit_LiteralExpression(self, node: LiteralExpression):
        if node.literal_type == TokenType.INTEGER_LITERAL:
            return ir.Constant(ir.IntType(64), int(node.value))
        elif node.literal_type == TokenType.FLOAT_LITERAL:
            return ir.Constant(ir.FloatType(), float(node.value))
        elif node.literal_type == TokenType.BOOLEAN_LITERAL:
            return ir.Constant(ir.IntType(1), 1 if node.value == True else 0)
        else:
            raise RuntimeError(f"Unexpected literal type: {node.literal_type}")

    def run_function(self, engine):
        main_function = self.module.get_global('main')
        if not main_function:
            raise RuntimeError("main function not found in the module")

        func_ptr = engine.get_function_address(str(main_function.name))
        cfunc = ctypes.CFUNCTYPE(None)(func_ptr)
        cfunc()
