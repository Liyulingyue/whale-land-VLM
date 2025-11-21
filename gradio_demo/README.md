# 鲸娱秘境-实景AI游戏

李鲁鲁老师指导的鲸娱秘境项目，鲸娱秘境是刘济帆经营的在北京望京的AI线下实体密室逃脱。项目新的部分将嵌入到即将上线到亚运村店中的新剧本。

这个项目致力于研究如何用多模态大模型与线下迷失场景进行结合。

[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-体验链接-FFD21F)](https://huggingface.co/spaces/silk-road/whale-land-VLM) [![ModelScope](https://img.shields.io/badge/ModelScope-体验链接-FFE411?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNTAgMjUwIj48cGF0aCBmaWxsPSIjMDAwIiBkPSJtMTI1IDM0LjkgNDEuNCAxMjUuOUg4My42bDQxLjQtMTI1Ljl6Ii8+PHBhdGggZmlsbD0iI0ZGRiIgZD0iTTEyNSA2Ni44bC0xOC43IDU2LjNoMzcuNEwxMjUgNjYuOHoiLz48L3N2Zz4=)](https://www.modelscope.cn/studios/LuoTuo2023/whale-land-VLM)

# Recent TODO (specific to 文心比赛)

在之前一段时间的开发中，我们已经初步完成了一些项目的VLM demo。然而相较于店内已经实装的chat类型的agent应用（如已经上线的嫌疑人对话系统）来说，这个demo距离实装到店内服务给消费者还存在一定的距离。我们希望通过这次文心开发赛，进一步去实现更接近实用的多模态剧本杀应用，并期望最终能够在北京的亚运村新店(朝阳区北投购物公园b1鲸娱秘境亚运村店)中进行实装。

- 测试准确率和稳定性，实拍场景。我们会以公开benchmark的形式，将剧本杀场景的测试数据发布在huggingface这样的公开平台并且汇报ernie多模态模型的性能。
- 更好的前端应用。相比于之前比赛用的gradio，我们会使用游戏引擎重写前端，使得其达到接近店铺实装应用的水平。
- 嵌入到即将上线到亚运村店中的新剧本。
- 对特定难以直接用单一prompt进行模拟的角色（如装疯卖傻、隐瞒信息、已读乱回等），在ernie系列模型上进行tuning，以获得公开api无法达到的效果。


# 之前的demo

新的前端努力赶工中。。。

<div style="display: flex; align-items: center;">
  <div style="flex: 0 0 300px;">
    <img src="asset/images/鲸娱秘境1.jpg" style="width: 300px;">
  </div>
  <div style="flex: 1; padding-left: 20px;">
    <!-- 在这里添加右侧文本内容 -->
    鲸娱密境AI实景游戏，是由清华-中戏跨学科团队打造的沉浸式娱乐解决方案。项目基于生成式AI技术，通过智能体（AIAgent）重构传统的线下密室与剧本杀产业，已在实际商业场景实现4000+玩家验证。我们试图使用最新的语言模型技术以及创新的运营模式，解决行业痛点：内容生产成本高、人力运营成本高、空间利用率低。鲸娱密境在游戏流程中，使用大量的角色扮演Agent，来代替玩家阅读剧本的方式，向玩家提供信息。
  </div>
</div>

<details>
<summary>demo开发者: 李鲁鲁, 王莹莹, sirly(黄泓森), 刘济帆</summary>
- 李鲁鲁负责了gradio大部分的交互和api连接
- 王莹莹实现了从vlm中抽取物体 并且根据物体生成角色台词
- 刘济帆提供了角色的剧情设计
- Sirly完成了OpenVINO的部署
</details>

# 原型项目的动机


https://github.com/user-attachments/assets/e2b707b6-dcdf-44de-b43d-e6765945ac38


在传统的线下密室中，往往需要玩家通过将特定的物品放到特定的位置来推动剧情。这时如果使用射频装置来进行验证，玩家往往会摸索检查道具中RFID的芯片以及寻找芯片的感应区，这一行为会造成严重的“出戏”。并且，对于错误的道具感应，往往由于主题设计的人力原因，没有过多的反馈。而如果使用人力来进行检验，往往会极大程度地拉高密室的运营成本。在这次比赛的项目中，我们希望借助VLM的泛化能力，能够实现对任意场景中的物品都能够触发对应的反馈。并且，当玩家将任意场景中的物品展示到场景区域的时候，会先由VLM确定物品，然后再触发对应的AIGC的文本。如果物品命中剧情需要的物品列表时，则会进一步推进剧情。借助语言模型的多样化文本的生成能力，可以为场景中的所有道具，都设计匹配的感应语音，以增加游戏的趣味性。


# 运行说明

在运行之前需要参照.env.example的方式部署.env，对于在线端可以这么设置

```bash
LLM_BACKEND = zhipu
MODEL_NAME = glm-4-air
```

对于使用openvino本地模型的，使用"openvino"，并且需要设置模型名称，在提交视频中使用了Qwen2.5-7B-Instruct-fp16-ov。同时你需要在本地建立openai形式的fastapi，使用8000端口。


```bash
LLM_BACKEND = openvino
MODEL_NAME = Qwen2.5-7B-Instruct-fp16-ov
```

同时LLM_BACKEND额外还支持openai和siliconflow

配置好之后直接运行gradio_with_state.py就可以

# 使用VLM和显式COT对广泛物体进行识别

在剧本杀场景中，物品识别的挑战在于需要处理高度多样化的物品类型——包括剧情相关的关键道具、环境装饰物品以及玩家携带的意外物品（如手机、个人配饰等）。为解决这一问题，我们创新性地采用了视觉语言模型（VLM）结合显式思维链（Chain-of-Thought, CoT）的技术方案，其核心设计如下：

1. **覆盖长尾物品**：传统CV模型难以覆盖剧本杀中可能出现的非常规物品（如"会员登记表"、"烟头"、"双节棍"等）
2. **语义灵活性**：同一物品可能有多种名称（如"会员卡" vs "VIP卡"），需要动态匹配候选词
3. **推理可解释性**：通过显式CoT确保模型决策过程透明可追溯

我们的核心prompt设计如下

```
请帮助我抽取图片中的主要物体，如果命中candidates中的物品，则按照candidates输出，否则，输出主要物品的名字
candidates: {candidates}
Let's think step by step and output in json format, 包括以下字段:
- caption 详细描述图像
- major_object 物品名称
- echo 重复字符串: 我将检查candidates中的物品，如果major_object有同义词在candidates中，则修正为candidate对应的名字，不然则保留major_object
- fixed_object_name: 检查candidates后修正（如果命中）的名词，如果不命中则重复输出major_object
```

这一段核心代码部分在src/recognize.py中。

# 使用显式COT对特定物品的台词生成

我们也使用一个显示的CoT，来对特定物品的台词进行生成。

这部分在GameMaster.py的generate_item_response函数中。具体使用了这样一个prompt

```
该游戏阶段的背景设定:{background}
对于道具 {item_i} 的回复是 {response_i}

你的剧情设定如下: {current_prompt}

Let's think it step-by-step and output into JSON format，包括下列关键字
    "item_name" - 要针对输出的物品名称{item_name}
    "analysis" - 结合剧情判断剧情中的人物应该进行怎样的输出
    "echo" - 重复下列字符串: 我认为在剧情设定的人物眼里，看到物品 {item_name}时，会说
    "character_response" - 根据人物性格和剧情设定，输出人物对物品 {item_name} 的反应
```

比如当物品输入手机的时候，LLM的回复为

```json
{
  "item_name": "手机",
  "analysis": "在剧情中，手机作为一个可能的线索，可能会含有凶手的通讯记录或者与受害者最后的联系信息。队长李伟会指示队员们检查手机，以寻找可能的线索，如通话记录、短信、社
交媒体应用等。",
  "echo": "我认为在剧情设定的人物眼里，看到物品 手机时，会说",
  "character_response": "队长李伟可能会说：'这手机可能是死者最后的通讯工具，检查一下有没有未接电话或者最近的通话记录，看看能否找到凶手的线索。'"
}
```


# 鲸娱秘境

**鲸娱秘境·现实游戏**  地址：酒仙桥路新辰里3楼（米瑞酷影城旁）

【鲸娱秘境·现实游戏】成立于2023年5月，团队致力于将游戏与真实场景结合，利用AIGC技术，打造出在现实中完全沉浸的游戏体验。

<img src="asset/images/鲸娱秘境1.jpg" style="height: 300px;">

不同于传统密室或沉浸式体验的封闭空间，鲸娱秘境的每个主题都拥有开放的实景地图。例如在《影院追凶》游戏中，玩家需要进入真实的电影院里寻找线索，走访附近商家。《朝阳浮生记》则把商战搬到整层商场，商场里的每个商户都是NPC，玩家要在真实商场里买地、炒股、斗智斗勇。

<img src="asset/images/鲸娱秘境2.jpg" style="height: 300px;">

此外，我们还利用各类AI技术增强游戏的沉浸感：比如让AI扮演证人与玩家进行对话，通过视觉模型分析玩家的动作并及时给出反馈，推动剧情发展。

<img src="asset/images/鲸娱秘境3.jpg" style="height: 300px;">

这种 “现实游戏” 的设计，让玩家在自由探索中获得更加真实、沉浸的体验。

# 决赛TODO

除了半决赛已有的demo，我们希望使用一个现场摄像头来进行现场demo的展示。

这个时候再使用gradio交互会略为单薄，我们考虑使用摄像头拍摄一个区域，当物品被放置之后按下识别按钮，系统会复用GameMaster来输出剧情。

## 视觉匹配类

为了增强官方物品的匹配准确率，我们希望建立一个视觉匹配系统，通过较高的阈值进行初步的匹配。视觉匹配系统会实现在src/ImageMaster中

ImageMaster类包含以下方法 数据库默认从local_data/official_image 中载入
- set_from_config( config_file_path ) 通过config进行阈值设定载入等等
- init_model( ) 将模型进行初始化
- extract_feature( image ) 返回特征
- load_database( ) 从local_data中载入特征 - 物品名数据库
- record( image, name ) 记录一张新的图片到数据库
- extract_item_from_image( image ) 从图片中提取物品
- extract_item_from_feature( feature ) 从特征中提取物品

ImageMaster保存的特征和物品名用jsonl进行存储，方便批量做删除之类的操作

### 临时视觉匹配类

(这个优先级低)

这是为了增加体验的。对于某次开机的临时数据，也会记录，这样同物品多次出现的时候，有可能可以快速响应

### OpenVino支持

我觉得实际运行系统中，图像特征完全可以考虑OpenVino去抽取

这里要做个backend切换系统，支持AIPC和非AIPC

## 官方物品录制工具

配套ImageMaster使用

## 新前端

因为gradio的前端不支持摄像头，所以要做一个新的前端，
- 展示聊天
- 实时展示拍照画面
- 4个候选聊天
- 按钮

其实gradio也有可能支持，要看一看gradio的摄像头能不能后台控制

## 四句话生成

根据当前的聊天历史，生成3-4句推荐的玩家问询的话。



## Detailed TODO

本项目的开发成员在开源社区招募，下面的TODO记录了每个人的贡献

- [x] DONE by 鲁叔, 参考了王莹莹的原始代码 调通一个openai形式的response
- [x] (DONE by 鲁叔) 在gamemaster引入config配置(一个gamemaster载入一个yaml文件)
- [x] (DONE by 鲁叔) 准备一堆物品照片，确定gamemaster的物品载入格式
- [x] (DONE by 鲁叔) gradio和GM增加图片上传接口
- [x] 鲁叔, 完成剧情内物体 调试物品在chatbot的submit功能
- [x] 剧情外物体在chatbot的submit
- [x] (DONE by 鲁叔)在yaml中定义物品-台词的对应关系
- [x] 鲁叔 fix prompt， 鲁叔 fix解析 DONE by 王莹莹 实现根据prompt 物品 生成台词的函数
- [x](DONE by 鲁叔) 接通chat history - 鲁叔
- [x] (DONE by 王莹莹， 鲁叔fix 输入type) VLM接口识别物体
- [x] 调通语音生成
- [x] (DONE by sirly) ， 调通OpenVINO后端LLM对接
- [x] (DONE by sirly) ， 调通OpenVINO后端VLM对接
- [ ] (DONE by sirly) ， 部署gradio到魔搭和hugging face
- [x] (Done by 鲁叔) 装修界面
- [ ] 每个阶段都可以看到所有物品，感觉有点乱，我们可以限制每个阶段看到的物品不一样
- [ ] 目前每个物品的台词暂时是单一的 不受到阶段的控制, 可以之后升级定义为 支持某个阶段 某个物品的台词（单阶段响应）

