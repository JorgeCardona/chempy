# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import pytest

from ..parsing import (
    formula_to_composition, relative_atomic_masses, mass_from_composition,
    to_reaction, atomic_number, formula_to_latex, formula_to_unicode,
    parsing_library

)
from ..testing import requires


def test_atomic_number():
    assert atomic_number('U') == 92
    assert atomic_number('carbon') == 6
    assert atomic_number('ununpentium') == 115
    with pytest.raises(ValueError):
        atomic_number('unobtainium')


@requires(parsing_library)
def test_formula_to_composition():
    assert formula_to_composition('H2O') == {1: 2, 8: 1}
    assert formula_to_composition('Fe/3+') == {0: 3, 26: 1}
    assert formula_to_composition('Fe+3') == {0: 3, 26: 1}
    assert formula_to_composition('Na/+') == {0: 1, 11: 1}
    assert formula_to_composition('Na+1') == {0: 1, 11: 1}
    assert formula_to_composition('Na+') == {0: 1, 11: 1}
    assert formula_to_composition('Cl/-') == {0: -1, 17: 1}
    assert formula_to_composition('Cl-') == {0: -1, 17: 1}
    assert formula_to_composition('NaCl') == {11: 1, 17: 1}
    assert formula_to_composition('NaCl(s)') == {11: 1, 17: 1}
    assert formula_to_composition('Fe(SCN)2/+') == {
        0: 1, 6: 2, 7: 2, 16: 2, 26: 1}
    assert formula_to_composition('Fe(SCN)2+') == {
        0: 1, 6: 2, 7: 2, 16: 2, 26: 1}
    assert formula_to_composition('Fe(SCN)2+1') == {
        0: 1, 6: 2, 7: 2, 16: 2, 26: 1}
    assert formula_to_composition('((H2O)2OH)12') == {1: 60, 8: 36}

    # Special case: solvated electron:
    assert formula_to_composition('e-') == {0: -1}
    assert formula_to_composition('e-1') == {0: -1}
    assert formula_to_composition('e-(aq)') == {0: -1}

    # prefixes and suffixes
    assert formula_to_composition('.NO2(g)') == {7: 1, 8: 2}
    assert formula_to_composition('.NH2') == {1: 2, 7: 1}
    assert formula_to_composition('ONOOH') == {1: 1, 7: 1, 8: 3}
    assert formula_to_composition('.ONOO') == {7: 1, 8: 3}
    assert formula_to_composition('.NO3/2-') == {0: -2, 7: 1, 8: 3}
    assert formula_to_composition('.NO3-2') == {0: -2, 7: 1, 8: 3}

    with pytest.raises(ValueError):
        formula_to_composition('F-F')

    assert formula_to_composition('alpha-FeOOH(s)') == {1: 1, 8: 2, 26: 1}
    assert formula_to_composition('epsilon-Zn(OH)2(s)') == {1: 2, 8: 2, 30: 1}


def test_relative_atomic_masses():
    assert relative_atomic_masses[0] == 1.008


def test_mass_from_composition():
    mass = mass_from_composition({11: 1, 9: 1})
    assert abs(41.988172443 - mass) < 1e-7


@requires(parsing_library)
def test_mass_from_composition__formula():
    mass = mass_from_composition(formula_to_composition('NaF'))
    assert abs(41.988172443 - mass) < 1e-7

    Fminus = mass_from_composition(formula_to_composition('F/-'))
    assert abs(Fminus - 18.998403163 - 5.489e-4) < 1e-7


@requires(parsing_library)
def test_to_reaction():
    from chempy.chemistry import Reaction, Equilibrium
    rxn = to_reaction(
        "H+ + OH- -> H2O; 1.4e11; ref={'doi': '10.1039/FT9908601539'}",
        'H+ OH- H2O'.split(), '->', Reaction)
    assert rxn.__class__ == Reaction

    assert rxn.reac['H+'] == 1
    assert rxn.reac['OH-'] == 1
    assert rxn.prod['H2O'] == 1
    assert rxn.param == 1.4e11
    assert rxn.ref['doi'].startswith('10.')

    eq = to_reaction("H+ + OH- = H2O; 1e-14; ref='rt, [H2O] == 1 M'",
                     'H+ OH- H2O'.split(), '=', Equilibrium)
    assert eq.__class__ == Equilibrium

    assert eq.reac['H+'] == 1
    assert eq.reac['OH-'] == 1
    assert eq.prod['H2O'] == 1
    assert eq.ref.startswith('rt')

    for s in ['2 e-(aq) + (2 H2O) -> H2 + 2 OH- ; 1e6 ; ',
              '2 * e-(aq) + (2 H2O) -> 1 * H2 + 2 * OH- ; 1e6 ; ']:
        rxn2 = to_reaction(s, 'e-(aq) H2 OH- H2O'.split(), '->', Reaction)
        assert rxn2.__class__ == Reaction
        assert rxn2.reac['e-(aq)'] == 2
        assert rxn2.inact_reac['H2O'] == 2
        assert rxn2.prod['H2'] == 1
        assert rxn2.prod['OH-'] == 2
        assert rxn2.param == 1e6


