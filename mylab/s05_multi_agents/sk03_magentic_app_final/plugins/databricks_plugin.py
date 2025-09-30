# Copyright (c) Microsoft. All rights reserved.

import json
from typing import Optional
from semantic_kernel.functions import kernel_function


class DatabricksPlugin:
    """Databricks 插件 - 處理資料分析和 Genie API 查詢"""
    
    def __init__(self):
        self.genie_api = None
        self.genie_space_id = None
        self.databricks_workspace_client = None
    
    def set_connections(self, genie_api, genie_space_id, databricks_workspace_client):
        """設定 Databricks 連接"""
        self.genie_api = genie_api
        self.genie_space_id = genie_space_id
        self.databricks_workspace_client = databricks_workspace_client
    
    @kernel_function
    def ask_genie(self, question: str, conversation_id: Optional[str] = None) -> str:
        """
        向 Databricks Genie 提問並以 JSON 格式回傳回應。
        回應 JSON 將包含對話 ID 以及訊息內容或結果表格。
        在後續呼叫中重複使用對話 ID 以繼續對話並保持上下文。
        
        Args:
            question: 要向 Genie 提出的問題
            conversation_id: 要繼續的對話 ID。若為 None，將開始新對話
            
        Returns:
            str: JSON 格式的回應，包含對話 ID 和結果
        """
        if not self.genie_api or not self.genie_space_id or not self.databricks_workspace_client:
            return json.dumps({
                "error": "Databricks Genie API not initialized",
                "details": "Please ensure FOUNDRY_DATABRICKS_CONNECTION_NAME is set correctly"
            })
        
        try:
            # 如果 conversation_id 是字串 "null"，將其設為 None
            if conversation_id == "null":
                conversation_id = None
                
            if conversation_id is None:
                message = self.genie_api.start_conversation_and_wait(self.genie_space_id, question)
                conversation_id = message.conversation_id
            else:
                message = self.genie_api.create_message_and_wait(self.genie_space_id, conversation_id, question)

            query_result = None
            if message.query_result:
                query_result = self.genie_api.get_message_query_result(
                    self.genie_space_id, message.conversation_id, message.id
                )

            message_content = self.genie_api.get_message(self.genie_space_id, message.conversation_id, message.id)

            # 嘗試解析結構化資料（如果有的話）
            if query_result and query_result.statement_response:
                statement_id = query_result.statement_response.statement_id
                results = self.databricks_workspace_client.statement_execution.get_statement(statement_id)
                columns = results.manifest.schema.columns
                data = results.result.data_array
                headers = [col.name for col in columns]
                rows = []
                for row in data:
                    formatted_row = []
                    for value, col in zip(row, columns):
                        if value is None:
                            formatted_value = "NULL"
                        elif col.type_name in ["DECIMAL", "DOUBLE", "FLOAT"]:
                            formatted_value = f"{float(value):,.2f}"
                        elif col.type_name in ["INT", "BIGINT", "LONG"]:
                            formatted_value = f"{int(value):,}"
                        else:
                            formatted_value = str(value)
                        formatted_row.append(formatted_value)
                    rows.append(formatted_row)
                return json.dumps({
                    "conversation_id": conversation_id,
                    "table": {
                        "columns": headers,
                        "rows": rows
                    }
                })

            # 回退到純文字訊息
            if message_content.attachments:
                for attachment in message_content.attachments:
                    if attachment.text and attachment.text.content:
                        return json.dumps({
                            "conversation_id": conversation_id,
                            "message": attachment.text.content
                        })

            return json.dumps({
                "conversation_id": conversation_id,
                "message": message_content.content or "No content returned."
            })

        except Exception as e:
            return json.dumps({
                "error": "An error occurred while talking to Genie.",
                "details": str(e)
            })