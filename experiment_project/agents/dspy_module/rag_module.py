import json
import random
import time
from pathlib import Path
from typing import Union, List
import dspy
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document

from experiment_project.agents.dspy_module.base_module import TaskAnalysisModule, QualityEnhancerModule
from experiment_project.agents.dspy_module.base_signature import init_costar_signature
from experiment_project.utils.files.split import split_txt_by_langchain
from langchain_community.document_loaders import PyPDFLoader



class BaseRag(dspy.Module):
    def __init__(self, module_path:str, pg_connection:str=None, collection_name:str='my_docs', is_upload_file:bool=False, files_path:List[str]=None, model_kwargs:dict={'device':0}, chunk_size:int=256, encoding:str= 'utf-8',multi_process:bool=False):
        super().__init__()
        self.embedding = HuggingFaceEmbeddings(model_name=module_path,model_kwargs=model_kwargs,show_progress=True,multi_process=multi_process)
        if pg_connection is None:
            pg_connection = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"  # Uses psycopg3!
        self.vectorstore = PGVector(
            embeddings=self.embedding,
            collection_name=collection_name,
            connection=pg_connection,
            use_jsonb=True,
        )
        if is_upload_file is True and files_path is not None:
            self.upload_file_to_vector(files_path=files_path, chunk_size=chunk_size, encoding=encoding)

    def delete_collection(self):
        self.vectorstore.drop_tables()

    def split_files(self,files_path:List[str],chunk_size:int=256,encoding:str='utf-8'):
        all_data = []
        id_num = 0
        for num,file_path in enumerate(files_path):
            file_path = Path(file_path)
            if file_path.is_file():
                file_extension = file_path.suffix
                if file_extension == '.txt':
                    data = split_txt_by_langchain(chuck_size=chunk_size,file_path=str(file_path),encoding=encoding)
                    if len(data) > 0:
                        for num, text in enumerate(data):
                            id_num += 1
                            doc = Document(page_content=text,
                                           metadata={"id": id_num, 'chunk_index': num, 'chunk_size': len(text),
                                                     'source': file_path})
                            all_data.append(doc)
                elif file_extension == '.pdf':
                    loader = PyPDFLoader(str(file_path))
                    pages = loader.load_and_split()
                    for doc in pages:
                        id_num += 1
                        doc.metadata['id'] = id_num
                        all_data.append(doc)
        return all_data

    def upload_file_to_vector(self, files_path: List[str], chunk_size:int=256, encoding:str= 'utf-8'):
        t1 = time.time()
        docs = self.split_files(files_path=files_path, chunk_size=chunk_size, encoding=encoding)
        # id_num = 0
        # for file_path_num,file_path in enumerate(files_path):
        #     data = split_txt_by_langchain(chuck_size=chunk_size,
        #                                   file_path=file_path,encoding=encoding)
        #     docs = []
        #     for num, text in enumerate(data):
        #         id_num +=1
        #         doc = Document(page_content=text, metadata={"id": id_num, 'chunk_index': num, 'chunk_size': len(text),'file_path':file_path})
        #         docs.append(doc)
        self.vectorstore.add_documents(docs, ids=[doc.metadata["id"] for doc in docs])
        print('当前数据入库完毕 : ',time.time() - t1 )
    def search(self, keywords: Union[List[str],str], k: int = 6):
        data = []
        if isinstance(keywords,str):
            results = self.vectorstore.similarity_search(keywords, k=k)

            for result in results:
                data.append(result.page_content)
            data = {keywords:list(set(data))}
        elif isinstance(keywords,list):
            data = []
            for keyword in keywords:
                results = self.vectorstore.similarity_search(keyword, k=k)
                data.append({keyword:list(set([i.page_content for i in results]))})

        return data

    @property
    def no_cache(self):
        return dict(temperature=0.7 + 0.0001 * random.uniform(-1, 1))


