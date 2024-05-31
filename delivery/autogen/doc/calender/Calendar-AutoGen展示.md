---
tags:
  - Calender
  - AutoGen
Create Time: 2024-05-11T09:26:00
Update Time: "{{date}},{{time}}"
Title:
---


# 一, Agent设计方案

## 一, 1.1  Agent功能设计

以下是各个Agent的功能描述和英文名称：

1. **日程管理Agent (Calendar Event Manager Agent)**
   - **功能**：该Agent作为日历系统的核心组件，负责维护和管理用户的日历事件。它不仅处理日常的日程管理任务，如查看、创建、编辑、删除和完成事件，还提供API接口供其他Agent调用，以查询日历信息或进行事件操作。

	- **详细功能**：
	  - **查看事件**：允许用户查询特定时间范围内的日历事件。
	  - **创建事件**：支持用户通过详细信息创建新的日历事件。
	  - **编辑事件**：允许用户修改已有事件的详细信息。
	  - **删除事件**：提供用户删除特定事件的能力。
	  - **完成事件**：允许用户标记事件为完成状态。
	  - **事件查询接口**：供其他Agent调用以获取特定条件下的事件信息。
	  - **事件操作接口**：供其他Agent调用以执行事件的创建、编辑、删除等操作。


2. **智能建议Agent (Intelligent Recommendation Agent)**

	1. **分析用户的日程历史**：分析用户过往的日程记录，包括频繁的活动类型、时间偏好等。
	2. **识别时间管理习惯**：根据日程历史识别用户的时间管理习惯，如工作和休息的平衡、活动的集中时间段等。
	3. **提供个性化建议**：基于分析结果和已知的时间管理最佳实践，为用户提供个性化的时间管理和日程安排建议。
	4. **优化日程安排**：提出优化现有日程安排的建议，如调整活动时间以减少冲突、建议合理的休息间隔等。
	5. **推荐新活动**：根据用户的偏好和空闲时间，推荐可能感兴趣的新活动或任务。




3. **系统集成协调器agent (Interoperability Broker Agent)**
	**功能介绍**:

	1. **方法暴露与封装（Method Exposure and Encapsulation）**：
	   - IBA封装本系统的功能和服务为标准化的API接口，供其他系统调用。这包括定义接口的输入输出规范、安全协议和访问权限。
	
	2. **外部服务调用（External Service Invocation）**：
	   - 负责主动调用外部系统的API或服务，并处理所有与此相关的任务，如认证授权、参数映射、以及调用结果的处理和转换。
	
	3. **数据转换与映射（Data Transformation and Mapping）**：
	   - 在两个系统间交换数据时，IBA负责数据格式和结构的转换，确保发送方和接收方之间的数据兼容性和准确性。
	
	
	5. **安全与访问控制（Security and Access Control）**：
	   - 实现安全机制以保护数据交换和API访问，包括数据加密、API密钥管理、访问令牌和权限控制。
	
	6. **错误处理与可靠性（Error Handling and Reliability）**：
	   - 提供错误处理机制来应对调用失败、数据不一致等问题，并实施重试策略以提高集成的可靠性。
	
	7. **监控与日志记录（Monitoring and Logging）**：
	   - 记录所有集成活动的详细日志，包括API调用的成功与失败、性能指标和系统事件，以支持系统的监控和故障排除。

