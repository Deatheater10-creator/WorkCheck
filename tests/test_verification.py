import unittest
import sympy as sp
from workcheck.parser import X, parse_expression
from workcheck.verification import domain_of, verify


class VerificationTests(unittest.TestCase):
    def test_equivalent_expanded_and_factored(self):
        p = parse_expression("2*x*(x+1)+x^2")
        self.assertEqual(verify(p, 3*X**2+2*X, sp.S.Reals).status, "proved")

    def test_trigonometric_identity(self):
        self.assertEqual(verify(parse_expression("sin(x)^2+cos(x)^2"), 1, sp.S.Reals).status, "proved")

    def test_domain_hole_not_lost(self):
        p = parse_expression("(x-1)/(x-1)")
        self.assertEqual(domain_of(p).contains(1), sp.S.false)
        self.assertEqual(verify(p, 1, sp.S.Reals).status, "unknown")

    def test_cancellation_can_broaden_candidate_domain(self):
        source = parse_expression("(x-1)/(x-1)")
        self.assertEqual(verify(parse_expression("1"), 1, domain_of(source)).status, "proved")

    def test_log_domain(self):
        self.assertEqual(domain_of(parse_expression("ln(x)")), sp.Interval.open(0, sp.oo))
        self.assertEqual(domain_of(parse_expression("ln(x^2+1)")), sp.S.Reals)

    def test_unproved_domain_returns_unknown(self):
        self.assertEqual(verify(parse_expression("ln(sin(x))"), 0, sp.S.Reals).status, "unknown")

    def test_near_equality_is_not_proof(self):
        self.assertEqual(verify(parse_expression("2*x+0.0000001"), 2*X, sp.S.Reals).status, "disproved")

    def test_agreement_at_sample_points_is_not_proof(self):
        p = parse_expression("x*(x-1)*(x+1)*(x-2)*(x+2)*(2*x-1)")
        self.assertEqual(verify(p, 0, sp.S.Reals).status, "disproved")

    def test_infinite_and_empty_domains(self):
        self.assertEqual(verify(parse_expression("x"), X, None).status, "unknown")
        self.assertEqual(verify(parse_expression("x"), X, sp.S.EmptySet).status, "unknown")
