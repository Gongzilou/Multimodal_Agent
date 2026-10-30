# Multimodal_Agent
```
2026/10/23
开始多模态Agent开发

由视觉模型作为眼睛，将图片等内容转为文本，
然后交给主控模型进行分析（增加备用模型），
代码生成/执行的技能交给code模型，
数学推理/深度逻辑的技能交给math模型
```

# 环境配置 pip install ...
```
Python=3.10.12
langchain==1.4.7
python-dotenv==1.2.4
langchain-ollama==1.1.0
PyJWT==2.15.1
cryptography==50.0.2
psycopg[binary]==3.3.6
langgraph-checkpoint-postgres==3.2.0



fastapi==0.162.0
uvicorn[standard]
```

# 待开发事项
```
"""  
待完成：
继续短期记忆逻辑修改
目前只完成针对映射表的操作，还有外层逻辑checkpointer.delete等
"""

"""  
待完成：
在主程序入口进行多轮对话，开始对话前判断user_id
"""

"""  
待完成：
通过开关判断是否开启长短期记忆
"""
```