import os
from typing import Optional

import serpapi
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.tools import tool


class FlightsInput(BaseModel):
    departure_airport: Optional[str] = Field(description='Departure airport code (IATA)')
    arrival_airport: Optional[str] = Field(description='Arrival airport code (IATA)')
    outbound_date: Optional[str] = Field(description='Parameter defines the outbound date. The format is YYYY-MM-DD. e.g. 2024-06-22')
    return_date: Optional[str] = Field(description='Parameter defines the return date. The format is YYYY-MM-DD. e.g. 2024-06-28')
    adults: Optional[int] = Field(1, description='Parameter defines the number of adults. Default to 1.')
    children: Optional[int] = Field(0, description='Parameter defines the number of children. Default to 0.')
    infants_in_seat: Optional[int] = Field(0, description='Parameter defines the number of infants in seat. Default to 0.')
    infants_on_lap: Optional[int] = Field(0, description='Parameter defines the number of infants on lap. Default to 0.')


@tool(args_schema=FlightsInput)
def flights_finder(departure_airport: Optional[str] = None, arrival_airport: Optional[str] = None,
                   outbound_date: Optional[str] = None, return_date: Optional[str] = None,
                   adults: Optional[int] = 1, children: Optional[int] = 0,
                   infants_in_seat: Optional[int] = 0, infants_on_lap: Optional[int] = 0):
    '''Find flights using the Google Flights engine.'''
    params = {
        'api_key': os.environ.get('SERPAPI_API_KEY'),
        'engine': 'google_flights',
        'hl': 'en',
        'gl': 'us',
        'departure_id': departure_airport,
        'arrival_id': arrival_airport,
        'outbound_date': outbound_date,
        'return_date': return_date,
        'currency': 'USD',
        'adults': adults,
        'infants_in_seat': infants_in_seat,
        'stops': '1',
        'infants_on_lap': infants_on_lap,
        'children': children,
    }
    try:
        search = serpapi.search(params)
        return search.data['best_flights']
    except Exception as e:
        return str(e)