4. **会议Agent (Meeting Agent)**
	会议管理Agent是一个专门设计用于优化会议安排和执行流程的智能助手。它通过自动化处理会议相关的各种任务，旨在提升会议的组织效率、参与度和成效。以下是其核心功能：

	1. **会议创建与安排**：
	   - 支持用户通过自然语言指令或界面操作快速创建会议。
	   - 自动分析日历空闲时间，推荐最佳会议时间，减少时间冲突。
	
	2. **邀请发送与响应跟踪**：
	   - 自动发送会议邀请给所有参与者，并跟踪他们的响应状态（接受、拒绝、待定）。
	   - 提供实时更新的参与者状态列表，便于会议组织者了解参与情况。
	
	3. **会议提醒设置**：
	   - 为会议设置自动提醒，确保所有参与者能够按时参加。
	   - 支持多种提醒方式，包括电子邮件、短信或应用内通知。
	
	4. **会议协商**：
	   - 在参与者时间安排出现冲突时，提供会议时间协商功能，帮助找到所有参与者都可接受的会议时间。
	   - 支持自动或手动协商模式，以适应不同的会议安排需求。
	
	5. **会议资料共享**：
	   - 提供一个平台，方便会议组织者和参与者共享会议资料，如议程、演示文稿、参考文件等。
	   - 支持文件上传、下载和在线查看，确保资料的易访问性和安全性。
	
	6. **会议效果跟踪与反馈收集**：
	   - 在会议结束后，自动收集参与者的反馈，用于评估会议效果和改进未来的会议安排。
	   - 提供会议效果的统计和分析报告，帮助组织者了解会议成效并做出调整。
	
5. **日历管理Agent (calendar Admin Agent)**
	日历系统管理员（Calendar Admin Agent）设计为一个核心系统组件，负责接收外部输入并协调内部不同的Agent来完成任务，特别是集成了提醒功能作为系统对外的主要入口
 
	1. **系统协调与管理**
	   - 作为日历系统的中枢，负责协调内部各Agent的工作，包括会议管理Agent、提醒Agent等，以确保系统的高效运行。
	   - 监控系统状态和性能，及时发现并解决潜在的问题。
	
	2. **外部输入处理**
	   - 接收来自用户或外部系统的请求，如会议安排、任务提醒设置等，并进行解析和分发。
	   - 作为系统对外的统一入口，提供API接口，支持外部系统与日历系统的集成。
	
	3. **提醒功能管理**
	   - 提供强大的提醒功能，支持多种提醒类型（会议提醒、任务提醒等）和通知方式（电子邮件、短信、应用内通知等）。
	   - 管理用户的提醒设置，允许用户自定义提醒内容和提醒时间。
	
	4. **Agent组件配置与优化**
	   - 管理和配置系统内部各Agent组件的工作参数，以优化它们的性能和功能。
	   - 根据系统运行数据和用户反馈，调整Agent组件的工作方式，以提升用户体验和系统效率。
	
	5. **安全与权限管理**
	   - 确保系统的安全性，包括数据加密、访问控制和安全审计。
	   - 管理用户权限，确保用户只能访问他们被授权的数据和功能。
	
	6. **数据与资源管理**
	   - 管理系统中的数据，包括用户数据、会议和任务信息等，确保数据的准确性和完整性。
	   - 监控系统资源使用情况，如服务器负载、存储使用等，确保系统稳定运行。
	
	7. **用户支持与反馈**
	   - 提供用户支持服务，解答用户问题，处理用户反馈。
	   - 基于用户反馈，持续改进系统功能和用户体验。


# 二, 案例展示

## 2.1 基础功能展示
- 帮我查询2024年5月15日到2024年5月17日所有的安排,输出变成表格给我(找到字段名称为date的,大于等于2024年5月15日到小于等于2024年5月17日的所有的数据)
- 我会在未来的那天去看望父母(查看event_name中包含看 'Visit Parents'的数据)
- 我在2024年6月1日有什么安排? (查询2024年6月1日的所有的安排)
- 帮我去除掉2024年6月1日所有的安排,我要在家好好休息一天 (删除2024年6月1日所有的数据,添加一条我要在2024年6月1日休息的数据)
- 我从2024年5月15这周开始,下面4周每周的周四下午都需要去上课,请你帮我加入日历

## 2.2 智能功能展示
- 分析我的日历记录，包括频繁的活动类型、时间偏好等。请站在健康的角度上给我提出建议(获取所有的数据,然后根据数据来对我的要求进行分析)
- 统计我在各个事件上面的事件占用比,根据不同的事务和事件对我进行提醒(获取所有的数据,然后根据每个事件占用的事件长度对我进行提醒)
- 如果根据我现在的数据,那么推荐我在什么时候需要进行休假,我的休假时间大概在1周(获取所有的数据,然后根据现在事件,推荐我大概在什么时候进行休假,需要考虑高峰期,时间,地点,消费水平等)
- 在我当前的日程活动中,是否有哪些异常的事件



