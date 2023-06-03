# import pytest

# @pytest.mark.parametrize("a,b", [(1, 2), (3, 4)])
# def test_test(a, b):
#     assert (a != b)

# @pytest.fixture
# def fixture_test():
#     # fixture is a function that runs before each test
#     return 1

# def test_fixture(fixture_test):
#     assert (fixture_test == 1)

# @pytest.mark.parametrize("a,b", [(3, 2), (3, 4)])
# # can use a fixture and parametrize to run multiple tests with the same fixture
# def test_para_fix(a, b, fixture_test):
#     assert (fixture_test != a)
#     assert (fixture_test != b)
    
# def test_raise(fixture_test):
#     # if test should raise an error, use pytest.raises
#     with pytest.raises(ZeroDivisionError):
#         (fixture_test/0)