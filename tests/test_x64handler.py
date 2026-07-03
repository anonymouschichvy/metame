import unittest
import sys
import os

# Add metame to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from metame.x64handler import X64Handler

class TestX64Handler(unittest.TestCase):
    def test_init_32bit(self):
        handler = X64Handler(bits=32)
        self.assertEqual(handler.bits, 32)
        self.assertIn("mov", handler.X64_SUBS)
        self.assertIn("nop", handler.X64_SUBS)
        self.assertIn("test", handler.X64_SUBS)
        self.assertIn("xor", handler.X64_SUBS)

    def test_init_64bit(self):
        handler = X64Handler(bits=64)
        self.assertEqual(handler.bits, 64)
        self.assertIn("mov", handler.X64_SUBS)
        self.assertIn("nop", handler.X64_SUBS)
        self.assertIn("test", handler.X64_SUBS)
        self.assertIn("xor", handler.X64_SUBS)

    def test_get_nops_32bit(self):
        handler = X64Handler(bits=32)
        # Size 1
        nops = handler.get_nops(1)
        self.assertEqual(nops, "nop")
        
        # Size 2
        for _ in range(20):
            nops = handler.get_nops(2)
            valid_nops = [
                "push eax; pop eax", "push ebx; pop ebx", 
                "push ecx; pop ecx", "push edx; pop edx",
                "push esi; pop esi", "push edi; pop edi",
                "pushad; popad", "nop; nop", "xchg ax, ax"
            ]
            self.assertTrue(nops in valid_nops or any(reg in nops for reg in ["eax", "ebx", "ecx", "edx", "esi", "edi"]))

    def test_get_nops_64bit(self):
        handler = X64Handler(bits=64)
        # Size 1
        nops = handler.get_nops(1)
        self.assertEqual(nops, "nop")
        
        # Size 2
        for _ in range(20):
            nops = handler.get_nops(2)
            self.assertTrue(
                nops in ["xchg ax, ax", "nop; nop"] or
                any(reg in nops for reg in ["rax", "rbx", "rcx", "rdx", "rsi", "rdi"])
            )

    def test_replace_fcn_opcodes_32bit(self):
        handler = X64Handler(bits=32, force_replace=True)
        fcn_ctx = {
            "ops": [
                {"opcode": "mov eax, eax", "bytes": "89c0", "offset": 1000, "type": "mov"},
                {"opcode": "nop", "bytes": "90", "offset": 1002, "type": "nop"},
                {"opcode": "nop", "bytes": "90", "offset": 1003, "type": "nop"},
                {"opcode": "test eax, eax", "bytes": "85c0", "offset": 1004, "type": "acmp"},
                {"opcode": "xor ebx, ebx", "bytes": "31db", "offset": 1006, "type": "xor"},
            ]
        }
        replacements = handler.replace_fcn_opcodes(fcn_ctx)
        self.assertGreater(len(replacements), 0)
        
        for rep in replacements:
            new_bytes = rep["newbytes"]
            self.assertEqual(len(new_bytes), 4)

    def test_replace_fcn_opcodes_64bit(self):
        handler = X64Handler(bits=64, force_replace=True)
        fcn_ctx = {
            "ops": [
                {"opcode": "mov rax, rax", "bytes": "4889c0", "offset": 2000, "type": "mov"},
                {"opcode": "test rbx, rbx", "bytes": "4885db", "offset": 2003, "type": "acmp"},
                {"opcode": "xor rcx, rcx", "bytes": "4831c9", "offset": 2006, "type": "xor"},
            ]
        }
        replacements = handler.replace_fcn_opcodes(fcn_ctx)
        self.assertGreater(len(replacements), 0)
        
        for rep in replacements:
            new_bytes = rep["newbytes"]
            self.assertEqual(len(new_bytes), 6)

    def test_normalize_opcode(self):
        handler = X64Handler(bits=32)
        self.assertEqual(handler.normalize_opcode("  MOV EAX,EBX  "), "mov eax, ebx")
        self.assertEqual(handler.normalize_opcode("test\teax,\t\teax"), "test eax, eax")
        self.assertEqual(handler.normalize_opcode("xor    ecx,   ecx"), "xor ecx, ecx")
        self.assertEqual(handler.normalize_opcode("nop"), "nop")

    def test_replace_fcn_opcodes_robustness(self):
        handler = X64Handler(bits=32, force_replace=True)
        fcn_ctx = {
            "ops": [
                {"opcode": "  MOV  EAX,EBX  ", "bytes": "89d8", "offset": 1000, "type": "mov"},
                {"opcode": "XOR\tECX,\t\tECX", "bytes": "31c9", "offset": 1002, "type": "xor"},
            ]
        }
        replacements = handler.replace_fcn_opcodes(fcn_ctx)
        self.assertGreater(len(replacements), 0)
        for rep in replacements:
            self.assertEqual(len(rep["newbytes"]), 4)

    def test_replace_fcn_opcodes_advanced(self):
        handler = X64Handler(bits=32, force_replace=True)
        # Test branch alias conversion, inc/dec swaps, and shl expansion
        fcn_ctx = {
            "ops": [
                {"opcode": "je 0x1000", "bytes": "74fe", "offset": 1000, "type": "cjmp"},
                {"opcode": "add eax, 1", "bytes": "83c001", "offset": 1002, "type": "add"},
                {"opcode": "shl ebx, 1", "bytes": "d1e3", "offset": 1005, "type": "shl"},
            ]
        }
        replacements = handler.replace_fcn_opcodes(fcn_ctx)
        self.assertGreater(len(replacements), 0)
        
        # Verify sizes are strictly conserved
        ops_dict = {op["offset"]: op for op in fcn_ctx["ops"]}
        for rep in replacements:
            offset = rep["offset"]
            orig_bytes = ops_dict[offset]["bytes"]
            new_bytes = rep["newbytes"]
            self.assertEqual(len(orig_bytes), len(new_bytes))

if __name__ == "__main__":
    unittest.main()