# 3,发现的问题和解决方案
## 3.1 FuncCall发现的问题

#### 函数设计要求

1. **类型标注**:
   - 函数的输入和输出参数必须明确标注类型，以便 agent 能正确理解和使用。
   - 如果参数类型不确定，使用 `Any` 表示。
   - 如果函数没有输出，使用 `None` 表示。

2. **参数简化**:
   - 参数设计应尽量简化，可以默认由 agent 生成复杂参数。
   - 避免设计复杂参数，若函数内部需要拼接多个参数，应将这些参数融合成一个参数传递。

3. **函数测试**:
   - 在编辑函数时要确保其可运行，进行充分测试。
   - 除非在 prompt 中明确说明，否则 agent 不会自动修正出错的函数。

4. **函数注册**:
   - 使用 `register_for_llm` 函数进行绑定，并在 `assistant` 和 `user_proxy` 中注册。
   - 在 `description` 中详细说明函数功能，描述越清楚越好。

5. **返回值设计**:
   - 函数最好都有返回值，即使不需要，也应返回类似 `Success` 的执行成功消息。
   - 否则 agent 可能误解函数的执行结果，影响后续流程。

6. **异常处理**:
   - 函数必须包含异常处理机制，如 `try-except` 机制。
   - 必要时使用 `assert` 或 `raise` 方法强制中断流程，以便 agent 捕获错误内容并进行修正。

7. **函数区分**:
   - 为避免 agent 混淆功能相近的函数，需要在编写函数时明确区分其功能，防止调用错误。

#### 优点

1. **规范性**:
   - 函数设计规范，参数类型和返回结果标注清晰，有助于提高代码的可读性和维护性。
   - 即使类型未知，也可以通过使用 `Any` 来定义，使函数具有较高的规范性。

2. **错误捕获**:
   - 通过异常处理机制，确保 agent 能够理解和处理函数执行结果，避免流程中断，提高稳定性。

#### 缺点

1. **高编写要求**:
   - 函数必须规整，不建议在一个函数内调用其他函数，保持函数逻辑简单。
   - 对函数编写的要求较高，可能增加开发难度。

2. **异常处理复杂性**:
   - 所有函数必须有异常处理机制，增加了函数编写的复杂性和开发工作量。
   - 需要更多的时间和精力来确保函数的健壮性和稳定性。

3. **调试困难**:
   - 在 AutoGen 的 agent 运行过程中无法进行实时调试(Debug)，只能依赖错误输出进行排查，增加了调试的难度。

4. **复杂流程风险**:
   - 对于特别复杂的流程，使用 AutoGen 可能会引发重大问题。复杂流程应尽量简化或分解，以降低使用风险。
5. **函数依赖的复杂程度**:
   - 如果某个函数在运行过程中出现了问题,但是这个函数又是其他函数的依赖函数,那么我们在处理这个函数的过程中就要非常小心了,因为牵扯到其他函数的入参和结果的使用,调试起来非常麻烦
## 3.2 Prompt问题

1. **Context（背景）**：提供背景信息，帮助 LLM 理解具体情境。
2. **Objective（目标）**：明确任务，指导 LLM 的关注点。
3. **Style（风格）**：指定所需的写作风格，使 LLM 的响应符合预期。
4. **Tone（语气）**：设定语气，确保响应与所需情感一致。
5. **Audience（受众）**：确定目标受众，使 LLM 的响应有针对性。
6. **Response（响应格式）**：提供响应格式（如文本或 JSON），确保 LLM 的输出符合构建流水线的需求。

 **在设计agent的时候如果调用了本地的东西我们需要添加一些什么内容**?
