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

        if re.search(pattern, content, flags=re.MULTILINE):
            new_content = re.sub(pattern, lambda m: f"{m.group(1)}{new_value_repr}  ", content, flags=re.MULTILINE, count=1)
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
        "search_terms": ["Data Analyst"],
        "search_location": "San Francisco",
        "date_posted": "Past week",
        "sort_by": "",
        "salary": "",
        "easy_apply_only": True,
        "experience_level": [],
        "job_type": ["Full-time"],
        "on_site": ["On-site", "Remote", "Hybrid"],
        "current_experience": 7,
        "bad_words": [],
        "about_company_bad_words": [],
        # Salary & Questions
        "years_of_experience": "7",
        "require_visa": "No",
        "us_citizenship": "U.S. Citizen/Permanent Resident",
        "website": "",
        "linkedIn": "",
        "default_resume_path": "Langston_Harris_Jara_Resume.pdf",
        "desired_salary": 125000,
        "current_ctc": 110000,
        "notice_period": 14,
        # Settings
        "click_gap": 1,
        "chrome_profile": "Default",
        "close_tabs": False,
        "follow_companies": False
    }

    try:
        from config.search import (
            search_terms, search_location, date_posted, sort_by, salary,
            easy_apply_only, experience_level, job_type, on_site, current_experience,
            bad_words, about_company_bad_words
        )
        settings["search_terms"] = search_terms
        settings["search_location"] = search_location
        settings["date_posted"] = date_posted
        settings["sort_by"] = sort_by
        settings["salary"] = salary
        settings["easy_apply_only"] = easy_apply_only
        settings["experience_level"] = experience_level
        settings["job_type"] = job_type
        settings["on_site"] = on_site
        settings["current_experience"] = current_experience
        settings["bad_words"] = bad_words
        settings["about_company_bad_words"] = about_company_bad_words
    except Exception as e:
        print("Error loading search settings:", e)

    try:
        from config.questions import (
            years_of_experience, require_visa, us_citizenship, website, linkedIn,
            default_resume_path, desired_salary, current_ctc, notice_period
        )
        settings["years_of_experience"] = str(years_of_experience)
        settings["require_visa"] = str(require_visa)
        settings["us_citizenship"] = str(us_citizenship)
        settings["website"] = str(website)
        settings["linkedIn"] = str(linkedIn)
        settings["default_resume_path"] = str(default_resume_path)
        settings["desired_salary"] = desired_salary
        settings["current_ctc"] = current_ctc
        settings["notice_period"] = notice_period
    except Exception as e:
        print("Error loading questions settings:", e)

    try:
        from config.settings import click_gap, chrome_profile, close_tabs, follow_companies
        settings["click_gap"] = click_gap
        settings["chrome_profile"] = chrome_profile
        settings["close_tabs"] = close_tabs
        settings["follow_companies"] = follow_companies
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
    if "salary" in data:
        success &= _update_var_in_file(SEARCH_CONFIG_PATH, "salary", repr(str(data["salary"])))
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
    if "bad_words" in data:
        success &= _update_var_in_file(SEARCH_CONFIG_PATH, "bad_words", repr(data["bad_words"]))
    if "about_company_bad_words" in data:
        success &= _update_var_in_file(SEARCH_CONFIG_PATH, "about_company_bad_words", repr(data["about_company_bad_words"]))

    # Questions config updates
    if "years_of_experience" in data:
        success &= _update_var_in_file(QUESTIONS_CONFIG_PATH, "years_of_experience", repr(str(data["years_of_experience"])))
    if "require_visa" in data:
        success &= _update_var_in_file(QUESTIONS_CONFIG_PATH, "require_visa", repr(str(data["require_visa"])))
    if "us_citizenship" in data:
        success &= _update_var_in_file(QUESTIONS_CONFIG_PATH, "us_citizenship", repr(str(data["us_citizenship"])))
    if "website" in data:
        success &= _update_var_in_file(QUESTIONS_CONFIG_PATH, "website", repr(str(data["website"])))
    if "linkedIn" in data:
        success &= _update_var_in_file(QUESTIONS_CONFIG_PATH, "linkedIn", repr(str(data["linkedIn"])))
    if "default_resume_path" in data:
        success &= _update_var_in_file(QUESTIONS_CONFIG_PATH, "default_resume_path", repr(str(data["default_resume_path"])))
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
    if "close_tabs" in data:
        success &= _update_var_in_file(SETTINGS_CONFIG_PATH, "close_tabs", str(bool(data["close_tabs"])))
    if "follow_companies" in data:
        success &= _update_var_in_file(SETTINGS_CONFIG_PATH, "follow_companies", str(bool(data["follow_companies"])))

    return success
