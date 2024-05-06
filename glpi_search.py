import os
from dotenv import load_dotenv
import glpi_api
from keyboards import research_or_connect_keyboard  # Добавить этот импорт

load_dotenv()

GLPI_API_URL = os.getenv('GLPI_API_URL')
GLPI_APPTOKEN = os.getenv('GLPI_APPTOKEN')
GLPI_USERTOKEN = os.getenv('GLPI_USERTOKEN')
GLPI_FAQ_URL = os.getenv('GLPI_FAQ_URL')

async def perform_search(search_term):
    try:
        with glpi_api.connect(GLPI_API_URL, GLPI_APPTOKEN, GLPI_USERTOKEN) as glpi:
            results = search_knowbaseitem(glpi, search_term)
            if results:
                links = [f"{GLPI_FAQ_URL}?id={result['2']}" for result in results]
                response_message = "\n".join(links)
            else:
                response_message = "Ничего не найдено."
    except Exception as e:
        response_message = f"Произошла ошибка при выполнении запроса: {str(e)}"
    finally:
        if hasattr(glpi, 'close'):
            glpi.close()
    return response_message, research_or_connect_keyboard()

def search_knowbaseitem(glpi, search_term):
    criteria = [
        {'field': 'name', 'searchtype': 'contains', 'value': search_term},
        {'link': 'AND', 'field': 'is_faq', 'searchtype': 'equals', 'value': '1'}
    ]
    forcedisplay = [2, 6]
    return glpi.search('KnowbaseItem', criteria=criteria, forcedisplay=forcedisplay)
