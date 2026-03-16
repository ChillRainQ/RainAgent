from agent_tools.register import register
from components.environment import SystemEnvironment
from components.permissions import Permissions, permissions
from components.work_space import WorkSpace
from core.config import LLMConfig
from core.llm import LLM
from system import constant
from system.config import AgentConfig
from utils import file_util, xml_util, template_util
import xml.etree.ElementTree as ET
import atexit
llm_config = LLMConfig()
agent_config = AgentConfig()
work_space = WorkSpace(agent_config)


class RainAgent:
    def __init__(self, llm_config: LLMConfig, agent_config: AgentConfig):
        self.llm_config = llm_config
        self.agent_config = agent_config
        self.tools_prompt = None
        self.system_prompt = None
        self.environment_prompt = None
        self.environment = None
        self.work_space = None
        self.llm = LLM(llm_config)

    def init(self):
        self.system_prompt = file_util.read_file(constant.SYSTEM_PROMPT_TEXT_PATH)
        self.tools_prompt = register.init()
        self.environment = SystemEnvironment(self.agent_config)
        self.environment_prompt = self.environment.to_prompt
        # self.work_space = WorkSpace(agent_config)
        work_space.init()
        permissions.init(config=agent_config)
        self.tick()

    def tick(self):
        self.work_space_prompt_dir = work_space.dir_to_prompt
        if self.tools_prompt:
            self.system_prompt = self.system_prompt.replace("{tools}", self.tools_prompt)
        if self.environment_prompt:
            self.system_prompt = self.system_prompt.replace("{system}", self.environment_prompt)
        if self.work_space_prompt_dir:
            self.system_prompt = self.system_prompt.replace("{work_dir}", self.work_space_prompt_dir)


    def setup(self):
        self.llm.setup(self.system_prompt)
        print(f"[DEBUG] system_prompt长度: {len(self.system_prompt)}")
        atexit.register(self.shutdown)

    def shutdown(self):
        self.tick()
        file_util.write_file(constant.SYSTEM_PROMPT_TEXT_LAST_FILE_PATH, self.system_prompt, type=0)
        self.system_prompt = self.system_prompt.replace(self.tools_prompt, "{tools}")
        self.system_prompt = self.system_prompt.replace(self.environment_prompt, "{system}")
        self.system_prompt = self.system_prompt.replace(self.work_space_prompt_dir, "{work_dir}")
        file_util.write_file(constant.SYSTEM_PROMPT_TEXT_PATH, self.system_prompt, type=0)



    def parse_action(self, action_raw: str) -> tuple[str, dict] | tuple[None, None]:
        try:
            # 处理CDATA
            import re
            action_raw = re.sub(r'<!\[CDATA\[(.*?)\]\]>',
                                lambda m: m.group(1).replace('<', '&lt;').replace('>', '&gt;'),
                                action_raw, flags=re.DOTALL)
            root = ET.fromstring(action_raw.strip())
            tool_name = root.tag
            kwargs = {child.tag: child.text for child in root}
            return tool_name, kwargs
        except ET.ParseError as e:
            print(f"[DEBUG] ET.ParseError: {e}")
            print(f"[DEBUG] action_raw: {action_raw}")
            return None, None

    def run(self, test: bool = False):
        while True:
            question = input(">>>")
            flag = True
            action = False
            result = None
            images = None

            if test:
                print(f"{self.llm.chat(messages=question, images=None, think=False)}")

            while flag and not test:
                kwargs = None
                tool_name = None

                if result is not None:
                    content = self.llm.chat(messages=result, images=images, think=False)
                else:
                    content = self.llm.chat(messages=question, images=None, think=False)

                # 重置images
                images = None

                # reply检测
                if xml_util.has_tag(content, xml_util.REPLY_TAG):
                    print(f"🤖 {xml_util.parse_xml(content, xml_util.REPLY_TAG)}")
                    flag = False
                    continue

                # thought 检测
                if xml_util.has_tag(content, xml_util.THOUGHT_TAG):
                    print(f"\n\n💭 Thought: \n{xml_util.parse_xml(content, xml_util.THOUGHT_TAG)}")

                # action 检测
                if xml_util.has_tag(content, xml_util.ACTION_TAG):
                    print(f"\n\n💭 Action: \n{xml_util.parse_xml(content, xml_util.ACTION_TAG)}")
                    tool_xml = xml_util.parse_xml(content, xml_util.ACTION_TAG)
                    tool_name, kwargs = self.parse_action(tool_xml)
                    action = True

                # final_answer 检测
                if xml_util.has_tag(content, xml_util.FINAL_ANSWER_TAG):
                    print(f"✅ {xml_util.parse_xml(content, xml_util.FINAL_ANSWER_TAG)}")
                    flag = False

                if action:
                    try:
                        tool = register.get_tool(tool_name)
                        observation = tool.invoke(**kwargs)

                        # 图片类型特殊处理
                        if tool_name == "file" and kwargs.get("action") == "read_image":
                            images = [observation]
                            result = template_util.create_observation_template("图片已读取，请分析图片内容")
                            print(f"\n\n💭 Observation: \n图片已读取")
                        else:
                            result = template_util.create_observation_template(observation)
                            print(f"\n\n💭 Observation: \n{xml_util.parse_xml(result, xml_util.OBSERVATION_TAG)}")

                    except Exception as e:
                        result = template_util.create_observation_template(f"ERROR: {e}")
                        print(f"\n\n💭 Observation: \n{xml_util.parse_xml(result, xml_util.OBSERVATION_TAG)}")

                    action = False

                # 更新tick
                self.tick()



if __name__ == "__main__":

    agent = RainAgent(llm_config, agent_config)
    agent.init()
    agent.setup()
    agent.run(test=False)
