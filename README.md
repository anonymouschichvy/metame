# 🌀 metame

> A highly optimized metamorphic code mutation engine for arbitrary executables (x86/x64).

[![Python Support](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.5-green.svg)](setup.py)

---

## 💡 What is Metamorphic Code?

> **Metamorphic code** is code that, when run or compiled, outputs a logically equivalent version of itself. In cybersecurity, this technique is typically used to evade signature-based detection mechanisms (like anti-virus pattern recognition) by ensuring the binary looks completely different on every generation while retaining the exact same logic and functionality.

---

## ✨ Features

- **🚀 Highly Optimized Execution**:
  - **$O(1)$ Mnemonic Indexing**: Grouping substitution rules by opcode mnemonics for instant lookup instead of scanning linear lists.
  - **Dynamic NOP Replacement**: Generates random NOP sequences dynamically on-the-fly rather than rebuilding/recompiling patterns inside hot-paths.
  - **🛡️ Flag & Register Safe NOPs**: Leverages native CPU multi-byte NOPs (e.g. `nop dword ptr [rax]`) and relative branch jumps to guarantee EFLAGS/RFLAGS stability and prevent register contamination.
  - **📏 Correct Size-Constrained Mutators**: Resolves 64-bit REX instruction size expansions and relative branch jumps to ensure strict instruction-size preservation during mutation.
- **🖥️ Architecture Support**: Fully supports **x86 (32-bit)** and **x64 (64-bit)** instructions.
- **📦 Multi-Format Support**: Leverages [radare2](http://radare.org/) for file parsing and assembly analysis, supporting PE, ELF, Mach-O, and more.
- **🛡️ Safe Assembler Execution**: Exception boundaries around the Keystone assembler ensure stability.

---

## ⚙️ How It Works

```mermaid
graph TD
    A["Open Binary via Radare2"] --> B["Analyze Code / Functions"]
    B --> C["O(1) Mnemonic-Indexed Rule Lookup"]
    C --> D["Randomly Replace Instructions keeping logic & size"]
    D --> E["Dynamically Generate NOPs"]
    E --> F["Patch Original Binary using Radare2"]
    F --> G["Generate Mutated Variant"]
```

1. **Disassemble & Analyze**: Opens the input executable with `radare2` to load symbol metadata and function offsets.
2. **Mutate Opcodes**: Scans each instruction, instantly queries candidate replacement patterns, and chooses a random matching sequence of equivalent size.
3. **Patch & Save**: Copies the original file and overwrites the target instruction offsets with the newly assembled metamorphic bytes.

---

## 📊 Mutation Examples

### Example 1: Instruction Mutation
*Can you spot the difference between the original and mutated assembly?*

![Spot the differences](https://raw.githubusercontent.com/a0rtega/metame/master/screens/screen1.png)

> [!TIP]
> Two instructions were replaced in the snippet above to modify signature bytes while preserving behavior.

### Example 2: NOP Sled Refactoring
*Mutating static NOP sleds into a variety of random operations.*

![Spot the differences](https://raw.githubusercontent.com/a0rtega/metame/master/screens/screen2.png)

---

## 🚀 Installation

### From PyPI
```bash
pip install metame
```

### From Source (Local Development)
Navigate to the root directory of the project and run one of the following commands:

**Developer Mode (Recommended)**:
Installs the package in editable mode. Any changes to the source code are reflected immediately without re-installing:
```bash
pip install -e .
```

**Regular Local Install**:
```bash
pip install .
```

### Prerequisites
- **[radare2](http://radare.org/)**: Used for binary analysis. Please make sure it is installed and available on your system's `PATH`.
- **`simplejson`** (Optional performance boost):
  ```bash
  pip install simplejson
  ```

---

## 📖 Usage

Run the engine from the command line:

```bash
metame -i original.exe -o mutation.exe -d
```

### Options
- `-i`, `--input`: Path to the input file to mutate.
- `-o`, `--output`: Path to save the mutated file.
- `-d`, `--debug`: Print detailed replacement logs.
- `-f`, `--force`: Force instruction replacement even if it reduces metamorphism entropy.

Use `metame -h` for a full list of commands.

---

## 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.
