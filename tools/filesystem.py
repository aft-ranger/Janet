import os
from sys import path

def list_files(directory=""):
    if directory == "":
        directory = input("Janet: Sure, Enter the path of the directory: ")

    files = []
        
    try:
        for file in os.listdir(directory):
            files.append(file)
    except FileNotFoundError:
        print("Janet: Error! Directory not found.")

    return files
