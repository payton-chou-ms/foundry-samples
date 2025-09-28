import json
import requests
from typing import Dict, Any, Callable

from azure.identity import DefaultAzureCredential
from azure.mgmt.logic import LogicManagementClient


class AzureLogicAppTool:
    """
    一個管理多個 Logic Apps 的服務，透過擷取和儲存它們的回呼 URL，
    然後以適當的酬載調用它們。
    """

    def __init__(self, subscription_id: str, resource_group: str, credential=None):
        if credential is None:
            credential = DefaultAzureCredential()
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.logic_client = LogicManagementClient(credential, subscription_id)

        self.callback_urls: Dict[str, str] = {}

    def register_logic_app(self, logic_app_name: str, trigger_name: str) -> None:
        """
        為特定的 Logic App + 觸發器擷取並儲存回呼 URL。
        如果回呼 URL 遺失則拋出 ValueError。
        """
        callback = self.logic_client.workflow_triggers.list_callback_url(
            resource_group_name=self.resource_group,
            workflow_name=logic_app_name,
            trigger_name=trigger_name,
        )

        if callback.value is None:
            raise ValueError(f"Logic App '{logic_app_name}' 未回傳回呼 URL。")

        self.callback_urls[logic_app_name] = callback.value

    def invoke_logic_app(self, logic_app_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        以給定的 JSON 酬載調用已註冊的 Logic App（依名稱）。
        回傳摘要成功/失敗的字典。
        """
        if logic_app_name not in self.callback_urls:
            raise ValueError(f"Logic App '{logic_app_name}' 尚未註冊。")

        url = self.callback_urls[logic_app_name]
        response = requests.post(url=url, json=payload)

        if response.ok:
            return {"result": f"成功調用 {logic_app_name}。"}
        else:
            return {"error": (f"調用 {logic_app_name} 時發生錯誤 " f"({response.status_code}): {response.text}")}


def create_send_email_function(service: AzureLogicAppTool, logic_app_name: str) -> Callable[[str, str, str], str]:
    """
    回傳一個函數，透過在 LogicAppService 中調用指定的 Logic App 來傳送電子郵件。
    這透過在閉包中擷取 LogicAppService 實例來將其保持在全域範圍之外。
    """

    def send_email_via_logic_app(recipient: str, subject: str, body: str) -> str:
        """
        透過以給定的收件人、主旨和內容調用指定的 Logic App 來傳送電子郵件。

        :param recipient: 收件人的電子郵件地址。
        :param subject: 電子郵件的主旨。
        :param body: 電子郵件的內容。
        :return: 摘要操作結果的 JSON 字串。
        """
        payload = {
            "to": recipient,
            "subject": subject,
            "body": body,
        }
        result = service.invoke_logic_app(logic_app_name, payload)
        return json.dumps(result)

    return send_email_via_logic_app