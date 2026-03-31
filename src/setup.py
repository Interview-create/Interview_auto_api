from cx_Freeze import setup, Executable

setup(
    name="myprogram",
    version="0.1",
    description="",
    executables=[Executable("main.py")]
)
