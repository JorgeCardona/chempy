# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

from collections import defaultdict
try:
    import numpy as np
except ImportError:
    np = None

from ..util.testing import requires
from ..units import (
    allclose, get_derived_unit, is_unitless, linspace,
    SI_base_registry, unitless_in_registry, get_physical_quantity,
    to_unitless, magnitude, default_unit_in_registry,
    unit_of, unit_registry_to_human_readable, units_library,
    unit_registry_from_human_readable, default_units as u
)


@requires(units_library)
def test_default_units():
    u.metre
    u.second
    u.hour
    u.decimetre
    u.mole
    u.kilogram
    u.ampere
    u.kelvin
    u.candela
    u.molar
    u.per100eV
    u.joule
    u.gray
    u.eV
    u.MeV
    u.metre
    u.decimetre
    u.centimetre
    u.micrometre
    u.nanometre
    u.gram
    u.molar
    u.hour
    u.perMolar_perSecond
    u.per100eV
    u.umol
    u.umol_per_J


@requires(units_library)
def test_allclose():
    a = np.linspace(2, 3)*u.second
    b = np.linspace(2/3600., 3/3600.)*u.hour
    assert allclose(a, b)
    assert allclose([3600*u.second, 2*u.metre/u.hour],
                    [1*u.hour, 2/3600*u.metre/u.second])


@requires(units_library)
def test_is_unitless():
    assert not is_unitless(1*u.second)
    assert is_unitless(1)


@requires(units_library)
def test_unit_of():
    assert unit_of(0.1*u.metre/u.second) == u.metre/u.second
    assert unit_of(7) == 1


@requires(units_library)
def test_to_unitless():
    dm = u.decimetre
    vals = [1.0*dm, 2.0*dm]
    result = to_unitless(vals, u.metre)
    assert result[0] == 0.1
    assert result[1] == 0.2

    vals = [1.0, 2.0]*dm
    result = to_unitless(vals, u.metre)
    assert result[0] == 0.1
    assert result[1] == 0.2

    length_unit = 1000*u.metre
    result = to_unitless(1.0*u.metre, length_unit)
    assert abs(result - 1e-3) < 1e-12

    amount_unit = 1e-9  # nano
    assert abs(to_unitless(1.0, amount_unit) - 1e9) < 1e-6

    assert abs(to_unitless(3/(u.second*u.molar),
                           u.metre**3/u.mole/u.second) - 3e-3) < 1e-12


@requires(units_library)
def test_linspace():
    ls = linspace(2*u.second, 3*u.second)
    assert abs(to_unitless(ls[0], u.hour) - 2/3600.) < 1e-15


@requires(units_library)
def test_get_derived_unit():
    registry = SI_base_registry.copy()
    registry['length'] = 1e-1*registry['length']
    conc_unit = get_derived_unit(registry, 'concentration')
    dm = u.decimetre
    assert abs(conc_unit - 1*u.mole/(dm**3)) < 1e-12*u.mole/(dm**3)

    registry = defaultdict(lambda: 1)
    registry['amount'] = 1e-9  # nano
    assert abs(to_unitless(1.0, get_derived_unit(
        registry, 'concentration')) - 1e9) < 1e-6


@requires(units_library)
def test_unit_registry_to_human_readable():
    # Not as much human readable as JSON serializable...
    d = defaultdict(lambda: 1)
    assert unit_registry_to_human_readable(d) == dict(
        (x, (1, 1)) for x in SI_base_registry.keys())

    ur = {
        'length': 1e3*u.metre,
        'mass': 1e-2*u.kilogram,
        'time': 1e4*u.second,
        'current': 1e-1*u.ampere,
        'temperature': 1e1*u.kelvin,
        'luminous_intensity': 1e-3*u.candela,
        'amount': 1e4*u.mole
    }
    assert unit_registry_to_human_readable(ur) == {
        'length': (1e3, 'm'),
        'mass': (1e-2, 'kg'),
        'time': (1e4, 's'),
        'current': (1e-1, 'A'),
        'temperature': (1e1, 'K'),
        'luminous_intensity': (1e-3, 'cd'),
        'amount': (1e4, 'mol')
    }
    assert unit_registry_to_human_readable(ur) != {
        'length': (1e2, 'm'),
        'mass': (1e-2, 'kg'),
        'time': (1e4, 's'),
        'current': (1e-1, 'A'),
        'temperature': (1e1, 'K'),
        'luminous_intensity': (1e-3, 'cd'),
        'amount': (1e4, 'mol')
    }


