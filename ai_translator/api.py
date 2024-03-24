from fastapi import FastAPI, Request
import uvicorn, json, datetime
from utils import LOG
from model import GLMModel, OpenAIModel
from utils import ArgumentParser, ConfigLoader, LOG

app = FastAPI()

# 初始化翻译模型
def init_model(model_type):
    argument_parser = ArgumentParser()
    args = argument_parser.parse_args()
    config_loader = ConfigLoader(args.config)
    config = config_loader.load_config()
    LOG.info(config)
    model = None
    # 检查赋值参数
    if config and model_type:
        model_name = config['OpenAIModel']['model']
        api_key = config['OpenAIModel']['api_key']
        glm_url = config['GLMModel']['model_url']
        timeout = config['GLMModel']['timeout']
        LOG.info(f'model_name:{model_name}, api_key:{api_key}, glm_url:{glm_url}, timeout:{timeout}')
        if model_type == 'OpenAIModel':
            print("使用openai接口")
            model_name = config['OpenAIModel']['model']
            api_key = config['OpenAIModel']['api_key']
            model = OpenAIModel(model=model_name, api_key=api_key)
        elif model_type == 'GLMModel':
            print("使用glm接口")
            glm_url = config['GLMModel']['model_url']
            timeout = config['GLMModel']['timeout']
            model = GLMModel(model_url=glm_url, timeout=timeout)
    else:
        LOG.error("config参数缺失")
        return None
    return model




@app.post("/")
async def translator_service(item: dict):


    languages = item.get('languages')
    text = item.get('text')
    model_type = item.get('model_type')

    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    model = init_model(model_type)
    LOG.info(f"{languages},{text},{model_type}")

    prompt = model.make_text_prompt(text, languages)
    response = model.make_request(prompt)

    answer = {
        "response": response[0],
        "status": 200,
        "time": time
    }
    log = "[" + time + "] " + '", prompt:"' + prompt + '", response:"' + repr(response) + '"'
    LOG.info(log)
    return answer

if __name__ == '__main__':

    uvicorn.run(app, host='0.0.0.0', port=8000, workers=1)
