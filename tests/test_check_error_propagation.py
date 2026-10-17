import unittest

from tools.check_error_propagation import check_error_propagation, ft_score


class CheckErrorPropagationTests(unittest.TestCase):
    def assert_same_faults(self, left, right, data=(0, 1, 2), flags=()):
        self.assertEqual(
            check_error_propagation(left, list(data), list(flags)),
            check_error_propagation(right, list(data), list(flags)),
        )

    def test_nested_repeats_match_unrolled_circuit(self):
        self.assert_same_faults(
            "H 0\nREPEAT 2 {\nCX 0 1\nREPEAT 2 {\nH 1\n}\n}",
            "H 0\nCX 0 1\nH 1\nH 1\nCX 0 1\nH 1\nH 1",
        )

    def test_packed_swaps_match_separate_operations(self):
        self.assert_same_faults("SWAP 0 1 1 2", "SWAP 0 1\nTICK\nSWAP 1 2")

    def test_packed_single_qubit_cliffords_match_separate_operations(self):
        self.assert_same_faults("H_XY 0 1\nCX 0 1", "H_XY 0\nTICK\nH_XY 1\nCX 0 1")

    def test_annotations_do_not_create_fault_sites(self):
        self.assert_same_faults(
            "QUBIT_COORDS(1, 2) 0\nH 0\nCX 0 1\nTICK\nM 2\n"
            "DETECTOR rec[-1]\nSHIFT_COORDS(0, 1)\nOBSERVABLE_INCLUDE(0) rec[-1]",
            "H 0\nCX 0 1\nM 2",
        )

    def test_fault_between_packed_pairs_can_spread(self):
        circuit = "SQRT_XX 0 1 1 2"
        rows = check_error_propagation(circuit, [0, 1, 2], [])
        fault = next(r for r in rows if r["loc"] == 0 and r["fault_qubit"] == 1 and r["fault_pauli"] == "Z")
        self.assertEqual(fault["final_paulis"], {0: "I", 1: "Y", 2: "X"})
        self.assertEqual(fault["data_weight"], 2)
        self.assertEqual(ft_score(circuit, [0, 1, 2], [], d=3), 0.0)


if __name__ == "__main__":
    unittest.main()
