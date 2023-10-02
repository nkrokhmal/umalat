from utils_ak.lazy_tester.lazy_tester_class import lazy_tester


def test():
    lazy_tester.configure_function_path()
    lazy_tester.log(make_cleaning("separator"))
    lazy_tester.assert_logs()


if __name__ == "__main__":
    test()
