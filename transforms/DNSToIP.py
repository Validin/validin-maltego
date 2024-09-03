from maltego_trx.entities import IPv4Address, IPv6Address
from maltego_trx.maltego import UIM_TYPES, MaltegoMsg, MaltegoTransform
from maltego_trx.transform import DiscoverableTransform


@registry.register_transform(display_name="Domain DNS Infrastructure", input_entity="maltego.DNSName",
                             description='Receive DNS name from the Client, and resolve all historic A, AAAA, and NS records.',
                             output_entities=["maltego.IPv4Address", "maltego.IPv6Address", "maltego.DNSName"])
class DomainDNSHistory(DiscoverableTransform):

  @classmethod
  def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
    domain_name = request.Value
    endpoint = request.TransformSettings.get("ValidinEndpoint", "app.validin.com")
    api_key = "Bearer " + request.TransformSettings.get("ValidinApiKey", "")
    headers = {'Authorization': api_key}
    path = "/api/axon/domain/dns/history/"
    url = f"https://{endpoint}{path}{domain_name}"

    try:
      # Make a GET request to the API endpoint
      res = requests.get(url, headers=headers)
      res.raise_for_status()  # Raises an HTTPError for bad responses

      # Assuming the response is in JSON format and has a structure like:
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
          if record_type == 'A':
            entity = response.addEntity(IPv4Address, value)
          elif record_type == 'AAAA':
            entity = response.addEntity(IPv6Address, value)
          elif record_type == 'NS':
            entity = response.addEntity(DNSName, value)
          else:
            continue  # Skip unknown record types

          # Add properties to the entity if desired
          entity.addProperty("first_seen", "First Seen", "strict", first_seen)
          entity.addProperty("last_seen", "Last Seen", "strict", last_seen)
          entity.addProperty("record_type", "Record Type", "strict", record_type)

    except requests.exceptions.HTTPError as http_err:
        response.addUIMessage(f"HTTP error occurred: {http_err}", UIM_TYPES["partialError"])
    except Exception as err:
        response.addUIMessage(f"An error occurred: {err}", UIM_TYPES["fatalError"])

    return response