- 当我们在使用问题提问的时候,如果你的agent里面绑定的func的话,并且agent需要访问一些本地的文件,那么请你在prompt中或者在问题中,将你的文件地址,数据库结构(Schema Name, 字段名称),都说清楚. 


## 3.3 Autogen 运行函数过程中相关报错

**运行过程中,出现func_id的问题,没有找到解决方法**:
- 我2024年5月18日下午3点是否有空?如果有空,帮我安排一个会议
- (这个时间段有会议)那么请你通知参会人员取消这个会议
~~~
Provide feedback to chat_manager. Press enter to skip and use auto-reply, or type 'exit' to end the conversation: >? 我2024年5月18日下午3点是否有空?如果有空,帮我安排一个会议
user (to chat_manager):
我2024年5月18日下午3点是否有空?如果有空,帮我安排一个会议
--------------------------------------------------------------------------------
calendar_enenvt_agent (to chat_manager):
***** Suggested tool call (call_iinXdfVyZHu3ToQZnEI7SG1z): sqlite_select *****
Arguments: 
{"sql":"SELECT * FROM user_calendar WHERE date = '2024-05-18' AND ((start_time <= '15:00' AND end_time > '15:00') OR (start_time < '16:00' AND end_time >= '16:00') OR (start_time >= '15:00' AND start_time < '16:00'))","db_file":"/mnt/d/project/zzbc/experiment_project/experiment_project/experiment/output/func_tool.db"}
******************************************************************************
--------------------------------------------------------------------------------
>>>>>>>> EXECUTING FUNCTION sqlite_select...
Execute_Proxy (to chat_manager):
Execute_Proxy (to chat_manager):
***** Response from calling tool (call_iinXdfVyZHu3ToQZnEI7SG1z) *****
[["Discussion on the Impact of Agents in the Future", "15:00", "18:00", "Online Meeting, Tencent Meeting", "Meeting to discuss the impact of agents in the future", "\u6211,\u5434\u535a,\u95e8\u603b", "2024-05-18"]]
**********************************************************************
--------------------------------------------------------------------------------
calendar_enenvt_agent (to chat_manager):
2024年5月18日下午3点您已经有安排了一个会议，具体如下：
- **事件名称**: Discussion on the Impact of Agents in the Future
- **时间**: 15:00 - 18:00
- **位置**: Online Meeting, Tencent Meeting
- **描述**: Meeting to discuss the impact of agents in the future
- **参与人**: 我, 吴博, 门总
因此，您在这个时间段内没有空闲。如果需要重新安排，请告诉我时间段或做其他调整。
--------------------------------------------------------------------------------
calendar_enenvt_agent (to chat_manager):
2024年5月18日下午3点您已经有安排了一个会议，具体信息如下：
- **事件名称**: 讨论：代理在未来的影响
- **时间**: 15:00 - 18:00
- **位置**: 在线会议, 腾讯会议
- **描述**: 会议讨论代理在未来的影响
- **参与人**: 我, 吴博, 门总
因此，您在2024年5月18日下午3点没有空闲时间。如果需要重新安排其他时间的会议或有其他需求，请告知我。
--------------------------------------------------------------------------------
Provide feedback to chat_manager. Press enter to skip and use auto-reply, or type 'exit' to end the conversation: >? 那么请你通知参会人员取消这个会议
meeting_agent (to chat_manager):
那么请你通知参会人员取消这个会议
--------------------------------------------------------------------------------
Provide feedback to chat_manager. Press enter to skip and use auto-reply, or type 'exit' to end the conversation: >? 
>>>>>>>> NO HUMAN INPUT RECEIVED.
>>>>>>>> USING AUTO REPLY...
Traceback (most recent call last):
  File "/home/cc/.pycharm_helpers/pydev/pydevconsole.py", line 364, in runcode
    coro = func()
           ^^^^^^
  File "<input>", line 233, in <module>
  File "/home/cc/miniconda/envs/agent_py11/lib/python3.11/site-packages/autogen/agentchat/conversable_agent.py", line 1000, in initiate_chat
    self.send(msg2send, recipient, request_reply=True, silent=silent)
  File "/home/cc/miniconda/envs/agent_py11/lib/python3.11/site-packages/autogen/agentchat/conversable_agent.py", line 645, in send
    recipient.receive(message, self, request_reply, silent)
  File "/home/cc/miniconda/envs/agent_py11/lib/python3.11/site-packages/autogen/agentchat/conversable_agent.py", line 808, in receive
    reply = self.generate_reply(messages=self.chat_messages[sender], sender=sender)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/cc/miniconda/envs/agent_py11/lib/python3.11/site-packages/autogen/agentchat/conversable_agent.py", line 1949, in generate_reply
    final, reply = reply_func(self, messages=messages, sender=sender, config=reply_func_tuple["config"])
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/cc/miniconda/envs/agent_py11/lib/python3.11/site-packages/autogen/agentchat/groupchat.py", line 1018, in run_chat
    reply = speaker.generate_reply(sender=self)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/cc/miniconda/envs/agent_py11/lib/python3.11/site-packages/autogen/agentchat/conversable_agent.py", line 1949, in generate_reply
    final, reply = reply_func(self, messages=messages, sender=sender, config=reply_func_tuple["config"])
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/cc/miniconda/envs/agent_py11/lib/python3.11/site-packages/autogen/agentchat/conversable_agent.py", line 1315, in generate_oai_reply
    extracted_response = self._generate_oai_reply_from_client(
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/cc/miniconda/envs/agent_py11/lib/python3.11/site-packages/autogen/agentchat/conversable_agent.py", line 1334, in _generate_oai_reply_from_client
    response = llm_client.create(
               ^^^^^^^^^^^^^^^^^^
  File "/home/cc/miniconda/envs/agent_py11/lib/python3.11/site-packages/autogen/oai/client.py", line 638, in create
    response = client.create(params)
               ^^^^^^^^^^^^^^^^^^^^^
  File "/home/cc/miniconda/envs/agent_py11/lib/python3.11/site-packages/autogen/oai/client.py", line 285, in create
    response = completions.create(**params)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/cc/miniconda/envs/agent_py11/lib/python3.11/site-packages/openai/_utils/_utils.py", line 277, in wrapper
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/home/cc/miniconda/envs/agent_py11/lib/python3.11/site-packages/openai/resources/chat/completions.py", line 590, in create
    return self._post(
           ^^^^^^^^^^^
  File "/home/cc/miniconda/envs/agent_py11/lib/python3.11/site-packages/openai/_base_client.py", line 1240, in post
    return cast(ResponseT, self.request(cast_to, opts, stream=stream, stream_cls=stream_cls))
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/cc/miniconda/envs/agent_py11/lib/python3.11/site-packages/openai/_base_client.py", line 921, in request
    return self._request(
           ^^^^^^^^^^^^^^
  File "/home/cc/miniconda/envs/agent_py11/lib/python3.11/site-packages/openai/_base_client.py", line 1020, in _request
    raise self._make_status_error_from_response(err.response) from None
openai.UnprocessableEntityError: Failed to deserialize the JSON body into the target type: messages[4].role: unknown variant `tool`, expected one of `system`, `user`, `assistant` at line 1 column 22306

~~~


## 3.4 Agent调用数据库函数操作失败
 当你向一个Agent提出需求时，Agent会分析你的需求。如果你的需求涉及对本地文件或数据库的操作，Agent会自动拼接所需的函数参数。如果参数不正确，例如在操作数据库时，操作将会失败，导致数据库数据未能正常处理。

解决方案：
- 在你的提示中增加对本地数据、文件或数据库的详细说明。
- 使用更强大的模型来更好地理解你的需求。

## 3.5 Agent与人类交互

无论使用哪个框架，在人类与Agent交互的过程中，要么是完全由Agent自主进行交互，要么是Agent与人类进行交互。目前，我们还无法在Agent说到一半时，进行中途交互。