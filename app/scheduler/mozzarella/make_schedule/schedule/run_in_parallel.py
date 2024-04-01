from joblib import Parallel, delayed


def run_in_parallel(func: callable, kwargs_list: list, parallelism: int = 1) -> list:
    if parallelism == 1:
        return [func(**kwargs) for kwargs in kwargs_list]
    else:
        return Parallel(n_jobs=parallelism)(delayed(func)(**kwargs) for kwargs in kwargs_list)


def test():
    # - Test run_in_parallel

    def f(x):
        return x

    res = run_in_parallel(f, kwargs_list=[{"x": 1}, {"x": 2}], parallelism=2)
    assert res == [1, 2]
    print("run_in_parallel passed")


if __name__ == "__main__":
    test()