@requires(units_library)
def test_unit_registry_from_human_readable():
    hr = unit_registry_to_human_readable(defaultdict(lambda: 1))
    assert hr == dict((x, (1, 1)) for x in SI_base_registry.keys())
    ur = unit_registry_from_human_readable(hr)
    assert ur == dict((x, 1) for x in SI_base_registry.keys())

    hr = unit_registry_to_human_readable(SI_base_registry)
    assert hr == {
        'length': (1.0, 'm'),
        'mass': (1.0, 'kg'),
        'time': (1.0, 's'),
        'current': (1.0, 'A'),
        'temperature': (1.0, 'K'),
        'luminous_intensity': (1.0, 'cd'),
        'amount': (1.0, 'mol')
    }
    ur = unit_registry_from_human_readable(hr)
    assert ur == SI_base_registry

    ur = unit_registry_from_human_readable({
        'length': (1.0, 'm'),
        'mass': (1.0, 'kg'),
        'time': (1.0, 's'),
        'current': (1.0, 'A'),
        'temperature': (1.0, 'K'),
        'luminous_intensity': (1.0, 'cd'),
        'amount': (1.0, 'mol')
    })
    assert ur == {
        'length': u.metre,
        'mass': u.kilogram,
        'time': u.second,
        'current': u.ampere,
        'temperature': u.kelvin,
        'luminous_intensity': u.candela,
        'amount': u.mole
    }

    ur = unit_registry_from_human_readable({
        'length': (1e3, 'm'),
        'mass': (1e-2, 'kg'),
        'time': (1e4, 's'),
        'current': (1e-1, 'A'),
        'temperature': (1e1, 'K'),
        'luminous_intensity': (1e-3, 'cd'),
        'amount': (1e4, 'mol')
    })
    assert ur == {
        'length': 1e3*u.metre,
        'mass': 1e-2*u.kilogram,
        'time': 1e4*u.second,
        'current': 1e-1*u.ampere,
        'temperature': 1e1*u.kelvin,
        'luminous_intensity': 1e-3*u.candela,
        'amount': 1e4*u.mole
    }

    assert ur != {
        'length': 1e2*u.metre,
        'mass': 1e-3*u.kilogram,
        'time': 1e2*u.second,
        'current': 1e-2*u.ampere,
        'temperature': 1e0*u.kelvin,
        'luminous_intensity': 1e-2*u.candela,
        'amount': 1e3*u.mole
    }


@requires(units_library)
def test_unitless_in_registry():
    mag = magnitude(unitless_in_registry(3*u.per100eV, SI_base_registry))
    ref = 3*1.0364268834527753e-07
    assert abs(mag - ref) < 1e-14


@requires(units_library)
def test_get_physical_quantity():
    assert get_physical_quantity(3*u.mole) == {'amount': 1}
    assert get_physical_quantity(42) == {}


@requires(units_library)
def test_default_unit_in_registry():
    mol_per_m3 = default_unit_in_registry(3*u.molar, SI_base_registry)
    assert magnitude(mol_per_m3) == 1
    assert mol_per_m3 == u.mole/u.metre**3

    assert default_unit_in_registry(3, SI_base_registry) == 1
    assert default_unit_in_registry(3.0, SI_base_registry) == 1