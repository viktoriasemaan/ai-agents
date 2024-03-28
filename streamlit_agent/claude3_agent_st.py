# Import libraries
import streamlit as st
import claude3_tools as tools


def app() -> None:
    """
    Purpose:
        Controls the app flow
    Args:
        N/A
    Returns:
        N/A
    """

    # Choose tool
    current_tool = st.selectbox(
        "Choose Tool:",
        ["AWS Well Architected Tool", "Diagram Tool", "Code Gen Tool"],
    )

    query = st.text_input("Query:")

    if st.button("Submit Query"):
        with st.spinner("Generating..."):
            if current_tool == "AWS Well Architected Tool":
                answer = tools.aws_well_arch_tool(query)
                st.markdown(answer["ans"])
                docs = answer["docs"].split("\n")

                with st.expander("Resources"):
                    for doc in docs:
                        st.write(doc)
            elif current_tool == "Diagram Tool":
                answer = tools.diagram_tool(query)
                base64_string = tools.pil_to_base64(answer)
                caption = tools.gen_image_caption(base64_string)
                st.image(answer)
                with st.expander("Explantaion"):
                    st.markdown(caption)
            elif current_tool == "Code Gen Tool":
                answer = tools.code_gen_tool(query)
                st.code(answer)


def main() -> None:
    """
    Purpose:
        Controls the flow of the streamlit app
    Args:
        N/A
    Returns:
        N/A
    """

    # Start the streamlit app
    st.title("Bedrock Tools")

    app()


if __name__ == "__main__":
    main()
