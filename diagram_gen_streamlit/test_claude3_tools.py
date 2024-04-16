import claude3_tools

# test aws_well_arch_tool
query = "How can I design secure VPCs?"
print(claude3_tools.aws_well_arch_tool(query))
print("aws well arch tool done")


# test diagram tool
query = "A diagram that shows an s3 bucket connected to an ec2 instance"
diag = claude3_tools.diagram_tool(query)

base64_string = claude3_tools.pil_to_base64(diag)
print(base64_string)
caption = claude3_tools.gen_image_caption(base64_string)
print(caption)
print("diagram tool done")


query = "Python code to upload a file to S3"
print(claude3_tools.code_gen_tool(query))
print("code gen tool done")