import yaml

from setting import DIR_NAME

"""
    yamlÎÄ¼þ¶ÁÈ¡
"""
def read_yaml(file_path):
    with open(DIR_NAME + file_path, "r", encoding="utf-8") as f:
        return yaml.load(f, Loader=yaml.FullLoader)


if __name__ == "__main__":
    print(read_yaml("/data/base.yaml"))
    print(read_yaml("/data/base.yaml")["test_pytest"]["goto"])
