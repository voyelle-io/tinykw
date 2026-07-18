import os
from setuptools import setup
from wheel.bdist_wheel import bdist_wheel

class PlatWheel(bdist_wheel):
    def get_tag(self):
        print(os.environ["WHEEL_PLAT_TAG"])
        return "py3", "none", os.environ["WHEEL_PLAT_TAG"]

setup(cmdclass={"bdist_wheel": PlatWheel})