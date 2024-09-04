import requests
from maltego_trx.entities import IPAddress, NS
from maltego_trx.maltego import UIM_TYPES, MaltegoMsg, MaltegoTransform
from maltego_trx.transform import DiscoverableTransform
from settings import VALIDIN_ENDPOINT, VALIDIN_API_KEY


#@registry.register_transform(display_name="Domain DNS Infrastructure", input_entity="maltego.DNSName",
#                             description='Receive DNS name from the Client, and resolve all historic A, AAAA, and NS records.',
#                             output_entities=["maltego.IPv4Address", "maltego.IPv6Address", "maltego.NSRecord"])
class DomainHostPivotsHistory(DiscoverableTransform):

  @classmethod
  def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
    domain_name = request.Value
    endpoint = VALIDIN_ENDPOINT
    api_key = "Bearer " + VALIDIN_API_KEY
    headers = {'Authorization': api_key}
    path = "/api/axon/domain/pivots/"
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
        value_cat = record_type.split('-', 1)[1]
        for record in record_list:
          value = record.get('value')
          value_type = record.get('value_type')
          first_seen = record.get('first_seen')
          last_seen = record.get('last_seen')

          # Determine entity type based on DNS record type
          if value_cat == 'HOST':
            entity = response.addEntity("maltego.DNSName", value)
          elif value_cat == 'IP':
            if value_type.lower() == 'ip4':
              entity = response.addEntity("maltego.IPv4Address", value)
            else:
              entity = response.addEntity("maltego.IPv6Address", value)
          elif value_cat == 'LOCATION':
            entity = response.addEntity("maltego.Url", value)
          elif 'DOMAIN' in value_cat:
            entity = response.addEntity("maltego.DNSName", value)
          elif value_cat.startswith('CERT_FINGERPRINT'):
            entity = response.addEntity("maltego.SSLCertificateHash", value)
          elif value_cat.endswith('HASH'):
            entity = response.addEntity("maltego.Hash", value)
          elif value_cat == 'JARM':
            entity = response.addEntity("maltego.JARMFingerprint", value)
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
