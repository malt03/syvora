import sys
from llvmlite import binding as llvm
from llvmlite.binding.module import parse_assembly
from .ast_creator import createAst
from .llvmir_generator import LLVMIRGenerator


def main():
    if len(sys.argv) < 2:
        print("Usage: syvora <filename>")
        return

    file_path = sys.argv[1]
    with open(file_path, "r") as file:
        source_code = file.read()

    ast = createAst(source_code, file_path)

    # print(ast)

    llvm_ir_generator = LLVMIRGenerator()
    llvm_ir_generator.visit(ast)

    print(str(llvm_ir_generator.module))

    # llvm.initialize()
    # llvm.initialize_native_target()
    # llvm.initialize_native_asmprinter()

    # target_machine = llvm.Target.from_default_triple().create_target_machine()
    # llvm_module = parse_assembly(str(llvm_ir_generator.module))
    # engine = llvm.create_mcjit_compiler(llvm_module, target_machine)

    # llvm_ir_generator.run_function(engine)


if __name__ == "__main__":
    main()
