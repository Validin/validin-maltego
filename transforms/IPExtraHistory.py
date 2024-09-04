import requests
from maltego_trx.entities import IPAddress, NS
from maltego_trx.maltego import UIM_TYPES, MaltegoMsg, MaltegoTransform
from maltego_trx.transform import DiscoverableTransform
from settings import VALIDIN_ENDPOINT, VALIDIN_API_KEY


#@registry.register_transform(display_name="Domain DNS Infrastructure", input_entity="maltego.IPv4Address",
#                             description='Receive DNS name from the Client, and resolve all historic A, AAAA, and NS records.',
#                             output_entities=["maltego.IPv4Address", "maltego.IPv6Address", "maltego.NSRecord"])
class IPExtraHistory(DiscoverableTransform):

  @classmethod
  def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
    ip_addr = request.Value
    endpoint = VALIDIN_ENDPOINT
    api_key = "Bearer " + VALIDIN_API_KEY
    headers = {'Authorization': api_key}
    path = "/api/axon/ip/dns/extra/"
    url = f"https://{endpoint}{path}{ip_addr}"

    try:
      # Make a GET request to the API endpoint
      res = requests.get(url, headers=headers)
      res.raise_for_status()  # Raises an HTTPError for bad responses

      # The response is in JSON format and has a structure like:
      # res.json() => {'records': {'A': [...], 'AAAA': [...], 'NS': [...]}}

      data = res.json()
      records = data.get('records', {})

      for record_type, record_list in records.items():
        for record in record_list:
          value = record.get('value')
          first_seen = record.get('first_seen')
          last_seen = record.get('last_seen')

          entity = response.addEntity("maltego.DNSName", value)

          entity.addProperty("first_seen", "First Seen", "strict", first_seen)
          entity.addProperty("last_seen", "Last Seen", "strict", last_seen)
          entity.addProperty("record_type", "Record Type", "strict", record_type)

    except requests.exceptions.HTTPError as http_err:
        response.addUIMessage(f"HTTP error occurred: {http_err}")
    except Exception as err:
        response.addUIMessage(f"An error occurred: {err}")

    return response
