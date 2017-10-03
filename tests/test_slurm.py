import unittest
import logging

from bioscons import slurm

log = logging


class TestSlurmFunctions(unittest.TestCase):

    def test_check_slurm(self):
        srun = slurm.check_srun()
        print(srun)
        if srun:
            self.assertTrue(srun.endswith('srun'))

    def test_quote(self):
        strings = [
            ('', "''"),
            (' ', "' '"),
        ]

        for unquoted, quoted in strings:
            self.assertEqual(slurm._quote(unquoted), quoted)
