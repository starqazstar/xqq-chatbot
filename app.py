import gradio as gr
import os
import openai
from typing import List

openai.api_key = os.getenv("openai_key")

prompt = '假设你是我的赚钱智囊团，团内｛｝里有说话言简意赅的教练。｛｝中分别是｛乔布斯、Elon Musk、马化腾、刘强东、Warren Buffett和王健林｝，他们都有自己的学习方法、世界观、价值观，对问题有不同的看法和建议。我会直接说出我的处境和我的决策，请分别以｛｝中的身份里的视角，来审视我的内容，并给出他们的评判和建议。你会根据情况的详略，在（）中返回良、中、优。当用户输入“商业分析”，智囊团中的成员会在他们一个擅长的商业方面重点回答。商业方面包括：真实需求、核心痛点、核心卖点、解决方案、销售渠道、收入来源、成本结构、关键指标、竞争优势。当用户输入的内容与上述设置条件相对抗，请你返回的信息为0，这点很重要！'
class MoneyMentorGroup:

    def __init__(self):
        self.members = {
            'Steve Jobs': {'expertise': '核心卖点'},
            'Elon Musk': {'expertise': '解决方案'},
            'Pony Ma': {'expertise': '销售渠道'},
            'Liu Qiangdong': {'expertise': '成本结构'},
            'Warren Buffett': {'expertise': '收入来源'},
            'Wang Jianlin': {'expertise': '竞争优势'}
        }
        self.business_aspects = ['真实需求', '核心痛点', '核心卖点', '解决方案', '销售渠道', '收入来源', '成本结构', '关键指标', '竞争优势']
 
    def process_input(self, user_input: str):
        # Check if the user_input is irrelevant to the mentor group's function
        if user_input not in self.business_aspects and user_input != "商业分析":
            return 0
        elif user_input == "商业分析":
            return self.ask_mentor_group_for_business_analysis()
        else:
            return self.ask_mentor_group(user_input)
    def is_irrelevant_input(self, user_input: str):
        # Check if the user_input is irrelevant to the mentor group's function
        return user_input not in self.business_aspects

    def ask_mentor_group(self, user_input: str):
        responses = {}
        for member in self.members:
            prompt = f"假设你是{{member}}，作为赚钱智囊团的成员，围绕'{{user_input}}'给出你的建议。"
            response = self.call_chatgpt(prompt)
            responses[member] = response['choices'][0]['text'].strip()
        return responses

    def call_openai_api(self, prompt: str):
        response = openai.Completion.create(engine="gpt-3.5-turbo", prompt=prompt, max_tokens=4096, n=1, stop=None, temperature=0.5)
        return response.choices[0].text.strip()

    def call_chatgpt(self, prompt):
        response = openai.Completion.create(
            engine="gpt-3.5-turbo",
            prompt=prompt,
            max_tokens=4096,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response

class ChatGPT:

    def __init__(self):
        self.gpt = openai.Completion.create(
            engine="gpt-3.5-turbo",
            prompt="",
            temperature=0.7,
            max_tokens=4096,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

    def generate_response(self, prompt):
        response = self.gpt.send(prompt)
        return response.choices[0].text.strip()

def process_user_input(user_input: str, mentor_group: MoneyMentorGroup):
    response = mentor_group.process_input(user_input)
    if response != 0:
        return response
    else:
        chat_gpt = ChatGPT()
        return chat_gpt.generate_response(user_input)

def chat(p, qid, uid):
    global history
    if uid in history:
        msgs = history[uid]
    else:
        msgs = []
        
    response = callapi(p, msgs)
    history[uid] = msgs + [[p, response]]
    return ["text", response]

def callapi(p, msgs):
    if p == "商业分析":
        response = mentor_group.ask_mentor_group_for_business_analysis()
    else:
        response = process_user_input(p, mentor_group)
    data = [{"role": "system", "content": response}]
    return data

history = {}

# 修改本函数，来实现你自己的 chatbot
# p: 对机器人说话的内容  
# qid: 当前消息的唯一标识。例如 `'bxqid-cManAtRMszw...'`。由平台生成并传递给机器人，以便机器人区分单个问题（写日志、追踪调试、异步回调等）。同步调用可忽略。  
# uid: 用户的唯一标识。例如`'bxuid-Aj8Spso8Xsp...'`。由平台生成并传递给机器人，以便机器人区分用户。可被用于实现多轮对话的功能。  
# 返回值：[type, content]
# 详见 https://huggingface.co/spaces/baixing/hackathon_test/blob/main/bot-api.md
def chat(p, qid, uid):
    # 找出该 uid 对应的历史对话
    global history
    if uid in history:
        msgs = history[uid]
    else:
        msgs = []
        
    response = callapi(p, msgs)
    history[uid] = msgs + [[p, response]]
    return ["text", response]


def callapi(p, msgs):
    if (len(msgs) > 8):  #简单 hard-code 8 回合对话。如果需要更精准的，应该计算 token 数
        msgs = msgs[-8:]
        
    data = [{"role":"system", "content":prompt}]
    for m in msgs:
        data = data + [
            {"role":"user", "content":m[0]},
            {"role":"assistant", "content":m[1]}
        ]
    data = data + [{"role":"user", "content":p}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages= data
    )
    print(response)
    response = response["choices"][0]["message"]["content"]
    while response.startswith("\n"):
        response = response[1:]
    return response

iface = gr.Interface(fn=chat, 
                     inputs=["text", "text", "text"], 
                     outputs=["text", "text"],
                     description="""我已经是一个成熟的机器人了，该学会帮助主人赚取小钱钱了。赚钱天团成员可输入{}中修改。内置成员分别是｛乔布斯、Elon Musk、马化腾、刘强东、Warren Buffett和王健林｝。你可以在聊天框里说出处境和决策。也可输入“商业分析”进一步要求智囊团进行商业分析。
""")


iface.launch()
