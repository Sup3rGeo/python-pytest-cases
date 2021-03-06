from distutils.version import LooseVersion

import pytest
from pytest_cases import param_fixture, param_fixtures, pytest_fixture_plus


# pytest.param - not available in all versions
if LooseVersion(pytest.__version__) >= LooseVersion('3.0.0'):
    pytest_param = pytest.param
else:
    def pytest_param(*args, **kwargs):
        return args


# create a single parameter fixture
my_parameter = param_fixture("my_parameter", [1, 2, 3, 4])


@pytest.fixture
def fixture_uses_param(my_parameter):
    return my_parameter


def test_uses_param(my_parameter, fixture_uses_param):
    # check that the parameter injected in both is the same
    assert my_parameter == fixture_uses_param


# -----
# create a 2-tuple parameter fixture
arg1, arg2 = param_fixtures("arg1, arg2", [(1, 2), (3, 4)])


@pytest.fixture
def fixture_uses_param2(arg2):
    return arg2


def test_uses_param2(arg1, arg2, fixture_uses_param2):
    # check that the parameter injected in both is the same
    assert arg2 == fixture_uses_param2
    assert arg1, arg2 in [(1, 2), (3, 4)]


# -----------

parg1, parg2 = param_fixtures("parg1, parg2", [("a", "b"), ("c", "d")])
"""Two parameter fixtures"""


@pytest_fixture_plus
@pytest.mark.parametrize("arg1, arg2", [
    pytest_param(1, 2, id="f_a"),
    pytest_param(3, 4, id="f_b")
])
def myfix(arg1, arg2, parg1):
    """One parameterized fixture relying on above param fixture"""
    return arg1, arg2, parg1


@pytest.mark.parametrize("arg3, arg4", [
    pytest_param(10, 20, id="t_a"),
    pytest_param(30, 40, id="t_b")
])
def test_one(myfix, arg3, arg4, parg1, parg2, request):
    """"""
    assert myfix[2] == parg1
    paramvalues = request.node.nodeid.split('[')[1][:-1]
    if LooseVersion(pytest.__version__) >= LooseVersion('3.0.0'):
        arg1arg2id = "f_a" if myfix[:-1] == (1, 2) else "f_b"
        arg3arg4id = "t_a" if (arg3, arg4) == (10, 20) else "t_b"
    else:
        arg1arg2id = "-".join(["%s" % v for v in myfix[:-1]])
        arg3arg4id = "-".join(["%s" % v for v in (arg3, arg4)])

    assert paramvalues == "{}-{}-{}-{}".format(arg1arg2id, parg1, parg2, arg3arg4id)
    # print("parg1={} parg2={} myfix={} arg3={} arg4={}".format(parg1, parg2, myfix, arg3, arg4))


def test_synthesis(module_results_dct):
    """Use pytest-harvest to check that the list of executed tests is correct """

    if LooseVersion(pytest.__version__) >= LooseVersion('3.0.0'):
        end_list = ['test_one[f_a-a-b-t_a]',
                    'test_one[f_a-a-b-t_b]',
                    'test_one[f_a-c-d-t_a]',
                    'test_one[f_a-c-d-t_b]',
                    'test_one[f_b-a-b-t_a]',
                    'test_one[f_b-a-b-t_b]',
                    'test_one[f_b-c-d-t_a]',
                    'test_one[f_b-c-d-t_b]']
    else:
        end_list = [ 'test_one[1-2-a-b-10-20]',
                     'test_one[1-2-a-b-30-40]',
                     'test_one[1-2-c-d-10-20]',
                     'test_one[1-2-c-d-30-40]',
                     'test_one[3-4-a-b-10-20]',
                     'test_one[3-4-a-b-30-40]',
                     'test_one[3-4-c-d-10-20]',
                     'test_one[3-4-c-d-30-40]']

    assert list(module_results_dct) == ['test_uses_param[1]',
                                        'test_uses_param[2]',
                                        'test_uses_param[3]',
                                        'test_uses_param[4]',
                                        'test_uses_param2[1-2]',
                                        'test_uses_param2[3-4]',
                                        ] + end_list
