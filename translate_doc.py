from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
import gradio as gr
import os

from langchain_community.document_loaders import (
    WebBaseLoader,
    TextLoader,
    PyPDFLoader,
    CSVLoader,
    Docx2txtLoader,
    UnstructuredEPubLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredMarkdownLoader,
    UnstructuredXMLLoader,
    UnstructuredRSTLoader,
    UnstructuredExcelLoader,
)

def get_loader(filename: str, file_content_type: str, file_path: str):
    file_ext = filename.split(".")[-1].lower()
    known_type = True

    known_source_ext = [
        "go",
        "py",
        "java",
        "sh",
        "bat",
        "ps1",
        "cmd",
        "js",
        "ts",
        "css",
        "cpp",
        "hpp",
        "h",
        "c",
        "cs",
        "sql",
        "log",
        "ini",
        "pl",
        "pm",
        "r",
        "dart",
        "dockerfile",
        "env",
        "php",
        "hs",
        "hsc",
        "lua",
        "nginxconf",
        "conf",
        "m",
        "mm",
        "plsql",
        "perl",
        "rb",
        "rs",
        "db2",
        "scala",
        "bash",
        "swift",
        "vue",
        "svelte",
    ]

    if file_ext == "pdf":
        loader = PyPDFLoader(file_path, extract_images=False)
    elif file_ext == "csv":
        loader = CSVLoader(file_path)
    elif file_ext == "rst":
        loader = UnstructuredRSTLoader(file_path, mode="elements")
    elif file_ext == "xml":
        loader = UnstructuredXMLLoader(file_path)
    elif file_ext == "md":
        loader = UnstructuredMarkdownLoader(file_path)
    elif file_content_type == "application/epub+zip":
        loader = UnstructuredEPubLoader(file_path)
    elif (
        file_content_type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        or file_ext in ["doc", "docx"]
    ):
        loader = Docx2txtLoader(file_path)
    elif file_content_type in [
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ] or file_ext in ["xls", "xlsx"]:
        loader = UnstructuredExcelLoader(file_path)
    elif file_ext in known_source_ext or (
        file_content_type and file_content_type.find("text/") >= 0
    ):
        loader = TextLoader(file_path)
    else:
        loader = TextLoader(file_path)
        known_type = False

    return loader, known_type

def translateDoc(file):
    file_name_with_extension = os.path.basename(file.name)
    file_name_without_extension = os.path.splitext(file_name_with_extension)[0]
    content_type = os.path.splitext(file_name_with_extension)[1]

    loader, known_type = get_loader(os.path.basename(file.name), "", file.name)
    data = loader.load()
    print(data[0].page_content)

    text_splitter = RecursiveCharacterTextSplitter(
        # Set a really small chunk size, just to show.
        chunk_size=100,
        chunk_overlap=0,
        length_function=len,
        is_separator_regex=False,
    )
    texts = text_splitter.split_text(data[0].page_content)
   
    with open('result.txt', 'w') as file:
        file.write("")

    pageNum = 1;
    for sentence in texts:
        result = translateText(sentence)
        with open('result.txt', 'a') as file:
            file.write(result)
            file.write("\r\n")
        pageNum += 1
        if (pageNum == 10):
            break;
    return open('result.txt', 'r').name

def translateText(content):
    output_parser = StrOutputParser()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个专业的翻译人员,你的任务是将我提供的文字翻译为英文,请直接输出翻译后的内容，不要输出任何多余的文本"),
        ("user", "你要翻译的内容是:```{input}```")
    ])
    llm = ChatOpenAI(
        openai_api_base="https://api.chatanywhere.tech/v1", # 注意，末尾要加 /v1
        openai_api_key="sk-YQRCTjFzTU6rCVM85QrEJlewchE2fE30VWcB1NWmMIYt94Qb",
    )
    # llm = Ollama(model="llama2-chinese")
    # llm = Ollama(model="qwen:7b",base_url="http://121.15.182.141:11434")

    chain = prompt | llm | output_parser
    return chain.invoke({"input": content})

    # llm = Ollama(model="llama2-chinese")
    # chain = prompt | llm | output_parser

demo = gr.Interface(
    fn=translateDoc,
    inputs=["file"],
    outputs=["file"],
)
if __name__ == "__main__":
    demo.launch()

