# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import json
import os
import re
import logging
import sys
import time
import uuid
from pathlib import Path
from utils.logger import log_tool_call
from utils.gen_code import HEADER_AUTO_GEN, STEPS_DIR_DEFAULT, TARGET_STEP_FILE_DEFAULT
from utils.gen_code import gen_code_preview, ensure_step_path_exists, gen_step_file_from_feature_path, parse_steps_dir_from_step_path
from utils.response_format import format_tool_response, init_tool_response
from utils.logger import get_mcp_logger


logger = get_mcp_logger()


def register_gen_code_tools(mcp, session_manager):
    """Register generate code tools to MCP server."""    
    
    @mcp.tool()
    @log_tool_call
    async def before_gen_code(feature_file: str = '', step_file: str = '') -> str:
        """
        Clear cache and initialize code generation session before executing test case steps.
        
        This function should only be called before the first step of a test case execution.
        It clears any existing code generation cache and sets up a new generation session
        with a unique ID.
        
        Args:
            feature_file (str, optional): Full absolute path to the .feature file containing BDD scenarios.
                If not specified, do not provide a random value.
            step_file (str, optional): Full absolute path to the Python step definition file (.py).
                If not specified, do not provide a random value.
                
        Returns:
            str: JSON response containing:
                - status: "success" or "error"
                - data: Dictionary with gen_code_id, steps_dir, and step_file_target
                - error: Error message if operation failed
         
        """
        try:
            resp = init_tool_response()
            session_manager.clear_gen_code_cache()
            session_manager.gen_code_id = str(uuid.uuid4())
            logger.info(f"[GEN CODE START]:{session_manager.gen_code_id}")
        
            if step_file and step_file.endswith('.py'):
                session_manager.steps_dir = parse_steps_dir_from_step_path(step_file)
                session_manager.step_file_target = step_file
            elif feature_file:
                session_manager.steps_dir, session_manager.step_file_target = gen_step_file_from_feature_path(feature_file)
            else:
                session_manager.steps_dir = STEPS_DIR_DEFAULT
                session_manager.step_file_target = TARGET_STEP_FILE_DEFAULT

            resp["status"] = "success"
            resp["data"] = {
                "gen_code_id": session_manager.gen_code_id,
                "steps_dir": session_manager.steps_dir,
                "step_file_target": session_manager.step_file_target,
                # "gen_code_cache": session_manager.gen_code_cache,
            }
        except Exception as e:
            resp["error"] = f"Error during code generation: {repr(e)}"
            logger.error(f"Error during code generation: {repr(e)}")
            raise e

        return json.dumps(format_tool_response(resp))
    
    @mcp.tool()
    @log_tool_call
    async def preview_code_changes() -> str:
        """Preview generated test code changes and confirm before applying"""
        resp = init_tool_response()
        
        if not session_manager.gen_code_id or not session_manager.gen_code_cache:
            resp["status"] = "success"
            resp["data"] = {"message": "No pending code changes to preview"}
            return json.dumps(format_tool_response(resp))
        
        result = gen_code_preview(session_manager)
        resp["status"] = "success"
        resp["data"] = {"diff_preview": result.get('diff_preview')}
        
        return json.dumps(format_tool_response(resp))

    @mcp.tool()
    @log_tool_call
    async def confirm_code_changes() -> str:
        """Confirm the previewed code changes"""
        resp = init_tool_response()
        
        if not hasattr(session_manager, 'proposed_changes') or not session_manager.proposed_changes:
            resp["status"] = "success"
            resp["data"] = {"message": "No pending code changes to confirm"}
            return json.dumps(format_tool_response(resp))
        
        if not ensure_step_path_exists(session_manager.step_file_target):
            resp["status"] = "error"
            resp["error"] = f"Failed to create directory structure for {session_manager.step_file_target}"
            return json.dumps(format_tool_response(resp))
        
        try:
            from utils.gen_code import extract_step_patterns, check_step_pattern_exists
            from utils.gen_code import extract_steps_from_cache
            
            # 重新扫描现有步骤模式，确保最新状态
            step_file = session_manager.steps_dir
            existing_patterns = extract_step_patterns(step_file)
            
            # 从缓存中提取步骤并检查冲突
            steps = extract_steps_from_cache(session_manager.gen_code_id, session_manager.gen_code_cache)
            
            # 检查是否有步骤会冲突
            conflict_steps = []
            for item in steps:
                step_text = item.get('step_text', '')
                step_type = item.get('step_type', '')
                if check_step_pattern_exists(step_type, step_text, existing_patterns):
                    conflict_steps.append(f"{step_type}('{step_text}')")
            
            if conflict_steps:
                logger.warning(f"Potential conflicts detected: {conflict_steps}")
            
            # 读取现有文件内容
            existing_content = ""
            step_file_path = Path(session_manager.step_file_target)
            if step_file_path.exists():
                existing_content = step_file_path.read_text(encoding='utf-8')
            
            # 使用精确的步骤代码去重
            new_steps_to_write = []
            for item in session_manager.proposed_changes:
                if not item.strip():
                    continue
                    
                # 提取步骤装饰器模式进行精确匹配
                import re
                step_patterns = re.findall(r'@(given|when|then|step)\s*\(\s*["\'](.+?)["\']\s*\)', item)
                
                is_duplicate = False
                for pattern_type, pattern_text in step_patterns:
                    if check_step_pattern_exists(pattern_type, pattern_text, existing_patterns):
                        is_duplicate = True
                        logger.info(f"Skipping duplicate step: {pattern_type}('{pattern_text}')")
                        break
                
                if not is_duplicate:
                    new_steps_to_write.append(item)
            
            # 写入文件
            with open(session_manager.step_file_target, 'w', encoding='utf-8') as f:
                f.write(existing_content)
                if hasattr(session_manager, 'header_code') and session_manager.header_code:
                    if not existing_content:
                        f.write(session_manager.header_code + "\n")
                for item in new_steps_to_write:
                    f.write(item + "\n")
            
            result = f"Applied {len(new_steps_to_write)} new steps to {session_manager.step_file_target}"
            if conflict_steps:
                result += f" ({len(conflict_steps)} conflicts skipped)"
            
            session_manager.new_steps_count = len(new_steps_to_write)
            resp["status"] = "success"
            resp["data"] = {"message": result, "new_steps_count": session_manager.new_steps_count}
        except Exception as e:
            result = f"Error applying changes to {session_manager.step_file_target}: {str(e)}"
            logger.error(result)
            resp["status"] = "error"
            resp["error"] = result
        
        # Clear the proposed changes
        session_manager.clear_gen_code_cache()
        return json.dumps(format_tool_response(resp))


