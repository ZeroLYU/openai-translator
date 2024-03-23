import gradio as gr
import sys
import os
from utils import LOG
from model import GLMModel, OpenAIModel
from translator import PDFTranslator
import tempfile
import shutil
import pdfplumber
import markdown

def predict(file_obj, model_type, openai_model=None, openai_api_key=None, glm_model_url=None, timeout=300,
            file_format='markdown', languages="中文"):
    global filedir
    shutil.copy(file_obj.name, filedir)
    # 获取上传Gradio的文件名称
    FileName=os.path.basename(file_obj.name)
    # 获取拷贝在临时目录的新的文件地址
    NewfilePath=os.path.join(filedir,FileName)
    LOG.info(NewfilePath)
    # 打开复制到新路径后的文件
    with open(NewfilePath, 'rb') as file_obj:

        #在本地电脑打开一个新的文件，并且将上传文件内容写入到新文件
        outputPath=os.path.join(filedir,"New"+FileName)
        with open(outputPath,'wb') as w:
            w.write(file_obj.read())

    # 使用pdfplumber打开PDF文件
    with pdfplumber.open(NewfilePath) as pdf:
        # 读取第一页
        first_page = pdf.pages[0]
        # 提取文本内容
        text = first_page.extract_text()

    LOG.info(text)
    LOG.info(model_type)
    model = None
    if model_type == 'GLMModel':
        LOG.info("使用glm接口")
        result = {'model_type': model_type, 'glm_model_url': glm_model_url, 'timeout': timeout, 'file_format':
            file_format}
        glm_url = glm_model_url
        timeout = int(timeout)
        model = GLMModel(model_url=glm_url, timeout=timeout)
    elif model_type == 'OpenAIModel':
        LOG.info("使用openai接口")
        result = {'model_type': model_type, 'openai_model': openai_model, 'openai_api_key': openai_api_key,
                  'file_format': file_format}
        model_name = openai_model
        api_key = openai_api_key
        model = OpenAIModel(model=model_name, api_key=api_key)
    else:
        result = {'error': 'Invalid model type'}
    LOG.info(result)
    pdf_file_path = outputPath

    # 实例化 PDFTranslator 类，并调用 translate_pdf() 方法
    translator = PDFTranslator(model)
    output_file_path = translator.translate_pdf(pdf_file_path, file_format, target_language=languages)
    html_text = ""
    if file_format == "markdown":
        output_file_path = output_file_path.replace('\\', '/')
        LOG.info(output_file_path)
        html_text = read_markdown_file(output_file_path)
    elif file_format == "pdf":
        # 使用pdfplumber打开PDF文件
        with pdfplumber.open(output_file_path) as pdf:
            # 读取第一页
            first_page = pdf.pages[0]
            # 提取文本内容
            html_text = first_page.extract_text()

    return result, output_file_path, html_text

def read_markdown_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        print(f"文件未找到： {file_path}")
    except Exception as e:
        print(f"读取文件时发生错误： {e}")



if __name__ == "__main__":
    global filedir
    filedir= "./files"
    upload_file = gr.components.File(label="上传文件")
    model_type_input = gr.Radio(choices=['GLMModel', 'OpenAIModel'], value='OpenAIModel', label="Model Type")
    openai_model_input = gr.Textbox(label="OpenAI Model", value="gpt-3.5-turbo-16k")
    openai_api_key_input = gr.Textbox(label="OpenAI API Key", value="")
    glm_model_url_input = gr.Textbox(label="GLM Model URL", value="")
    timeout_input = gr.Textbox(label="Timeout", value="300")
    file_format = gr.Radio(choices=['markdown', 'pdf'], value='markdown', label="file_format")
    download_file = gr.components.File(label="下载文件")
    languages = gr.Radio(choices=['中文', '英文', "日文", "拉丁文"], value='中文', label="languages")


    inputs = [upload_file, model_type_input, openai_model_input, openai_api_key_input, glm_model_url_input, timeout_input,
              file_format, languages]
    output = [gr.JSON(label="Result"), download_file, "text"]

    gr.Interface(fn=predict, inputs=inputs, outputs=output, title="AI-PDF翻译神器", description="请上传需要翻译的PDF文件").launch()
