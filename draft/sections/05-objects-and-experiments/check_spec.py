"""Validate the proposed input specification, not meshes or elastic solutions.
Uses only the Python standard library. Run: python check_spec.py
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def signed_area(poly):
    return sum(x1 * y2 - x2 * y1
               for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1])) / 2


def check(data):
    base = data['baseline']
    force = base['traction_Pa'][0] * base['thickness_m']
    assert math.isclose(force, base['total_force_N'][0], rel_tol=1e-12)
    material_areas = {}
    for obj in data['objects']:
        outer = obj['outer_ccw_m']
        assert signed_area(outer) > 0, 'Outer boundary must be counterclockwise'
        area = signed_area(outer)
        xmin, xmax = min(p[0] for p in outer), max(p[0] for p in outer)
        ymin, ymax = min(p[1] for p in outer), max(p[1] for p in outer)
        assert ymin == 0 and ymax == 1
        for hole, seed in zip(obj['holes_cw_m'], obj['hole_seeds_m']):
            assert signed_area(hole) < 0, 'Hole boundary must be clockwise'
            assert all(xmin < x < xmax and ymin < y < ymax for x, y in hole)
            hx, hy = [p[0] for p in hole], [p[1] for p in hole]
            assert min(hx) < seed[0] < max(hx) and min(hy) < seed[1] < max(hy)
            area += signed_area(hole)
        assert len(obj['holes_cw_m']) == len(obj['hole_seeds_m'])
        assert area > 0
        material_areas[obj['id']] = area
        for interval in data['studies']['location']['right_edge_intervals_y_m']:
            assert set(interval) <= set(obj['right_boundary_splits_y_m'])
            length = interval[1] - interval[0]
            assert length > 0
            p = data['studies']['location']['patch_traction_Pa'][0]
            assert math.isclose(p * base['thickness_m'] * length, force, rel_tol=1e-12)
        for a, b in data['studies']['supports']['left_clamp_intervals_y_m']:
            assert a < b and {a, b} <= set(obj['left_boundary_splits_y_m'])
            # ux=tx-rotation*y at two distinct y values forces rotation=tx=0;
            # uy=ty+rotation*x at x=0 then forces ty=0.
            assert b - a > 0
    mesh = data['meshing']
    areas = mesh['max_triangle_area_m2']
    assert all(a > 0 for a in areas)
    assert all(math.isclose(a / b, 4, rel_tol=1e-12) for a, b in zip(areas, areas[1:]))
    assert mesh['default_max_triangle_area_m2'] == areas[1]
    assert all(math.isclose(float(opt.split('a')[1]), a, rel_tol=1e-12)
               for opt, a in zip(mesh['options'], areas))
    return {'status': 'PASS: proposed inputs only',
            'material_areas_m2': material_areas,
            'baseline_total_force_N': force,
            'equal_patch_total_force_N': force,
            'max_triangle_areas_m2': areas,
            'checks': ['boundary orientation', 'rectangular hole containment and seed',
                       'load/support endpoint splits', 'consistent total forces',
                       'two-point support rigid-motion argument', 'area-limit options'],
            'not_checked': ['generated mesh validity or quality', 'assembly',
                            'solver convergence', 'physical small-strain validity']}


if __name__ == '__main__':
    data = json.loads((ROOT / 'cases.json').read_text())
    print(json.dumps(check(data), indent=2))
