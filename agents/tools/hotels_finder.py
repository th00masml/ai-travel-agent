import os
from typing import Optional

import serpapi
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.tools import tool


class HotelsInput(BaseModel):
    q: str = Field(description='Location of the hotel')
    check_in_date: str = Field(description='Check-in date. The format is YYYY-MM-DD. e.g. 2024-06-22')
    check_out_date: str = Field(description='Check-out date. The format is YYYY-MM-DD. e.g. 2024-06-28')
    sort_by: Optional[str] = Field(8, description='Parameter is used for sorting the results. Default is sort by highest rating')
    adults: Optional[int] = Field(1, description='Number of adults. Default to 1.')
    children: Optional[int] = Field(0, description='Number of children. Default to 0.')
    rooms: Optional[int] = Field(1, description='Number of rooms. Default to 1.')
    hotel_class: Optional[str] = Field(None, description='Parameter defines to include only certain hotel class in the results. for example- 2,3,4')


@tool(args_schema=HotelsInput)
def hotels_finder(q: str, check_in_date: str, check_out_date: str, sort_by: Optional[str] = None,
                  adults: Optional[int] = 1, children: Optional[int] = 0,
                  rooms: Optional[int] = 1, hotel_class: Optional[str] = None):
    '''Find hotels using the Google Hotels engine.'''
    params = {
        'api_key': os.environ.get('SERPAPI_API_KEY'),
        'engine': 'google_hotels',
        'hl': 'en',
        'gl': 'us',
        'q': q,
        'check_in_date': check_in_date,
        'check_out_date': check_out_date,
        'currency': 'USD',
        'adults': adults,
        'children': children,
        'rooms': rooms,
        'sort_by': sort_by,
        'hotel_class': hotel_class,
    }
    try:
        search = serpapi.search(params)
        return search.data['properties'][:5]
    except Exception as e:
        return str(e)
