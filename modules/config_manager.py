"""
Config Manager Module for Auto Job Applier LinkedIn
Provides safe reading and writing of configuration parameters in config/*.py
"""

import os
import re

SEARCH_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "search.py")
SETTINGS_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "settings.py")
QUESTIONS_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "questions.py")

def _update_var_in_file(file_path: str, var_name: str, new_value_repr: str) -> bool:
    """Updates a single variable definition in a python configuration file while preserving all comments."""
    if not os.path.exists(file_path):
        return False
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Match variable assignment at the start of a line (allowing whitespace)
        pattern = rf"^(\s*{re.escape(var_name)}\s*=\s*)(.*?)(?=#.*|\n|$)"
        replacement = f"\\1{new_value_repr}"

        if re.search(pattern, content, flags=re.MULTILINE):
            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE, count=1)
        else:
            # Append if not found
            new_content = content + f"\n{var_name} = {new_value_repr}\n"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"Error updating {var_name} in {file_path}: {e}")
        return False

def load_all_settings() -> dict:
    """Loads all editable settings from python config files."""
    settings = {
        # Search Preferences
        "search_terms": ["Data Analyst", "Software Engineer"],
        "search_location": "San Francisco",
        "date_posted": "Past week",
        "sort_by": "",
        "easy_apply_only": True,
        "experience_level": [],
        "job_type": ["Full-time"],
        "on_site": ["On-site", "Remote", "Hybrid"],
        "current_experience": 7,
        # Salary & Questions
        "desired_salary": 120000,
        "current_ctc": 110000,
        "notice_period": 14,
        # Settings
        "click_gap": 1,
        "chrome_profile": "Default"
    }

    try:
        from config.search import (
            search_terms, search_location, date_posted, sort_by,
            easy_apply_only, experience_level, job_type, on_site, current_experience
        )
        settings["search_terms"] = search_terms
        settings["search_location"] = search_location
        settings["date_posted"] = date_posted
        settings["sort_by"] = sort_by
        settings["easy_apply_only"] = easy_apply_only
        settings["experience_level"] = experience_level
        settings["job_type"] = job_type
        settings["on_site"] = on_site
        settings["current_experience"] = current_experience
    except Exception as e:
        print("Error loading search settings:", e)

    try:
        from config.questions import desired_salary, current_ctc, notice_period
        settings["desired_salary"] = desired_salary
        settings["current_ctc"] = current_ctc
        settings["notice_period"] = notice_period
    except Exception as e:
        print("Error loading questions settings:", e)

    try:
        from config.settings import click_gap, chrome_profile
        settings["click_gap"] = click_gap
        settings["chrome_profile"] = chrome_profile
    except Exception as e:
        print("Error loading settings:", e)

    return settings

def save_all_settings(data: dict) -> bool:
    """Saves updated settings back to config/search.py, config/questions.py, and config/settings.py."""
    success = True

    # Search config updates
    if "search_terms" in data:
        success &= _update_var_in_file(SEARCH_CONFIG_PATH, "search_terms", repr(data["search_terms"]))
    if "search_location" in data:
        success &= _update_var_in_file(SEARCH_CONFIG_PATH, "search_location", repr(str(data["search_location"])))
    if "date_posted" in data:
        success &= _update_var_in_file(SEARCH_CONFIG_PATH, "date_posted", repr(str(data["date_posted"])))
    if "sort_by" in data:
        success &= _update_var_in_file(SEARCH_CONFIG_PATH, "sort_by", repr(str(data["sort_by"])))
    if "easy_apply_only" in data:
        success &= _update_var_in_file(SEARCH_CONFIG_PATH, "easy_apply_only", str(bool(data["easy_apply_only"])))
    if "experience_level" in data:
        success &= _update_var_in_file(SEARCH_CONFIG_PATH, "experience_level", repr(data["experience_level"]))
    if "job_type" in data:
        success &= _update_var_in_file(SEARCH_CONFIG_PATH, "job_type", repr(data["job_type"]))
    if "on_site" in data:
        success &= _update_var_in_file(SEARCH_CONFIG_PATH, "on_site", repr(data["on_site"]))
    if "current_experience" in data:
        success &= _update_var_in_file(SEARCH_CONFIG_PATH, "current_experience", str(int(data["current_experience"])))

    # Questions config updates
    if "desired_salary" in data:
        success &= _update_var_in_file(QUESTIONS_CONFIG_PATH, "desired_salary", str(int(data["desired_salary"])))
    if "current_ctc" in data:
        success &= _update_var_in_file(QUESTIONS_CONFIG_PATH, "current_ctc", str(int(data["current_ctc"])))
    if "notice_period" in data:
        success &= _update_var_in_file(QUESTIONS_CONFIG_PATH, "notice_period", str(int(data["notice_period"])))

    # Settings config updates
    if "click_gap" in data:
        success &= _update_var_in_file(SETTINGS_CONFIG_PATH, "click_gap", str(int(data["click_gap"])))
    if "chrome_profile" in data:
        success &= _update_var_in_file(SETTINGS_CONFIG_PATH, "chrome_profile", repr(str(data["chrome_profile"])))

    return success
