import dspy
import openai
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dspy.retrieve.weaviate_rm import WeaviateRM
from qdrant_client import QdrantClient
from dspy.datasets import HotPotQA
from dspy.retrieve.qdrant_rm import QdrantRM

def read_text(file_path: str = '/mnt/d/project/dy/extra/nlp/uie/三体1疯狂年代.txt') -> str:
    content = ""
    with open(file_path, 'r', encoding='gbk') as f:
        content = f.read()
    return content
def split_txt_by_langchain(chuck_size: int = 1024, chuck_overlap: int = 0,
                           file_path: str = '/mnt/d/project/dy/extra/nlp/uie/三体1疯狂年代.txt') -> list[str]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chuck_size,
        chunk_overlap=chuck_overlap,
        length_function=len,
    )

    texts = text_splitter.split_text(read_text(file_path=file_path))
    return texts

class GenerateAnswer(dspy.Signature):
    """Answer questions with short factoid answers."""
    context = dspy.InputField(desc="")
    question = dspy.InputField()
    answer = dspy.OutputField(desc="")


dataset = HotPotQA(train_seed=1, test_size=0, train_size=1000)
dataset = [x.with_inputs('question') for x in dataset.train]

qdrant_client = QdrantClient(":memory:")  # In-memory load
docs = [x.question + " -> " + x.answer for x in dataset]
ids = list(range(0, len(docs)))

qdrant_client.add(
    collection_name="hotpotqa",
    documents=docs,
    ids=ids
)

qdrant_retriever_model = QdrantRM("hotpotqa", qdrant_client, k=3)
qwen32b_ollama = dspy.OllamaLocal(model='qwen:32b',)
qwen32b_ollama('Hello?')

qwen32b_ollama('Hello')
dspy.settings.configure(lm=qwen32b_ollama,rm=qdrant_retriever_model)

texts = split_txt_by_langchain()

generate_answer = dspy.ChainOfThought("context, question -> answer")
generate_answer = dspy.ChainOfThought(GenerateAnswer)



# Call the module on a particular input.
pred = generate_answer(context = texts[0],
                       question = "1, 获取文本中的实体名称和实体属性名称 2,实体类型应包括但不限于'人物'、'地点'、'组织'、'时间'、'事件'等 3,返回结果不应该包含两个重复的内容 4,每一个entity_name和entity_type,根据构建知识图谱的原理,构建出一个完整的数据体系 5,如果某个实体没有在文本中明确定义，你应该根据上下文推断其可能的属性和与其他实体的关联关系，并尽可能提供详细信息。 6,输出的结果要详细,包含实体和其他实体的关系/实体的内容/实体的类型/说=实体说明等等详细的信息")
