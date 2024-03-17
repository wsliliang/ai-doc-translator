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
    elif file_ext in ["doc", "docx"]:
        loader = Docx2txtLoader(file_path)
    elif file_ext in ["xls", "xlsx"]:
        loader = UnstructuredExcelLoader(file_path)
    elif file_ext in known_source_ext:
        loader = TextLoader(file_path)
    else:
        loader = TextLoader(file_path)
        known_type = False

    return loader, known_type

def translateDoc(file, targetLang, llm):
    print("目标语言:" + targetLang + ",大模型:" + llm)
    file_name_with_extension = os.path.basename(file.name)
    file_name_without_extension = os.path.splitext(file_name_with_extension)[0]
    content_type = os.path.splitext(file_name_with_extension)[1]

    loader, known_type = get_loader(os.path.basename(file.name), "", file.name)
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=0,
        length_function=len,
        is_separator_regex=False,
    )
    
    with open('result.txt', 'w') as file:
        file.write("")

    sentenceNum = 0
    previousSentence = ""
    for document in data:
        # texts = text_splitter.split_text(document.page_content)
        # print("句子数量:")
        # print(len(texts))
        # for sentence in texts:
        #     sentenceNum += 1
        #     if sentence.isspace():
        #         continue
        #     print("正在翻译:" + str(sentenceNum) + "/" + str(len(texts)) + ":" + sentence)
        #     result = translateText(sentence, targetLang, previousSentence, llm)
        #     previousSentence = result
        #     with open('result.txt', 'a') as file:
        #         file.write(result)
        #         file.write("\r\n")
        #     if (sentenceNum == 10):
        #         break;
        if (document.page_content.isspace()):
            continue
        result = translateText(document.page_content, targetLang, previousSentence, llm)
        translated = text_splitter.split_text(result)
        previousSentence = translated[len(translated)-1]
        with open('result.txt', 'a') as file:
            file.write(result)
            file.write("\r\n")
        #if (sentenceNum == 10):
        #    break;
    
    return open('result.txt', 'r').name

def translateText(content, targetLang, context, llm):
    output_parser = StrOutputParser()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个专业的翻译人员,我想把一个文档翻译为{targetLang}，每次我会提供给你一段要翻译的内容，注意：你只需要直接输出翻译后的内容，不要输出任何的提示。"),
        ("user", "{input}")
    ])
    if (llm == '本地ollama'):
        llm = Ollama(model="qwen:7b",base_url="http://localhost:11434")
    
    if (llm == 'openAI'):
        llm = ChatOpenAI(
            openai_api_base="https://api.chatanywhere.tech/v1", # 注意，末尾要加 /v1
            openai_api_key="sk-你的api key",
        )
    chain = prompt | llm | output_parser
    return chain.invoke({"input": content,"targetLang":targetLang,"context":context})

demo = gr.Interface(
    fn=translateDoc,
    inputs=[
        "file",
        gr.Dropdown(choices=['English','中文'], value = 'English',label = '目标语言'),
        gr.Dropdown(choices=['本地ollama','openAI'], value = 'openAI',label = '大模型')
    ],
    outputs=["file"],
)
if __name__ == "__main__":
    demo.launch()

