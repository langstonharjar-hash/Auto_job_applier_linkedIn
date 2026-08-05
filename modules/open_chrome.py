'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

Support me: https://github.com/sponsors/GodsScion

version:    26.01.20.5.08
'''

import sys
from modules.helpers import get_default_temp_profile, make_directories
from config.settings import run_in_background, stealth_mode, disable_extensions, safe_mode, chrome_profile, file_name, failed_file_name, logs_folder_path, generated_resume_path
from config.questions import default_resume_path
if stealth_mode:
    import undetected_chromedriver as uc
else: 
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    # from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from modules.helpers import find_default_profile_directory, critical_error_log, print_lg
from selenium.common.exceptions import SessionNotCreatedException

def createChromeSession(isRetry: bool = False):
    make_directories([file_name,failed_file_name,logs_folder_path+"/screenshots",default_resume_path,generated_resume_path+"/temp"])
    # Set up WebDriver with Chrome Profile
    options = uc.ChromeOptions() if stealth_mode else Options()
    if run_in_background:   options.add_argument("--headless")
    if disable_extensions:  options.add_argument("--disable-extensions")

    profile_dir = find_default_profile_directory()
    if isRetry:
        print_lg("Will login with a guest profile, browsing history will not be saved in the browser!")
    elif profile_dir and not safe_mode:
        options.add_argument(f"--user-data-dir={profile_dir}")
        options.add_argument(f"--profile-directory={chrome_profile}")
    else:
        print_lg("Logging in with a guest profile, Web history will not be saved!")
        options.add_argument(f"--user-data-dir={get_default_temp_profile()}")
    if stealth_mode:
        print_lg("Downloading Chrome Driver... This may take some time. Undetected mode requires download every run!")
        driver = uc.Chrome(options=options)
    else: 
        if sys.platform.startswith('win'):
            import subprocess
            from selenium.webdriver.chrome.service import Service
            service = Service()
            service.creation_flags = subprocess.CREATE_NO_WINDOW
            driver = webdriver.Chrome(options=options, service=service)
        else:
            driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    try:
        main_handle = driver.current_window_handle
        handles = driver.window_handles
        if len(handles) > 1:
            print_lg(f"Closing {len(handles) - 1} extra startup tab(s)...")
            for handle in handles:
                if handle != main_handle:
                    driver.switch_to.window(handle)
                    driver.close()
            driver.switch_to.window(main_handle)
    except Exception as e:
        print_lg(f"Notice: Could not close extra tabs automatically ({e})")

    wait = WebDriverWait(driver, 5)
    actions = ActionChains(driver)
    return options, driver, actions, wait

options, driver, actions, wait = None, None, None, None

def init_chrome(isRetry: bool = False):
    global options, driver, actions, wait
    if driver is not None:
        return options, driver, actions, wait
    try:
        options, driver, actions, wait = createChromeSession(isRetry)
    except SessionNotCreatedException as e:
        critical_error_log("Failed to create Chrome Session, retrying with guest profile", e)
        options, driver, actions, wait = createChromeSession(True)
    except Exception as e:
        msg = 'Error starting Google Chrome session. Make sure Chrome is updated or try Safe Mode.'
        if isinstance(e,TimeoutError): msg = "Couldn't download Chrome-driver. Set stealth_mode = False in config!"
        print_lg(msg)
        critical_error_log("In Opening Chrome", e)
        try:
            if driver: driver.quit()
        except NameError: pass
        raise Exception(msg) from e
    return options, driver, actions, wait
    
