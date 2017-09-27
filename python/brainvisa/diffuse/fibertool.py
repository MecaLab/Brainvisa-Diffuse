import os

def define_toolpath():
    script_path = os.path.dirname(os.path.abspath(__file__))
    toolpath = script_path + '/fibertool/'
    return toolpath
