
import requests
from maltego_trx.entities import IPAddress, NS
from maltego_trx.maltego import UIM_TYPES, MaltegoMsg, MaltegoTransform
from maltego_trx.transform import DiscoverableTransform
from settings import VALIDIN_ENDPOINT, VALIDIN_API_KEY


#@registry.register_transform(display_name="Domain DNS Infrastructure", input_entity=["maltego.DNSName", "maltego.MXRecord", "maltego.NSRecord"],
#                             description='Receive DNS name from the Client, and resolve all historic A, AAAA, and NS records.',
#                             output_entities=["maltego.IPv4Address", "maltego.IPv6Address", "maltego.NSRecord"])
class DomainExtraHistory(DiscoverableTransform):

  @classmethod
  def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
    domain_name = request.Value
    endpoint = VALIDIN_ENDPOINT
    api_key = "Bearer " + VALIDIN_API_KEY
    headers = {'Authorization': api_key}
    path = "/api/axon/domain/dns/extra/"
    url = f"https://{endpoint}{path}{domain_name}"

    try:
      # Make a GET request to the API endpoint
      res = requests.get(url, headers=headers)
      res.raise_for_status()  # Raises an HTTPError for bad responses

      # The response is in JSON format and has a structure like:
      # res.json() => {'records': {'A': [...], 'AAAA': [...], 'NS': [...]}}

      data = res.json()
      records = data.get('records', {})

      # Iterate through the record types (A, AAAA, NS)
      for record_type, record_list in records.items():
        for record in record_list:
          value = record.get('value')
          first_seen = record.get('first_seen')
          last_seen = record.get('last_seen')

          # Determine entity type based on DNS record type
          if record_type == 'SOA_SERIAL':
            continue
          if record_type == 'MX':
            entity = response.addEntity("maltego.MXRecord", value)
          elif record_type.startswith('SOA'):
            entity = response.addEntity("maltego.DNSName", value)
          elif record_type.endswith('_FOR'):
            entity = response.addEntity("maltego.DNSName", value)
          else:
            entity = response.addEntity("maltego.Phrase", value)
          # Add properties to the entity if desired
          entity.addProperty("first_seen", "First Seen", "strict", first_seen)
          entity.addProperty("last_seen", "Last Seen", "strict", last_seen)
          entity.addProperty("record_type", "Record Type", "strict", record_type)

    except requests.exceptions.HTTPError as http_err:
        response.addUIMessage(f"HTTP error occurred: {http_err}")
    except Exception as err:
        response.addUIMessage(f"An error occurred: {err}")

    return response