class ReasonerRagOldModule(BaseRag):
    def __init__(self, module_path:str, reasoning_signature: dspy.Signature=None, pg_connection:str=None, collection_name:str='my_docs', is_upload_file:bool=False, files_path:List[str]=None,encoding:str= 'utf-8',chunk_size:int=256,multi_process:bool=False,rag_search_num:int=5):
        super().__init__(module_path=module_path, pg_connection=pg_connection, collection_name=collection_name, is_upload_file=is_upload_file, files_path=files_path,encoding=encoding,chunk_size=chunk_size,multi_process=multi_process)
        if reasoning_signature is None:
            reasoning_signature = init_costar_signature(role='Reasoner',
                                                        specifics="The agent should provide accurate and coherent answers based on the user's questions.",
                                                        results="A clear and accurate response to the user's query.",
                                                        example="user_query: 'What is the capital of France?'\nagent_response: 'The capital of France is Paris.'")
        self.reasoner = dspy.Predict(reasoning_signature)
        self.task_evaluation = TaskAnalysisModule()
        self.quality_enhancer = QualityEnhancerModule()
        self.rag_search_num = rag_search_num

    def forward(self, question:str):
        task_result = json.loads(self.task_evaluation.forward(question=question).answer)
        question = task_result.get('task_description')
        keywords = task_result.get('keywords')
        # llm_result = self.reasoner(question=question,**self.no_cache).answer
        llm_result = ''
        all_rag_result = self.search(keywords=keywords,k=self.rag_search_num)
        result = self.quality_enhancer.forward(question=question,rag_data=json.dumps(all_rag_result),llm_data=llm_result,).answer
        return result


from experiment_project.utils.initial.util import init_sys_env
from experiment_project.utils.files.read import read_yaml
import dspy

init_sys_env()
secret_env_file = '/mnt/d/project/zzbc/env_secret_config.yaml'

api_configs = read_yaml(secret_env_file)

model_config = api_configs.get('openai')
turbo = dspy.OpenAI(model=model_config.get('model'), max_tokens=4096,api_key=model_config.get('api_key'))
dspy.settings.configure(lm=turbo)
# module_path = '/mnt/d/models/embeddings/bce-embedding-base_v1'
# is_upload_file = True
# # files_path = ['/mnt/d/project/experiment_project/data/text_to_kg/三体1疯狂年代.txt','/mnt/c/Users/cc/Desktop/pic/Retrieval-Augmented Generation with Knowledge Graphs for Customer Service Question Answering.pdf']
# files_path = ['/mnt/c/Users/cc/Desktop/pic/Text-Animator Controllable Visual Text Video Generation.pdf']
# encoding = 'gbk'
# rag_search_num = 4
# collection_name = 'pdf'
# refine_module = ReasonerRagModule(module_path=module_path,is_upload_file=is_upload_file,files_path=files_path,encoding=encoding,rag_search_num=rag_search_num)
# result = refine_module.forward(question="Provide a detailed summary of the theme and explanation of the paper 'Text-Animator Controllable Visual Text Video Generation'. Additionally, explain which papers it cites, what achievements it has made, when it was written, and who the authors are.")
# print(result)


