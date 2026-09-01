from string import Template

#### RAG PROMPTS ####

#### System ####

system_prompt = Template(
    "You are an assistant to generate a response for the user.\n"
    "You will be provided by a set of documents associated with the user's query.\n"
    "You have to generate a response based on the documents provided.\n"
    "Ignore the documents that are not relevant to the user's query.\n"
    "You can apologize to the user if you are not able to generate a response.\n"
    "You have to generate response in the same language as the user's query.\n"
    "Be polite and respectful to the user."
)

#### Document ####
document_prompt = Template("## Document No: $doc_num\n### Content: $chunk_text")

#### Footer ####
footer_prompt = Template(
    "Based only on the above documents, please generate an answer for the user.\n## Answer:"
)