@requires(parsing_library)
def test_formula_to_latex():
    assert formula_to_latex('H2O') == 'H_{2}O'
    assert formula_to_latex('C6H6/+') == 'C_{6}H_{6}^{+}'
    assert formula_to_latex('Fe(CN)6/3-') == 'Fe(CN)_{6}^{3-}'
    assert formula_to_latex('Fe(CN)6-3') == 'Fe(CN)_{6}^{3-}'
    assert formula_to_latex('C18H38/2+') == 'C_{18}H_{38}^{2+}'
    assert formula_to_latex('C18H38/+2') == 'C_{18}H_{38}^{2+}'
    assert formula_to_latex('C18H38+2') == 'C_{18}H_{38}^{2+}'
    assert formula_to_latex('((H2O)2OH)12') == '((H_{2}O)_{2}OH)_{12}'
    assert formula_to_latex('NaCl') == 'NaCl'
    assert formula_to_latex('NaCl(s)') == 'NaCl(s)'
    assert formula_to_latex('e-(aq)') == 'e^{-}(aq)'
    assert formula_to_latex('.NO2(g)') == r'^\bullet NO_{2}(g)'
    assert formula_to_latex('.NH2') == r'^\bullet NH_{2}'
    assert formula_to_latex('ONOOH') == 'ONOOH'
    assert formula_to_latex('.ONOO') == r'^\bullet ONOO'
    assert formula_to_latex('.NO3/2-') == r'^\bullet NO_{3}^{2-}'
    assert formula_to_latex('.NO3-2') == r'^\bullet NO_{3}^{2-}'
    assert formula_to_latex('alpha-FeOOH(s)') == r'\alpha-FeOOH(s)'
    assert formula_to_latex('epsilon-Zn(OH)2(s)') == (
        r'\varepsilon-Zn(OH)_{2}(s)')


@requires(parsing_library)
def test_formula_to_unicoce():
    assert formula_to_unicode('NH4+') == u'NH₄⁺'
    assert formula_to_unicode('H2O') == u'H₂O'
    assert formula_to_unicode('C6H6/+') == u'C₆H₆⁺'
    assert formula_to_unicode('Fe(CN)6/3-') == u'Fe(CN)₆³⁻'
    assert formula_to_unicode('Fe(CN)6-3') == u'Fe(CN)₆³⁻'
    assert formula_to_unicode('C18H38/2+') == u'C₁₈H₃₈²⁺'
    assert formula_to_unicode('C18H38/+2') == u'C₁₈H₃₈²⁺'
    assert formula_to_unicode('C18H38+2') == u'C₁₈H₃₈²⁺'
    assert formula_to_unicode('((H2O)2OH)12') == u'((H₂O)₂OH)₁₂'
    assert formula_to_unicode('NaCl') == u'NaCl'
    assert formula_to_unicode('NaCl(s)') == u'NaCl(s)'
    assert formula_to_unicode('e-(aq)') == u'e⁻(aq)'
    assert formula_to_unicode('.NO2(g)') == u'⋅NO₂(g)'
    assert formula_to_unicode('.NH2') == u'⋅NH₂'
    assert formula_to_unicode('ONOOH') == u'ONOOH'
    assert formula_to_unicode('.ONOO') == u'⋅ONOO'
    assert formula_to_unicode('.NO3/2-') == u'⋅NO₃²⁻'
    assert formula_to_unicode('.NO3-2') == u'⋅NO₃²⁻'
    assert formula_to_unicode('alpha-FeOOH(s)') == u'α-FeOOH(s)'
    assert formula_to_unicode('epsilon-Zn(OH)2(s)') == u'ε-Zn(OH)₂(s)'