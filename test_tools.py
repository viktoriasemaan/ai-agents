import tools

# test aws_well_arch_tool
#query = "How can I design secure VPCs?"
#print(tools.answer_query(query))

# test code_gen_tool
query = "Provide configuration steps with all the services outlined to build simple e-commerce website."
print(tools.iac_gen_tool(query))

# test iac_cost_estimation_tool
# query = "Recommend where I can save costs. "
# print(tools.iac_cost_tool(query))