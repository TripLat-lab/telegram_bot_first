import re
from aiogram.fsm.state import StatesGroup, State

def validate_and_normalize_number(number: str) -> tuple[bool, str]:
    pattern_plus7 = r'^\+7\d{10}$'
    pattern_8 = r'^8\d{10}$'
    pattern_7 = r'^7\d{10}$'
    if re.fullmatch(pattern_plus7, number):
        return True, number
    elif re.fullmatch(pattern_8, number):
        normalized_number = '+7' + number[1:]
        return True, normalized_number
    elif re.fullmatch(pattern_7, number):
        normalized_number = '+' + number
        return True, normalized_number
    else:
        return False, ""
    
class users(StatesGroup):
    number = State()
    CHECK = State()

class admin(StatesGroup):
    reg_pin = State()
    reg_id = State()
    password = State()
    reg_password = State()
    CHECK = State()

class registered_department(StatesGroup):
    department = State()
    get_organization = State()
    organization = State()

class registered_user(StatesGroup):
    number = State()
    number_user = State()
    organization_id = State()
    department_id = State()
    name = State()

class upload_link_files_sample(StatesGroup):
    type = State()
    select_org_sample = State()
    name_document = State()
    upload_link = State()
    CHECK = State()
    get_type = State()
    get_link = State()
    link = State()

class upload_link_files_dms(StatesGroup):
    type = State()
    select_org_sample = State()
    name_document = State()
    upload_link = State()
    CHECK = State()
    get_type = State()
    get_link = State()

class add_boss(StatesGroup):
    organization = State()
    department = State()
    mentor = State()
    user = State()
    url = State()

class add_pdf(StatesGroup):
    upload_pdf = State()
    add_pdff = State()

class add_photo(StatesGroup):
    add_photo = State()


class type_videos(StatesGroup):
    upload_link_videos = State()
    type_video = State()
    department_name = State()
    name = State()