question = '总结《三体》的核心情节和主题，包括分析主要人物及其行为动机，探讨主要事件及其影响，关注科学概念及其在故事中的作用。'
all_rag_result = [{'三体': ['三体（中国科幻基石丛书） \n\u3000\u3000刘慈欣著',
   '质子的二维平面对三体行星的包裹是一个漫长的过程，当星空的变形逼近天顶的三体行星映像时，群星从上至下依次消失了，已弯曲到行星另一面的质子平面挡住了星空，这时仍有阳光照进已弯曲成曲面的平面质子内。可以看到三体世界的映像在太空中的宇宙哈哈镜里已变得面目全非。当最后一缕阳光消失后，一切都隐入天边的黑暗中。这是三体世界有史以来最黑的夜。在行星的引力和人工电磁辐射的平衡下，质子平面形成了一个半径为同步轨道的大球壳，将行星完全包在球心。',
   '是的，太空中出现了另一个三体世界。\n\u3000\u3000紧接着，天色亮了起来，在太空中的第二三体行星旁边，扩大的南半球星空的边界又扫描出了一轮太阳。这显然是现在正照耀着南半球的那个太阳，但似乎只有它的一半大小。\n\u3000\u3000现在，终于有人悟出了事情的真相：“那是一面镜子！”\n\u3000\u3000这面在三体世界上方出现的巨镜，就是那粒正在被展开成二维平面的质子，这是一个没有厚度的真正意义上的几何平面。',
   '从《三体》连载中得知，国内科幻读者喜欢描述宇宙终极图景的科幻小说，这多少让人感到有些意外。我是从八十年代的科幻高潮中过来的，个人认为那时的作家们创造了真正的、以后再也没有成规模出现过的中国式科幻，这种科幻最显著的特点就是完全技术细节化，没有形而上的影子。而现在的科幻迷们已经打开了天眼，用思想拥抱整个宇宙了。这也对科幻小说作者提出了更高的要求，很遗憾《三体》不是这样的“终级科幻小说”。创作《2001》式的科幻是很难的，特别是长篇，很容易成为既无小说的生动，又无科普的正确，更无论文的严谨的一堆空架子，笔者',
   '严寒降临了。全反射的质子平面将所有阳光反射回太空，三体世界的气温急骤下降，最后降到了曾导致多轮文明毁灭的三颗飞星同现时的程度。三体世界绝大多数公民脱水贮存，黑暗笼罩的大地上一片死寂。天空中，只有维持质子巨膜的电磁辐射激发的微弱光晕在晃动，偶尔还可以看到同步轨道上的几点灯光，那是在巨膜上进行集成电路蚀刻的飞船。']},
 {'刘慈欣': ['三体（中国科幻基石丛书） \n\u3000\u3000刘慈欣著',
   '说起爱因斯坦，你比我有更多的东西需要交待。1922 年冬天，爱因斯坦到上海访问，你父亲因德语很好被安排为接待陪同者之一。你多次告诉我，父亲是在爱因斯坦的亲自教诲下走上物理学之路的，而你选择物理专业又是受了父亲的影响，所以爱翁也可以看作你的间接导师，你为此感到无比的自豪和幸福。\n\u3000\u3000后来我知道，父亲对你讲了善意的谎言，他与爱因斯坦只有过一次短得不能再短的交流。\n\u3000\u3000那是 1922 年 11 月 13 日上午，他陪爱因斯坦到南京路散步，同行的',
   '好像还有上海大学校长于右任、《大公报》经理曹谷冰等人，经过一个路基维修点，爱因斯坦在一名砸石子的小工身旁停下，默默看着这个在寒风中衣衫破烂、手脸污黑的男孩子，问你父亲：他一天挣多少钱？问过小工后，你父亲回答：五分。这就是他与改变世界的科学大师唯一的一次交流，没有物理学，没有相对论，只有冰冷的现实。据你父亲说，爱因斯坦听到他的回答后又默默地站在那里好一会儿，看着小工麻木的劳作，手里的烟斗都灭了也没有吸一口。你父亲在回忆这件事后，对我发出这样的感叹：在中国，任何超脱飞扬的思想都会砰然坠地的，现实的引力太沉',
   '从《三体》连载中得知，国内科幻读者喜欢描述宇宙终极图景的科幻小说，这多少让人感到有些意外。我是从八十年代的科幻高潮中过来的，个人认为那时的作家们创造了真正的、以后再也没有成规模出现过的中国式科幻，这种科幻最显著的特点就是完全技术细节化，没有形而上的影子。而现在的科幻迷们已经打开了天眼，用思想拥抱整个宇宙了。这也对科幻小说作者提出了更高的要求，很遗憾《三体》不是这样的“终级科幻小说”。创作《2001》式的科幻是很难的，特别是长篇，很容易成为既无小说的生动，又无科普的正确，更无论文的严谨的一堆空架子，笔者',
   '《三体》终于能与科幻朋友们见面了，用连载的方式事先谁都没有想到，也是无奈之举。之前就题材问题与编辑们仔细商讨过，感觉没有什么问题，但没想到今年是文革三十周年这事儿，单行本一时出不了，也只能这样了。\n\u3000\u3000其实这本书不是文革题材的，文革内容在其中只占不到十分之一，但却是一个漂荡在故事中挥之不去的精神幽灵。']},
 {'科幻': ['从《三体》连载中得知，国内科幻读者喜欢描述宇宙终极图景的科幻小说，这多少让人感到有些意外。我是从八十年代的科幻高潮中过来的，个人认为那时的作家们创造了真正的、以后再也没有成规模出现过的中国式科幻，这种科幻最显著的特点就是完全技术细节化，没有形而上的影子。而现在的科幻迷们已经打开了天眼，用思想拥抱整个宇宙了。这也对科幻小说作者提出了更高的要求，很遗憾《三体》不是这样的“终级科幻小说”。创作《2001》式的科幻是很难的，特别是长篇，很容易成为既无小说的生动，又无科普的正确，更无论文的严谨的一堆空架子，笔者',
   '三体（中国科幻基石丛书） \n\u3000\u3000刘慈欣著',
   '哦，这个设想中的系列叫《地球往事》，没有太多的意思，科幻与其他幻想文学的区别就在于它与真实还牵着一根细线，这就使它成为现代神话而不是童话(古代神话在当时的读者心中是真实的)。所以我一直认为，好看的科幻小说应该是把最空灵最疯狂的想象写得像新闻报道一般真实。往事的回忆总是真实的，自己希望把小说写得像是历史学家对过去的真实记叙，但能不能做到，就是另一回事了。\n\u3000\u3000设想中《地球往事》的下一部暂名为《黑暗森林》，取自八十年代流行过的一句话：“城市就是森林，每一个男人都是猎手，每一个女人都是陷阱。”',
   '作者试图讲述一部在光年尺度上重新演绎的中国现代史，讲述一个文明二百次毁灭与重生的传奇。\n\u3000\u3000朋友们将会看到，连载的这第一期，几乎不是科幻，但这本书并不是这一期显示出来的这个样子，它不是现实科幻，比《球状闪电》更空灵，希望您能耐心地看下去，后面的故事变化会很大。\n\u3000\u3000在以后的一段时光中，读者朋友们将走过我在过去的一年中走过的精神历程，坦率地说，我不知道你们将在这条黑暗诡异的迷途上看到什么，我很不安。但科幻写到今天，能够与大家同行这么长一段，也是缘份。',
   '《三体》终于能与科幻朋友们见面了，用连载的方式事先谁都没有想到，也是无奈之举。之前就题材问题与编辑们仔细商讨过，感觉没有什么问题，但没想到今年是文革三十周年这事儿，单行本一时出不了，也只能这样了。\n\u3000\u3000其实这本书不是文革题材的，文革内容在其中只占不到十分之一，但却是一个漂荡在故事中挥之不去的精神幽灵。']}]
llm_result = 'The Three-Body Problem" is a science fiction novel by Liu Cixin that explores the interaction between humanity and an alien civilization from the star system Trisolaris. The story begins during China\'s Cultural Revolution and follows several characters, including astrophysicist Ye Wenjie, who becomes disillusioned with humanity and sends a signal to the Trisolarans, inviting them to Earth. The Trisolarans, whose planet suffers from extreme and unpredictable climate changes due to its three suns, see Earth as a potential new home. The novel delves into themes of scientific discovery, the potential dangers of first contact with an alien civilization, and the moral and ethical dilemmas faced by humanity. Key scientific concepts include the three-body problem in orbital mechanics, which describes the complex gravitational interactions between three celestial bodies, and the use of advanced technology by the Trisolarans to disrupt human scientific progress.'
quality_enhancer = TaskAnalysisModule()
result = quality_enhancer.forward(question="Provide a detailed summary of the theme and explanation of the paper 'Text-Animator Controllable Visual Text Video Generation'. Additionally, explain which papers it cites, what achievements it has made, when it was written, and who the authors are.")
print(result)



