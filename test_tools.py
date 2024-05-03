import tools

# test answer_query
# query = "How to configure e-commerce website?"
# print(tools.answer_query(query))

# test code_gen_tool
#query = "Provide configuration steps with all the services outlined to build simple e-commerce website."
#print(tools.iac_gen_tool(query))

# test iac_cost_estimation_tool
query = "Estimate costs."
print(tools.iac_estimate_tool(query))