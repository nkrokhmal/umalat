def test():
    lazy_tester.configure_function_path()
    lazy_tester.log(make_cleaning("separator"))
    lazy_tester.assert_logs()


if __name__ == "__main__":
    test()
