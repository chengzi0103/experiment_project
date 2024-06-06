import dspy
from dspy.teleprompt import BootstrapFewShot


class EntitiesSignature(dspy.Signature):
    """
    实体识别任务的签名类
    """
    question = dspy.InputField()
    entities = dspy.OutputField(desc="获取实体和实体的类型")
    condition = dspy.OutputField(
        desc="识别并列出所有重要的实体。实体可以是 发生的事件、人名、地名、组织名、日期、等。对于每个实体，请指定其类型，确保没有重复的内容。")
    answer = dspy.OutputField(desc="返回的示例: [{'entity_name':'','entity_type':''}]")


class EntitieCoTModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought(EntitiesSignature)

    def forward(self, question):
        return self.prog(question=question)


class TextToKgSignature(dspy.Signature):
    question = dspy.InputField()
    answer = dspy.OutputField(
        desc="请你根据我传递过来的每一个entity_name和entity_type,根据构建知识图谱的原理,构建出一个完整的数据体系. 如果某个实体没有在文本中明确定义，你应该根据上下文推断其可能的属性和与其他实体的关联关系，并尽可能提供详细信息。", )
    return_type = dspy.OutputField(desc="""返回的结果必须保持完整的json结构,如果不能进行知识图谱辨识,那么返回None [
        {
            "entity_name": "",
            "entity_type": "",
            "description": "",
            "relationships": [
                {"related_entity": "", "relation_type": ""},
                {"related_entity": "", "relation_type": ""}
            ]
        }""")
    return_json = dspy.OutputField(desc='')



class TextToKGModule(dspy.Module):
    def __init__(self, entitie_optimized_cot: BootstrapFewShot):
        super().__init__()
        self.kg = dspy.ChainOfThoughtWithHint(TextToKgSignature)
        self.entitie_optimized_cot = entitie_optimized_cot
        self.entities = None

    def forward(self, context: str):
        entities = self.entitie_optimized_cot(question=context)
        self.entities = entities
        answer = self.kg(question=context, hint=str(entities))
        return answer