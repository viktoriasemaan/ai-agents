import tools

# test estimate_chost
file_path = "./cost-result/cost-reulst.txt"

try:
    with open(file_path, "r") as file:
        query = file.read()
except FileNotFoundError:
    print(f"File not found: {file_path}")
except IOError:
    print(f"An error occurred while reading the file: {file_path}")

print(tools.estimate_chost(query))
