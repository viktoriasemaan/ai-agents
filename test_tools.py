import tools

# test aws_well_arch_tool
query = "How can I design secure VPCs?"
print(tools.aws_well_arch_tool(query))

# test code_gen_tool
query = "Write a function that uploads a file to an S3 bucket using python."
print(tools.code_gen_tool(query))