= INSTALL ==
virtualenv env
source env/bin/activate
pip3 install -r requirements.txt

== mouser ==
client-id: 7e3d279a-5250-4ace-819c-bf0defb9102d

curl -X POST "https://api.mouser.com/api/v1/search/partnumber?apiKey=7e3d279a-5250-4ace-819c-bf0defb9102d" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"SearchByPartRequest\": { \"mouserPartNumber\": \"09160423101\", \"partSearchOptions\": \"09160423101\" }}"

== digikey ==
client-id: AcXVTuiOdh9bMO6b2IjY7pcVX81LmK4b
client-secret: wM460Hn7IueX7JUr

== modify_test ==
python3 modify_test.py 'Operating temperature: -15...70C'

== openai ==
# usage
python3 embed.py mpn/tme/1555-RD001.txt

# open-ai secret key
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

# send embedding request
curl https://api.openai.com/v1/embeddings \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "The food was delicious and the waiter...",
    "model": "text-embedding-ada-002"
  }'
