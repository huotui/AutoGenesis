# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from pydantic import BaseModel, Field
import json


def img_task_prompt(task_info: str = "") -> str:
    """
    Generates a prompt to analyze a screenshot and determine if it satisfies the given task information.

    Args:
        task_info (str): The specific task to evaluate based on the screenshot.

    Returns:
        str: A formatted prompt for the task.
    """
    return f"""
        ### **Task:**
        You are provided with an image that is a screenshot of a web page.
        Your task is to analyze the screenshot and determine if it satisfies the following requirement: {task_info}.

        ### **Instructions:**
        1. Analyze the screenshot for visual indicators that are relevant to the task. Look for elements such as:
        - Presence or absence of specific visual components mentioned in the task.
        - Any text, images, or UI elements that are critical to fulfilling the task.
        - Any error messages, alerts, or missing elements that might indicate the task is not satisfied.
        2. Based on your analysis, decide whether the screenshot satisfies the task requirement.
        3. Make sure your explanation clearly states the observed visual cues that led to your conclusion.

        ### **Note:**
        Focus your analysis on aspects related to the task requirement, regardless of the source of the screenshot.

        """


class ImgTaskResponse(BaseModel):
    """
    Response model for image task evaluation.

    Attributes:
        result (bool): Indicates whether the task is satisfied.
        reason (str): Explanation of the evaluation result.
    """

    result: bool = Field(..., description="Indicates whether the task is satisfied")
    reason: str = Field(..., description="Explanation of the evaluation result")

    @classmethod
    def get_json_schema(cls) -> str:
        return json.dumps(cls.model_json_schema(), indent=2)

    @classmethod
    def get_format_description(cls) -> str:
        schema = cls.model_json_schema()
        properties = schema.get("properties", {})

        format_desc = "{\n"
        for field_name, field_info in properties.items():
            field_type = field_info.get("type", "any")
            description = field_info.get("description", "")
            format_desc += f'  "{field_name}": {field_type}  // {description}\n'
        format_desc += "}"

        return format_desc

    @classmethod
    def get_example_json(cls) -> str:
        example = {"result": True, "reason": "The screenshot shows the expected elements and satisfies the task requirements."}
        return json.dumps(example, indent=2)

    @classmethod
    def get_prompt_format(cls) -> str:
        return f"""
            Response must be in strict JSON format with the following structure:

            {cls.get_format_description()}

            Example:
            {cls.get_example_json()}

            Required fields:
            - result: boolean indicating if task is satisfied
            - reason: string explanation of the evaluation result
            """


def web_task_prompt(task_info: str = "", page_source: str = "") -> str:
    """
    Generates a prompt to analyze a web page and determine if it satisfies the given task information.

    Args:
        task_info (str): The specific task to evaluate.
        page_source (str): The HTML source of the web page.

    Returns:
        str: A formatted prompt for the task.
    """
    page_source_section = ""
    if page_source:
        page_source_section = f"""
        ### **Page Source:**
        ```html
        {page_source}
        ```
        """

    return f"""
        ### **Task:**
        You are provided with information about a web page.
        Your task is to analyze the web page and determine if it satisfies the following requirement: {task_info}.

        ### **Instructions:**
        1. Analyze the web page for indicators that are relevant to the task. Look for elements such as:
        - Presence or absence of specific HTML elements, text content, or attributes.
        - Form fields, buttons, links, or other interactive elements.
        - Error messages, alerts, or validation messages.
        - Page title, URL, or navigation state.
        - CSS classes or data attributes that indicate element state.
        2. Based on your analysis, decide whether the web page satisfies the task requirement.
        3. Make sure your explanation clearly states the observed evidence that led to your conclusion.

        {page_source_section}

        ### **Note:**
        Focus your analysis on aspects related to the task requirement.
        If the page source is not provided, respond based on the available information.
        """


class WebTaskResponse(BaseModel):
    """
    Response model for web page task evaluation.

    Attributes:
        result (bool): Indicates whether the task is satisfied.
        reason (str): Explanation of the evaluation result.
        elements_found (list): List of relevant elements found on the page.
    """

    result: bool = Field(..., description="Indicates whether the task is satisfied")
    reason: str = Field(..., description="Explanation of the evaluation result")
    elements_found: list = Field(
        default_factory=list,
        description="List of relevant elements found on the page that support the evaluation"
    )

    @classmethod
    def get_json_schema(cls) -> str:
        return json.dumps(cls.model_json_schema(), indent=2)

    @classmethod
    def get_format_description(cls) -> str:
        schema = cls.model_json_schema()
        properties = schema.get("properties", {})

        format_desc = "{\n"
        for field_name, field_info in properties.items():
            field_type = field_info.get("type", "any")
            description = field_info.get("description", "")
            format_desc += f'  "{field_name}": {field_type}  // {description}\n'
        format_desc += "}"

        return format_desc

    @classmethod
    def get_example_json(cls) -> str:
        example = {
            "result": True,
            "reason": "The login form is visible with username and password fields.",
            "elements_found": ["input#username", "input#password", "button.login"]
        }
        return json.dumps(example, indent=2)

    @classmethod
    def get_prompt_format(cls) -> str:
        return f"""
            Response must be in strict JSON format with the following structure:

            {cls.get_format_description()}

            Example:
            {cls.get_example_json()}

            Required fields:
            - result: boolean indicating if task is satisfied
            - reason: string explanation of the evaluation result
            - elements_found: list of relevant element selectors found on the page
            """
