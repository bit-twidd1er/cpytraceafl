import builtins
import dis
from itertools import chain
import random
from types import CodeType

from cpytraceafl.rewriter import rewrite


test_source = """
foo = bar + 1

def baz(a, b=(foo*2)):
    a -= b
    try:
        import d
        for c in e(1):
            d.g[1:3] = d.h(c)
            if not e:
                del d[1]
                continue
            yield e(c).f[0]
        else:
            if d[2]:
                raise ValueError
    finally:
        if a < 2:
            a += b
        if b >= 2 or foo:
            raise StopIteration

    def qux(i, **j):
        i.oof += i("oof")[0]
        try:
            i.oof(j["rab"], len(j), lambda l: l or (i % 2))
        except XYZException as e:
            print(e)
        return i

    while a > b:
        a -= [a[0] or b[a] for k in bar(123)]
        yield qux(a and 321)
        if b:
            break

def zab(x, y, z, *w):
    z, _ = x if y(z) else w + "xuq"
    try:
        return (v(z) if v.y else v(y) for v in w if v and v({}))
    except A:
        return x()
    except B:
        return y()
    except C:
        return w[0]()
    finally:
        z[0] = 2
"""


def _extract_lnotabs(code_obj):
    return (
        tuple(_extract_lnotabs(const) for const in code_obj.co_consts if isinstance(const, CodeType)),
        code_obj.co_lnotab,
    )


# a compact way of representing a lnotab bytestring, handling interleaving & conversion
def _l(*a):
    return bytes(chain.from_iterable((b, 1) for b in a))


def test_rewrite():
    orig_code = builtins.compile(test_source, "foo.py", "exec")

    rewritten = rewrite(dis, random.Random, orig_code, True)

    assert _extract_lnotabs(rewritten) == (
        (
            (
                (
                    (
                        (
                            # lambda
                            ((), _l(0, 4, 6,)),
                        ),
                        # qux
                        _l(0, 58, 8, 20, 12, 2,),
                    ),
                    # listcomp
                    ((), _l(0, 4, 12, 6, 4,)),
                ),
                # baz
                _l(0, 28, 28, 8, 14, 4, 10, 4, 4, 8, 8, 8, 4, 4, 12, 8, 34, 2, 4, 6, 4, 2,),
            ),
            (
                (
                    # genexpr
                    ((), _l(0, 2, 8, 8, 6, 8, 6, 2, 4,),),
                ),
                # zab
                _l(0, 8, 4, 6, 30, 8, 12, 8, 12, 8, 16, 6,),
            ),
        ),
        # module
        _l(0),
    )