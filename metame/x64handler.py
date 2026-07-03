import re
import random
from typing import Dict, List, Tuple, Set, Pattern, Optional, Any
from keystone import *

class X64Handler:
    def get_nops(self, size: int, prev_ins_size: int = 0) -> str:
        if self.bits == 32:
            regs = ["eax", "ebx", "ecx", "edx", "esi", "edi"]
        else:
            regs = ["rax", "rbx", "rcx", "rdx", "rsi", "rdi"]

        if size == 1:
            return "nop"
        elif size == 2:
            if self.bits == 32:
                r = random.randint(1, 3)
                if r == 1:
                    reg = random.choice(regs)
                    return f"push {reg}; pop {reg}"
                elif r == 2:
                    return "pushad; popad"
                else:
                    return "nop; nop"
            else:
                reg = random.choice(regs)
                return f"push {reg}; pop {reg}"
        elif size == 3:
            if self.bits == 32:
                r = random.randint(1, 5)
                if r == 1:
                    return f"jmp {3 + prev_ins_size}; inc {random.choice(regs)}"
                elif r == 2:
                    return f"jmp {3 + prev_ins_size}; push {random.choice(regs)}"
                elif r == 3:
                    return f"jmp {3 + prev_ins_size}; pop {random.choice(regs)}"
                elif r == 4:
                    return f"nop; {self.get_nops(2)}"
                else:
                    return f"{self.get_nops(2)}; nop"
            else:
                r = random.randint(1, 4)
                reg = random.choice(regs)
                if r == 1:
                    return f"push {reg}; pop {reg}; nop"
                elif r == 2:
                    return f"nop; push {reg}; pop {reg}"
                elif r == 3:
                    return f"nop; {self.get_nops(2)}"
                else:
                    return f"{self.get_nops(2)}; nop"
        elif size == 4:
            if self.bits == 64:
                r = random.randint(1, 5)
                if r == 1:
                    return f"jmp {4 + prev_ins_size}; pop {random.choice(regs)}; pop {random.choice(regs)}"
                elif r == 2:
                    return f"jmp {4 + prev_ins_size}; push {random.choice(regs)}; push {random.choice(regs)}"
                elif r == 3:
                    return f"jmp {4 + prev_ins_size}; push {random.choice(regs)}; pop {random.choice(regs)}"
                elif r == 4:
                    return f"jmp {4 + prev_ins_size}; pop {random.choice(regs)}; push {random.choice(regs)}"
                else:
                    return f"{self.get_nops(2)}; {self.get_nops(2)}"
            else:
                return "; ".join(["nop"] * size)
        
        return "; ".join(["nop"] * size)

    def __init__(self, bits: int, debug: bool = False, force_replace: bool = False):
        self.bits = bits
        self.debug = debug
        self.force = force_replace
        ks_mode = KS_MODE_32 if self.bits == 32 else KS_MODE_64
        self.ks = Ks(KS_ARCH_X86, ks_mode)
        self.init_mutations()

    def init_mutations(self):
        if self.bits == 32:
            self.mutables = frozenset(["nop", "acmp", "or", "xor", "sub", "mov", "push"])
            raw_subs = [
                (
                    ((r"^mov (?P<a>e..), (?P<b>(?P=a))$",), "mov {a}, {b}", True),
                    ((), "{nop2}", False),
                ),
                (
                    ((r"^nop$", r"^nop$", r"^nop$"), "nop; nop; nop", True),
                    ((), "{nop3}", False),
                ),
                (
                    ((r"^nop$", r"^nop$"), "nop; nop", True),
                    ((), "{nop2}", False),
                ),
                (
                    ((r"^test (?P<a>e..), (?P<b>(?P=a))$",), "test {a}, {b}", True),
                    ((r"^or (?P<a>e..), (?P<b>(?P=a))$",), "or {a}, {b}", True),
                ),
                (
                    ((r"^xor (?P<a>e..), (?P<b>(?P=a))$",), "xor {a}, {b}", True),
                    ((r"^sub (?P<a>e..), (?P<b>(?P=a))$",), "sub {a}, {b}", True),
                ),
                (
                    ((r"^mov (?P<a>e..), (?P<b>e..)$",), "mov {a}, {b}", True),
                    ((r"^push (?P<b>e..)$", r"^pop (?P<a>e..)$"), "push {b}; pop {a}", True),
                ),
                (
                    ((r"^mov (?P<a>e..), (?P<b>0?x?0)$",), "mov {a}, {b}", True),
                    ((), "pushfd; xor {a}, {a}; popfd; {nop1}", False),
                    ((), "pushfd; sub {a}, {a}; popfd; {nop1}", False),
                    ((), "pushfd; and {a}, 0; popfd", False),
                ),
                (
                    ((r"^mov (?P<a>e..), (?P<b>0?x?1)$",), "mov {a}, {b}", True),
                    ((), "pushfd; xor {a}, {a}; inc {a}; popfd", False),
                ),
                (
                    ((r"^mov (?P<a>e..), (?P<b>0?x?([0-7][0-9A-Fa-f]|[0-9A-Fa-f]))$",), "mov {a}, {b}", True),
                    ((), "push {b}; pop {a}; {nop2}", False),
                    ((), "{nop2}; push {b}; pop {a}", False),
                    ((), "{nop1}; push {b}; {nop1}; pop {a}", False),
                ),
            ]
        else:
            self.mutables = frozenset(["nop", "acmp", "or", "xor", "sub", "mov"])
            raw_subs = [
                # Variations of 32 bits payloads
                (
                    ((r"^mov (?P<a>e..), (?P<b>(?P=a))$",), "mov {a}, {b}", True),
                    ((), "{nop2}", False),
                ),
                (
                    ((r"^nop$", r"^nop$", r"^nop$"), "nop; nop; nop", True),
                    ((), "{nop3}", False),
                ),
                (
                    ((r"^nop$", r"^nop$"), "nop; nop", True),
                    ((), "{nop2}", False),
                ),
                (
                    ((r"^test (?P<a>e..), (?P<b>(?P=a))$",), "test {a}, {b}", True),
                    ((r"^or (?P<a>e..), (?P<b>(?P=a))$",), "or {a}, {b}", True),
                ),
                (
                    ((r"^xor (?P<a>e..), (?P<b>(?P=a))$",), "xor {a}, {b}", True),
                    ((r"^sub (?P<a>e..), (?P<b>(?P=a))$",), "sub {a}, {b}", True),
                ),
                # Purely 64 bits payloads
                (
                    ((r"^test (?P<a>r..), (?P<b>(?P=a))$",), "test {a}, {b}", True),
                    ((r"^or (?P<a>r..), (?P<b>(?P=a))$",), "or {a}, {b}", True),
                ),
                (
                    ((r"^xor (?P<a>r..), (?P<b>(?P=a))$",), "xor {a}, {b}", True),
                    ((r"^sub (?P<a>r..), (?P<b>(?P=a))$",), "sub {a}, {b}", True),
                ),
                (
                    ((r"^mov (?P<a>r.(i|x|p)), (?P<b>r.(i|x|p))$",), "mov {a}, {b}", True),
                    ((), "push {b}; pop {a}; {nop1}", False),
                    ((), "{nop1}; push {b}; pop {a}", False),
                    ((), "push {b}; {nop1}; pop {a}", False),
                ),
            ]

        # Compile and group substitution rules by the mnemonic of their first instruction
        self.X64_SUBS: Dict[str, List[Tuple[Tuple[Any, ...], Tuple[Any, ...]]]] = {}
        for sub_rule in raw_subs:
            compiled_rule = []
            for eq in sub_rule:
                patterns, asm_fmt, is_match = eq
                compiled_patterns = tuple(re.compile(p) for p in patterns)
                compiled_rule.append((compiled_patterns, asm_fmt, is_match))
            compiled_rule_tuple = tuple(compiled_rule)

            for eq in compiled_rule_tuple:
                compiled_patterns, asm_fmt, is_match = eq
                if is_match:
                    first_pattern = compiled_patterns[0].pattern
                    m = re.match(r"^\^([a-zA-Z0-9]+)", first_pattern)
                    if m:
                        mnemonic = m.group(1)
                        if mnemonic not in self.X64_SUBS:
                            self.X64_SUBS[mnemonic] = []
                        self.X64_SUBS[mnemonic].append((eq, compiled_rule_tuple))

    def assemble_code(self, codestr: str) -> str:
        encoding, count = self.ks.asm(codestr)
        return "".join(["%02x" % i for i in encoding])

    def replace_fcn_opcodes(self, fcn_ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
        replacements = []
        if not fcn_ctx or "ops" not in fcn_ctx:
            return replacements

        count = -1
        n_ops = len(fcn_ctx["ops"])
        while count < n_ops - 1:
            count += 1
            op = fcn_ctx["ops"][count]

            opcode_str = op.get("opcode", "")
            if not opcode_str:
                continue

            mnemonic = opcode_str.split()[0]
            if mnemonic not in self.X64_SUBS:
                continue

            candidates = self.X64_SUBS[mnemonic]
            for x86_find, x86_sub in candidates:
                count_2 = 0
                ms = []
                opcodes_len = 0
                match_failed = False

                for regex in x86_find[0]:
                    if count + count_2 >= n_ops:
                        match_failed = True
                        break

                    next_op = fcn_ctx["ops"][count + count_2]
                    next_opcode = next_op.get("opcode", "")
                    if not next_opcode:
                        match_failed = True
                        break

                    m = regex.match(next_opcode)
                    if not m:
                        match_failed = True
                        break

                    ms.append(m)
                    op_bytes = next_op.get("bytes", "")
                    opcodes_len += len(op_bytes)
                    count_2 += 1

                if match_failed:
                    continue

                sub = random.choice(x86_sub)
                if self.force:
                    for _ in range(10):
                        if sub == x86_find:
                            sub = random.choice(x86_sub)
                        else:
                            break

                if sub == x86_find:
                    continue

                res_ass = sub[1]
                for m in ms:
                    for idx, val in m.groupdict().items():
                        if val is not None:
                            res_ass = res_ass.replace(f"{{{idx}}}", val)

                # Dynamically resolve NOP placeholders
                def nop_resolver(match_obj):
                    nop_size = int(match_obj.group(1))
                    return self.get_nops(nop_size)

                res_ass = re.sub(r"\{nop(\d+)\}", nop_resolver, res_ass)

                if self.debug:
                    print(f"[DEBUG] Replacing instruction at {hex(op['offset'])} ({opcode_str}) with: {res_ass} ... ")

                try:
                    new_assembly = self.assemble_code(res_ass)
                except Exception as e:
                    if self.debug:
                        print(f"[DEBUG] Keystone assembly failed for '{res_ass}': {e}")
                    continue

                if len(new_assembly) == opcodes_len:
                    replacements.append({
                        "offset": op["offset"],
                        "newbytes": new_assembly
                    })
                    count += count_2 - 1
                    break
                else:
                    if self.debug:
                        print(f"[DEBUG] Instruction opcodes are different in size (new: {len(new_assembly)//2}, expected: {opcodes_len//2})")

        return replacements
