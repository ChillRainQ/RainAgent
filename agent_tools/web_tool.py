import requests
from bs4 import BeautifulSoup
from agent_tools.register import register, BaseTool
from utils import xml_util


@register.register
class WebTool(BaseTool):
    name = "web"
    desc = "网络访问工具"

    def invoke(self, **kwargs) -> str:
        res, err = self.permission_check(kwargs)
        if not res:
            return err
        action = kwargs.pop(xml_util.INVOKE_TAG, None)
        actions = {
            "search": self._search,
            "fetch": self._fetch,
            "weather": self._weather,
            "news": self._news,
            "wiki": self._wiki,
        }
        func = actions.get(action)
        if func is None:
            return f"ERROR: 不支持的操作: {action}"
        try:
            return func(**kwargs)
        except requests.Timeout:
            return f"ERROR: 请求超时"
        except requests.ConnectionError:
            return f"ERROR: 网络连接失败"
        except Exception as e:
            return f"ERROR: {e}"

    def _search(self, query: str) -> str:
        response = requests.get(
            "https://www.bing.com/search",
            params={"q": query, "cc": "us"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for item in soup.select("li.b_algo")[:5]:
            title_tag = item.select_one("h2 a")
            snippet_tag = item.select_one("p")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            url = title_tag.get("href")
            snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
            results.append(f"标题: {title}\nURL: {url}\n摘要: {snippet}")
        return "\n\n".join(results) if results else "未找到相关结果"

    def _fetch(self, url: str) -> str:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        lines = [l.strip() for l in soup.get_text(separator="\n").splitlines() if l.strip()]
        return "\n".join(lines)[:4000]

    def _weather(self, city: str) -> str:
        response = requests.get(
            f"https://wttr.in/{city}",
            params={"format": "3", "lang": "zh"},
            headers={"User-Agent": "curl/7.68.0"},
            timeout=10
        )
        return response.text.strip() or "未获取到天气信息"

    def _news(self, query: str) -> str:
        response = requests.get(
            "https://www.bing.com/news/search",
            params={"q": query},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for item in soup.select("div.news-card")[:5]:
            title = item.select_one("a")
            source = item.select_one("div.source")
            if title:
                source_text = f" - {source.get_text(strip=True)}" if source else ""
                results.append(f"{title.get_text(strip=True)}{source_text}")
        return "\n".join(results) if results else "未找到新闻"

    def _wiki(self, query: str, lang: str = "zh") -> str:
        """支持中英文百科，lang: zh=中文 en=英文"""
        url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{query}"
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            # 中文没找到，尝试英文
            if lang == "zh":
                return self._wiki(query, lang="en")
            return "未找到百科信息"
        if response.status_code != 200:
            return f"ERROR: 百科请求失败，状态码 {response.status_code}"
        data = response.json()
        extract = data.get("extract", "")
        title = data.get("title", "")
        return f"{title}\n\n{extract}" if extract else "未找到百科信息"

    def to_prompt(self) -> str:
        return (
            "- web: 网络访问工具\n"
            "  支持操作:\n"
            "    search(query: str)           搜索网页\n"
            "    fetch(url: str)              获取网页正文\n"
            "    weather(city: str)           查询天气\n"
            "    news(query: str)             查询新闻\n"
            "    wiki(query: str, lang: str)  查询百科（lang默认zh，可选en）\n"
            "\n"
            "示例:\n"
            "<web><invoke>search</invoke><query>AI news</query></web>\n"

        )